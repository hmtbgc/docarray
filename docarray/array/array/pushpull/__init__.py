from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Type

from typing_extensions import Protocol

from docarray.array.array.io import BinaryIOLike

__cache_path__ = Path.home() / '.cache' / 'docarray-v2'

if TYPE_CHECKING:  # pragma: no cover
    from docarray import BaseDocument, DocumentArray


class PushPullLike(Protocol):
    @staticmethod
    def list(show_table: bool) -> List[str]:
        ...

    @staticmethod
    def delete(name: str) -> None:
        ...

    @staticmethod
    def push(
        da: BinaryIOLike,
        url: str,
        public: bool = True,
        show_progress: bool = False,
        branding: Optional[Dict] = None,
    ) -> Dict:
        ...

    @staticmethod
    def pull(
        cls: Type['BinaryIOLike'],
        name: str,
        show_progress: bool = False,
        local_cache: bool = True,
    ) -> 'DocumentArray':
        ...


class PushPullMixin(Sequence['BaseDocument'], BinaryIOLike):
    """Transmitting :class:`DocumentArray` via Jina Cloud Service"""

    _max_bytes = 4 * 2**30
    __backends__: Dict[str, PushPullLike] = {}

    @classmethod
    def get_backend(cls, protocol: str) -> PushPullLike:
        """
        Register a new backend for push/pull.

        :param protocol: the protocol to use, e.g. 'jinaai', 'file', 's3'
        :param backend: the backend to use
        """
        if protocol in cls.__backends__:
            return cls.__backends__[protocol]

        if protocol == 'jinaai':
            from docarray.array.array.pushpull.jinaai import PushPullJAC

            cls.__backends__[protocol] = PushPullJAC
        elif protocol == 'file':
            raise NotImplementedError('file protocol not implemented yet')
            # from docarray.array.array.pushpull.file import PushPullFile
        elif protocol == 's3':
            raise NotImplementedError('s3 protocol not implemented yet')
            # from docarray.array.array.pushpull.s3 import PushPullS3
        else:
            raise NotImplementedError(f'protocol {protocol} not supported')

        return cls.__backends__[protocol]

    @staticmethod
    def list(protocol: str, show_table: bool = False) -> List[str]:
        """
        List all the artifacts in the cloud.

        :param protocol: the protocol to use, e.g. 'jinaai', 'file', 's3'
        :param show_table: whether to show the table of artifacts
        :return: a list of artifact names
        """
        return PushPullMixin.get_backend(protocol).list(show_table)

    @classmethod
    def delete(cls, url: str):
        """
        Delete the artifact in the cloud.

        :param url: the url of the artifact to delete
        """
        protocol, name = url.split('://', 2)
        return PushPullMixin.get_backend(protocol).delete(name)

    def push(
        self,
        url: str,
        public: bool = True,
        show_progress: bool = False,
        branding: Optional[Dict] = None,
    ) -> Dict:
        """Push this DocumentArray object to Jina AI Cloud which can be later retrieved via :meth:`.push`

        .. note::
            - Push with the same ``name`` will override the existing content.
            - Kinda like a public clipboard where everyone can override anyone's content.
              So to make your content survive longer, you may want to use longer & more complicated name.
            - The lifetime of the content is not promised atm, could be a day, could be a week. Do not use it for
              persistence. Only use this full temporary transmission/storage/clipboard.

        :param name: A name that can later be used to retrieve this :class:`DocumentArray`.
        :param public: By default, anyone can pull a DocumentArray if they know its name.
            Setting this to false will restrict access to only the creator.
        :param show_progress: If true, a progress bar will be displayed.
        :param branding: A dictionary of branding information to be sent to Jina Cloud. {"icon": "emoji", "background": "#fff"}
        """
        protocol, name = url.split('://', 2)
        return PushPullMixin.get_backend(protocol).push(
            self, name, public, show_progress, branding
        )

    @classmethod
    def pull(
        cls,
        url: str,
        show_progress: bool = False,
        local_cache: bool = True,
    ):
        """Pull a :class:`DocumentArray` from Jina AI Cloud to local.

        :param name: the upload name set during :meth:`.push`
        :param show_progress: if true, display a progress bar.
        :param local_cache: store the downloaded DocumentArray to local folder
        :return: a :class:`DocumentArray` object
        """
        protocol, name = url.split('://', 2)
        return PushPullMixin.get_backend(protocol).pull(
            cls, name, show_progress, local_cache
        )
