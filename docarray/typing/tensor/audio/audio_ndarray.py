from docarray.typing.proto_register import _register_proto
from docarray.typing.tensor.audio.abstract_audio_tensor import AbstractAudioTensor
from docarray.typing.tensor.ndarray import NdArray


@_register_proto(proto_type_name='audio_ndarray')
class AudioNdArray(AbstractAudioTensor, NdArray):
    """
    Subclass of NdArray, to represent an audio tensor.
    Adds audio-specific features to the tensor.


    EXAMPLE USAGE

    .. code-block:: python

        from typing import Optional

        from pydantic import parse_obj_as

        from docarray import Document
        from docarray.typing import AudioNdArray, AudioUrl
        import numpy as np


        class MyAudioDoc(Document):
            title: str
            audio_tensor: Optional[AudioNdArray]
            url: Optional[AudioUrl]
            bytes_: Optional[bytes]


        # from tensor
        doc_1 = MyAudioDoc(
            title='my_first_audio_doc',
            audio_tensor=np.random.rand(1000, 2),
        )

        doc_1.audio_tensor.save_to_wav_file(file_path='path/to/file_1.wav')
        doc_1.bytes_ = doc_1.audio_tensor.to_bytes()

        # from url
        doc_2 = MyAudioDoc(
            title='my_second_audio_doc',
            url='https://www.kozco.com/tech/piano2.wav',
        )

        doc_2.audio_tensor = doc_2.url.load()
        doc_2.audio_tensor.save_to_wav_file(file_path='path/to/file_2.wav')
        doc_2.bytes_ = doc_1.audio_tensor.to_bytes()

    """

    ...