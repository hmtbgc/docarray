from typing import TYPE_CHECKING, Any, Tuple, Type, TypeVar, Union

import numpy as np
from pydantic.tools import parse_obj_as

from docarray.typing import AudioNdArray, NdArray
from docarray.typing.tensor.video import VideoNdArray
from docarray.typing.url.any_url import AnyUrl

if TYPE_CHECKING:
    from pydantic import BaseConfig
    from pydantic.fields import ModelField

    from docarray.proto import NodeProto

T = TypeVar('T', bound='VideoUrl')

VIDEO_FILE_FORMATS = ['mp4']


class VideoUrl(AnyUrl):
    """
    URL to a .wav file.
    Can be remote (web) URL, or a local file path.
    """

    def _to_node_protobuf(self: T) -> 'NodeProto':
        """Convert Document into a NodeProto protobuf message. This function should
        be called when the Document is nested into another Document that needs to
        be converted into a protobuf
        :return: the nested item protobuf message
        """
        from docarray.proto import NodeProto

        return NodeProto(video_url=str(self))

    @classmethod
    def validate(
        cls: Type[T],
        value: Union[T, np.ndarray, Any],
        field: 'ModelField',
        config: 'BaseConfig',
    ) -> T:
        url = super().validate(value, field, config)
        has_video_extension = any(ext in url for ext in VIDEO_FILE_FORMATS)
        if not has_video_extension:
            raise ValueError(
                f'Video URL must have one of the following extensions:'
                f'{VIDEO_FILE_FORMATS}'
            )
        return cls(str(url), scheme=None)

    def _load(
        self: T, skip_type: str, **kwargs
    ) -> Tuple[AudioNdArray, VideoNdArray, NdArray]:
        """
        Load the data from the url into a Tuple of AudioNdArray, VideoNdArray and
        NdArray.

        :param skip_type: determines what video frames to discard. Supported strings
            are: 'NONE', 'DEFAULT', 'NONREF', 'BIDIR', 'NONINTRA', 'NONKEY', 'ALL'.
        :param kwargs: supports all keyword arguments that are being supported by
            av.open() as described in:
            https://pyav.org/docs/stable/api/_globals.html?highlight=open#av.open

        :return: AudioNdArray representing the audio content, VideoNdArray representing
            the images of the video, NdArray of the key frame indices.

        """
        import av

        with av.open(self, **kwargs) as container:
            stream = container.streams.video[0]
            stream.codec_context.skip_frame = skip_type

            audio_frames = []
            video_frames = []
            keyframe_indices = []

            for frame in container.decode(
                video=0, audio=0 if skip_type != 'NONKEY' else []
            ):
                if type(frame) == av.audio.frame.AudioFrame:
                    audio_frames.append(frame.to_ndarray())
                elif type(frame) == av.video.frame.VideoFrame:
                    video_frames.append(frame.to_ndarray(format='rgb24'))

                    if frame.key_frame == 1:
                        curr_index = len(video_frames)
                        keyframe_indices.append(curr_index)

        if len(audio_frames) == 0:
            audio = parse_obj_as(AudioNdArray, np.array(audio_frames))
        else:
            audio = parse_obj_as(AudioNdArray, np.stack(audio_frames))

        video = parse_obj_as(VideoNdArray, np.stack(video_frames))
        indices = parse_obj_as(NdArray, keyframe_indices)

        return audio, video, indices

    def load(self: T, **kwargs) -> Tuple[AudioNdArray, VideoNdArray, NdArray]:
        """
        Load the data from the url into a Tuple of AudioNdArray, VideoNdArray and
        NdArray.

        :param kwargs: supports all keyword arguments that are being supported by
            av.open() as described in:
            https://pyav.org/docs/stable/api/_globals.html?highlight=open#av.open

        :return: AudioNdArray representing the audio content, VideoNdArray representing
            the images of the video, NdArray of the key frame indices.


        EXAMPLE USAGE

        .. code-block:: python

            from typing import Optional

            from docarray import BaseDocument

            from docarray.typing import VideoUrl, VideoNdArray, AudioNdArray, NdArray


            class MyDoc(BaseDocument):
                video_url: VideoUrl
                video: Optional[VideoNdArray]
                audio: Optional[AudioNdArray]
                key_frame_indices: Optional[NdArray]


            doc = MyDoc(
                video_url='https://github.com/docarray/docarray/tree/feat-add-video-v2/tests/toydata/mov_bbb.mp4?raw=true'
            )
            doc.audio, doc.video, doc.key_frame_indices = doc.video_url.load()

            assert isinstance(doc.video, VideoNdArray)
            assert isinstance(doc.audio, AudioNdArray)
            assert isinstance(doc.key_frame_indices, NdArray)

        """
        return self._load(skip_type='DEFAULT', **kwargs)

    def load_key_frames(self: T, **kwargs) -> VideoNdArray:
        """
        Load the data from the url into a VideoNdArray or Tuple of AudioNdArray,
        VideoNdArray and NdArray.

        :param kwargs: supports all keyword arguments that are being supported by
            av.open() as described in:
            https://pyav.org/docs/stable/api/_globals.html?highlight=open#av.open

        :return: VideoNdArray representing the keyframes.

        EXAMPLE USAGE

        .. code-block:: python

            from typing import Optional

            from docarray import BaseDocument

            from docarray.typing import VideoUrl, VideoNdArray


            class MyDoc(BaseDocument):
                video_url: VideoUrl
                video_key_frames: Optional[VideoNdArray]


            doc = MyDoc(
                video_url='https://github.com/docarray/docarray/tree/feat-add-video-v2/tests/toydata/mov_bbb.mp4?raw=true'
            )
            doc.video_key_frames = doc.video_url.load_key_frames()

            assert isinstance(doc.video_key_frames, VideoNdArray)

        """
        _, key_frames, _ = self._load(skip_type='NONKEY', **kwargs)
        return key_frames