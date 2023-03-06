from collections import ChainMap
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    MutableMapping,
    Type,
    TypeVar,
    Union,
)

from docarray.array.stacked.list_advance_indexing import ListAdvanceIndex
from docarray.base_document import BaseDocument
from docarray.typing import NdArray
from docarray.typing.tensor.abstract_tensor import AbstractTensor

if TYPE_CHECKING:
    from docarray.array.stacked.array_stacked import DocumentArrayStacked

IndexIterType = Union[slice, Iterable[int], Iterable[bool], None]


T = TypeVar('T', bound='ColumnStorage')


class ColumnStorage:
    """
    ColumnStorage is a container to store the columns of the
    :class:`~docarray.array.stacked.DocumentArrayStacked`.

    :param tensor_columns: a Dict of AbstractTensor
    :param doc_columns: a Dict of :class:`~docarray.array.stacked.DocumentArrayStacked`
    :param da_columns: a Dict of List of :class:`~docarray.array.stacked.DocumentArrayStacked`
    :param any_columns: a Dict of List
    :param document_type: document_type
    :param tensor_type: Class used to wrap the stacked tensors
    """

    document_type: Type[BaseDocument]

    tensor_columns: Dict[str, AbstractTensor]
    doc_columns: Dict[str, 'DocumentArrayStacked']
    da_columns: Dict[str, ListAdvanceIndex['DocumentArrayStacked']]
    any_columns: Dict[str, ListAdvanceIndex]

    def __init__(
        self,
        tensor_columns: Dict[str, AbstractTensor],
        doc_columns: Dict[str, 'DocumentArrayStacked'],
        da_columns: Dict[str, ListAdvanceIndex['DocumentArrayStacked']],
        any_columns: Dict[str, ListAdvanceIndex],
        document_type: Type[BaseDocument],
        tensor_type: Type[AbstractTensor] = NdArray,
    ):
        self.tensor_columns = tensor_columns
        self.doc_columns = doc_columns
        self.da_columns = da_columns
        self.any_columns = any_columns

        self.document_type = document_type
        self.tensor_type = tensor_type

        self.columns = ChainMap(
            self.tensor_columns,
            self.doc_columns,
            self.da_columns,
            self.any_columns,
        )

    def __len__(self) -> int:
        return len(self.any_columns['id'])  # TODO what if ID are None ?

    def __getitem__(self: T, item: IndexIterType) -> T:
        if isinstance(item, tuple):
            item = list(item)
        tensor_columns = {key: col[item] for key, col in self.tensor_columns.items()}
        doc_columns = {key: col[item] for key, col in self.doc_columns.items()}
        da_columns = {key: col[item] for key, col in self.da_columns.items()}
        any_columns = {key: col[item] for key, col in self.any_columns.items()}

        return ColumnStorage(
            tensor_columns,
            doc_columns,
            da_columns,
            any_columns,
            self.document_type,
            self.tensor_type,
        )


class ColumnStorageView(dict, MutableMapping[str, Any]):
    index: int
    storage: ColumnStorage

    def __init__(self, index: int, storage: ColumnStorage):
        super().__init__()
        self.index = index
        self.storage = storage

    def __getitem__(self, name: str) -> Any:
        return self.storage.columns[name][self.index]

    def __setitem__(self, name, value) -> None:
        self.storage.columns[name][self.index] = value

    def __delitem__(self, key):
        raise RuntimeError('Cannot delete an item from a StorageView')

    def __iter__(self):
        return self.storage.columns.keys()

    def __len__(self):
        return len(self.storage.columns)