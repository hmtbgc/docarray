import uuid
import warnings
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk

import docarray.typing
from docarray import BaseDocument, DocumentArray
from docarray.doc_index.abstract_doc_index import (
    BaseDocumentIndex,
    FindResultBatched,
    _ColumnInfo,
)
from docarray.utils.find import FindResult
from docarray.utils.misc import torch_imported

# mypy: ignore-errors

if TYPE_CHECKING:

    def composable(fn):  # type: ignore
        return fn

else:
    # static type checkers do not like callable objects as decorators
    from docarray.doc_index.abstract_doc_index import composable

TSchema = TypeVar('TSchema', bound=BaseDocument)
T = TypeVar('T', bound='ElasticDocumentIndex')

MAX_ES_RETURNED_DOCS = 10000

ELASTIC_PY_VEC_TYPES = [list, tuple, np.ndarray]
if torch_imported:
    import torch

    ELASTIC_PY_VEC_TYPES.append(torch.Tensor)


class ElasticDocumentIndex(BaseDocumentIndex, Generic[TSchema]):
    def __init__(self, db_config=None, **kwargs):
        super().__init__(db_config=db_config, **kwargs)
        if self._db_config.index_name is None:
            id = uuid.uuid4().hex
            self._db_config.index_name = 'index__' + id

        self._db_config = cast(ElasticDocumentIndex.DBConfig, self._db_config)

        self._client = Elasticsearch(
            hosts=self._db_config.hosts,
            **self._db_config.es_config,
        )

        # ElasticSearh index setup
        self._index_init_params = ('type',)
        self._index_vector_params = ('dims', 'similarity', 'index')
        self._index_vector_options = ('m', 'ef_construction')

        mappings = {'dynamic': 'true', '_source': {'enabled': 'true'}, 'properties': {}}
        for col_name, col in self._column_infos.items():
            if not col.config:
                continue  # do not create column index if no config is given
            mappings['properties'][col_name] = self._create_index(col)

        if self._client.indices.exists(index=self._db_config.index_name):
            self._client.indices.put_mapping(
                index=self._db_config.index_name, properties=mappings['properties']
            )
        else:
            self._client.indices.create(
                index=self._db_config.index_name, mappings=mappings
            )

        self._refresh(self._db_config.index_name)

    ###############################################
    # Inner classes for query builder and configs #
    ###############################################
    class QueryBuilder(BaseDocumentIndex.QueryBuilder):
        def build(self, *args, **kwargs) -> Any:
            return self._queries

    @dataclass
    class DBConfig(BaseDocumentIndex.DBConfig):
        hosts: Union[
            str, List[Union[str, Mapping[str, Union[str, int]]]], None
        ] = 'http://localhost:9200'
        index_name: Optional[str] = None
        es_config: Dict[str, Any] = field(default_factory=dict)

    @dataclass
    class RuntimeConfig(BaseDocumentIndex.RuntimeConfig):
        default_column_config: Dict[Type, Dict[str, Any]] = field(
            default_factory=lambda: {
                np.ndarray: {
                    'type': 'dense_vector',
                    'index': True,
                    'dims': 128,
                    'similarity': 'cosine',  # 'l2_norm', 'dot_product', 'cosine'
                    'm': 16,
                    'ef_construction': 100,
                },
                docarray.typing.ID: {'type': 'keyword'},
                # `None` is not a Type, but we allow it here anyway
                None: {},  # type: ignore
                # TODO: add support for other types
            }
        )

    ###############################################
    # Implementation of abstract methods          #
    ###############################################

    def python_type_to_db_type(self, python_type: Type) -> Any:
        """Map python type to database type."""
        for allowed_type in ELASTIC_PY_VEC_TYPES:
            if issubclass(python_type, allowed_type):
                return np.ndarray

        if python_type == docarray.typing.ID:
            return docarray.typing.ID

        raise ValueError(f'Unsupported column type for {type(self)}: {python_type}')

    def _index(self, column_to_data: Dict[str, Generator[Any, None, None]]):

        data = self._transpose_col_value_dict(column_to_data)
        requests = []

        for row in data:
            request = {
                '_index': self._db_config.index_name,
                '_id': row['id'],
            }
            # TODO change here when more types are supported
            for col_name, col in self._column_infos.items():
                if not col.config:
                    continue
                request[col_name] = row[col_name]
            requests.append(request)

        _, warning_info = self._send_requests(requests)
        for info in warning_info:
            warnings.warn(str(info))

        self._refresh(
            self._db_config.index_name
        )  # TODO add runtime config for efficient refresh

    def num_docs(self) -> int:
        return self._client.count(index=self._db_config.index_name)['count']

    def _del_items(self, doc_ids: Sequence[str]):
        requests = []
        for _id in doc_ids:
            requests.append(
                {'_op_type': 'delete', '_index': self._db_config.index_name, '_id': _id}
            )

        _, warning_info = self._send_requests(requests)

        # raise warning if some ids are not found
        if warning_info:
            ids = [info['delete']['_id'] for info in warning_info]
            warnings.warn(f'No document with id {ids} found')

        self._refresh(self._db_config.index_name)

    def _get_items(self, doc_ids: Sequence[str]) -> Sequence[TSchema]:
        accumulated_docs = []
        accumulated_docs_id_not_found = []

        for pos in range(0, len(doc_ids), MAX_ES_RETURNED_DOCS):

            es_rows = self._client.mget(
                index=self._db_config.index_name,
                ids=doc_ids[pos : pos + MAX_ES_RETURNED_DOCS],
            )['docs']

            for row in es_rows:
                if row['found']:
                    doc_dict = row['_source']
                    accumulated_docs.append(doc_dict)
                else:
                    accumulated_docs_id_not_found.append(row['_id'])

        # raise warning if some ids are not found
        if accumulated_docs_id_not_found:
            warnings.warn(f'No document with id {accumulated_docs_id_not_found} found')

        doc_list = self._convert_to_doc_list(accumulated_docs)
        da_cls = DocumentArray.__class_getitem__(cast(Type[BaseDocument], self._schema))
        return da_cls(doc_list)

    def execute_query(self, query: List[Tuple[str, Dict]], *args, **kwargs) -> Any:
        ...

    @composable
    def _find(
        self, query: np.ndarray, search_field: str, limit: int, **kwargs
    ) -> FindResult:
        knn_query = {
            'field': search_field,
            'query_vector': query,
            'k': limit,
            'num_candidates': 10000
            if 'num_candidates' not in kwargs
            else kwargs['num_candidates'],
        }

        resp = self._client.search(
            index=self._db_config.index_name,
            knn=knn_query,
        )

        docs = []
        scores = []
        for result in resp['hits']['hits']:
            doc_dict = result['_source']
            doc_dict['id'] = result['_id']
            docs.append(doc_dict)
            scores.append(result['_score'])

        doc_list = self._convert_to_doc_list(docs)
        da_cls = DocumentArray.__class_getitem__(cast(Type[BaseDocument], self._schema))
        return FindResult(documents=da_cls(doc_list), scores=np.array(scores))

    def _find_batched(
        self,
        queries: np.ndarray,
        search_field: str,
        limit: int,
    ) -> FindResultBatched:
        result_das = []
        result_scores = []

        for query in queries:
            documents, scores = self._find(query, search_field, limit)
            result_das.append(documents)
            result_scores.append(scores)

        result_scores = np.array(result_scores)
        return FindResultBatched(documents=result_das, scores=result_scores)

    @composable
    def _filter(
        self,
        filter_query: Any,
        limit: int,
    ) -> DocumentArray:
        resp = self._client.search(
            index=self._db_config.index_name,
            query=filter_query,
            size=limit,
        )

        docs = []
        for result in resp['hits']['hits'][:limit]:
            doc_dict = result['_source']
            doc_dict['id'] = result['_id']
            docs.append(doc_dict)

        doc_list = self._convert_to_doc_list(docs)
        da_cls = DocumentArray.__class_getitem__(cast(Type[BaseDocument], self._schema))
        return da_cls(doc_list)

    def _filter_batched(
        self,
        filter_queries: Any,
        limit: int,
    ) -> List[DocumentArray]:
        result_das = []
        for query in filter_queries:
            result_das.append(self._filter(query, limit))
        return result_das

    def _text_search(
        self,
        query: str,
        search_field: str,
        limit: int,
    ) -> FindResult:
        query = {
            "bool": {
                "must": [
                    {"match": {search_field: query}},
                ],
            }
        }

        resp = self._client.search(
            index=self._db_config.index_name,
            query=query,
            size=limit,
        )

        docs = []
        scores = []
        for result in resp['hits']['hits']:
            doc_dict = result['_source']
            doc_dict['id'] = result['_id']
            docs.append(doc_dict)
            scores.append(result['_score'])

        doc_list = self._convert_to_doc_list(docs)
        da_cls = DocumentArray.__class_getitem__(cast(Type[BaseDocument], self._schema))
        return FindResult(documents=da_cls(doc_list), scores=np.array(scores))

    def _text_search_batched(
        self,
        queries: Sequence[str],
        search_field: str,
        limit: int,
    ) -> FindResultBatched:
        result_das = []
        result_scores = []

        for query in queries:
            documents, scores = self._text_search(query, search_field, limit)
            result_das.append(documents)
            result_scores.append(scores)

        result_scores = np.array(result_scores)
        return FindResultBatched(documents=result_das, scores=result_scores)

    ###############################################
    # Helpers                                     #
    ###############################################

    # ElasticSearch helpers
    def _create_index(self, col: '_ColumnInfo') -> Dict[str, Any]:
        """Create a new HNSW index for a column, and initialize it."""
        index = dict((k, col.config[k]) for k in self._index_init_params)
        if col.db_type == np.ndarray:
            for k in self._index_vector_params:
                index[k] = col.config[k]
            if col.n_dim:
                index['dims'] = col.n_dim
            index['index_options'] = dict(
                (k, col.config[k]) for k in self._index_vector_options
            )
            index['index_options']['type'] = 'hnsw'
        return index

    def _convert_to_doc_list(self, docs: List[Dict[str, Any]]) -> List[BaseDocument]:
        """Convert a list of docs to a list of Document objects."""

        doc_list = []
        for doc_dict in docs:
            doc = self._convert_dict_to_doc(doc_dict, self._schema)
            doc_list.append(doc)

        return doc_list

    def _convert_dict_to_doc(
        self, doc_dict: Dict[str, Any], schema: Type[BaseDocument]
    ) -> BaseDocument:
        """Convert a dict to a Document object."""

        for field_name, _ in schema.__fields__.items():
            t_ = schema._get_field_type(field_name)
            if issubclass(t_, BaseDocument):
                inner_dict = {}

                fields = [
                    key for key in doc_dict.keys() if key.startswith(f'{field_name}__')
                ]
                for key in fields:
                    nested_name = key.replace(f'{field_name}__', '')
                    inner_dict[nested_name] = doc_dict.pop(key)

                doc_dict[field_name] = self._convert_dict_to_doc(inner_dict, t_)

        schema_cls = cast(Type[BaseDocument], schema)
        return schema_cls(**doc_dict)

    def _send_requests(self, request: Iterable[Dict[str, Any]], **kwargs) -> List[Dict]:
        """Send bulk request to Elastic and gather the successful info"""

        # TODO chunk_size

        accumulated_info = []
        warning_info = []
        for success, info in parallel_bulk(
            self._client,
            request,
            raise_on_error=False,
            raise_on_exception=False,
            **kwargs,
        ):
            if not success:
                warning_info.append(info)
            else:
                accumulated_info.append(info)

        return accumulated_info, warning_info

    def _refresh(self, index_name: str):
        self._client.indices.refresh(index=index_name)
