"""Groups y keywords for file metadata access"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple


class BaseKwd(ABC):
    """BaseClassForAllKeywords"""
    @property
    @abstractmethod
    def readable(self) -> bool:
        """
        ----------------------------------------------------------------------
        return if the metadata is readable by exiftool (https://exiftool.org/)
        ----------------------------------------------------------------------
        """

    @property
    @abstractmethod
    def editable(self) -> bool:
        """
        ----------------------------------------------------------------------
        return if the metadata is editable by exiftool (https://exiftool.org/)
        ----------------------------------------------------------------------
        """

    @property
    @abstractmethod
    def extensions(self) -> Tuple[str, ...]:
        """
        ----------------------------------------------------------------------
        Return the Keyword list of compatible formats (Uppercase without '.')
        - Keyword: exiftool uses keywords (also called groups) to arrange the
                   metadata information. For each field desired to use, a new
                   Keyword must be created indicating a list with the
                   compatible extensions.
        ----------------------------------------------------------------------
        """


@dataclass
class Keywords:
    """
    --------------------------------------------------------------------------
    keywords for ExifTool Groups/tags.
    - All <Keywords.members> muts be <BaseKwd>
    - It is not possible to have <readable=False and editable=True>
    - NOTE: It is not possible to have <readable=True> or <editable=True> with
            its extensions=() except for <ExifTool> and <File> Keywords since
            those are not real metadata information of the file
    --------------------------------------------------------------------------
    Development Info:
    - Only set 'readable/editable=True' if metadata edition (specially the
      creation_date information) has been successfuly edited with exiftool.
    --------------------------------------------------------------------------
    https://exiftool.org/TagNames/
    --------------------------------------------------------------------------
    """
    @dataclass
    class ExifTool(BaseKwd):
        """ExifTool Group"""
        readable = True
        editable = False
        extensions = ()
        tool_version = "ExifTool:ExifToolVersion"

    @dataclass
    class File(BaseKwd):
        """File Group"""
        readable = True
        editable = False
        extensions = ()
        modify_date = "File:FileModifyDate"
        access_date = "File:FileAccessDate"
        create_date = "File:FileCreateDate"

    @dataclass
    class Exif(BaseKwd):
        """Exif Group"""
        readable = True
        editable = True
        extensions = "JPEG", "JPG", "PNG", "MPO"
        camera_model = "EXIF:Model"
        camera_make = "EXIF:Make"
        modify_date = "EXIF:ModifyDate"
        _date_digitized = "EXIF:CreateDate"  # Not stable, use DatTimeOriginal
        datetime_original = "EXIF:DateTimeOriginal"

    @dataclass
    class QuickTime(BaseKwd):
        """QuickTime and Mov Group"""
        readable = True
        editable = True
        extensions = "MOV", "3GP", "MP4", "M4V"
        create_date = "QuickTime:CreateDate"
        modify_date = "QuickTime:ModifyDate"
        track_create_date = "QuickTime:TrackCreateDate"
        track_modify_date = "QuickTime:TrackModifyDate"
        media_create_date = "QuickTime:MediaCreateDate"
        media_modify_date = "QuickTime:MediaModifyDate"
        comment = "QuickTime:Comment"

    @dataclass
    class Asf(BaseKwd):
        """Asf Group"""
        readable = False
        editable = False
        extensions = ()
        create_date = "ASF:CreationDate"

    @dataclass
    class NoArranged(BaseKwd):
        """no metadata date info"""
        readable = False
        editable = False
        extensions = "BMP", "AVI", "MPG", "WAV", "MP3"
        ext_image = ("BMP", )
        ext_audio = ("WAV", "MP3")
        ext_video = ("AVI", "MPG")


# ----------------------------------------------------------------------------
#                                 AUTOTEST
# ----------------------------------------------------------------------------
# - All <Keywords.members> muts be <BaseKwd>
# - It is not possible to have <readable=False> and <editable=True>
# - It is not possible to have <readable=True> or <editable=True> with its
#   extensions=() except for <ExifTool> and <File> Keywords since those are
#   not real metadata information of the file
# ----------------------------------------------------------------------------
_ERRSZE = 109
_ERRLIN0 = "\n" + "-" * _ERRSZE + "\nERROR: "
_ERRLON1 = "\n" + "-" * _ERRSZE
for _name in [x for x in vars(Keywords) if "__" not in x]:
    _ERRMSG = _ERRLIN0
    _ERRMSG += f"Keywords.{_name} is not a Class.Child of <BaseKwd>"
    _ERRMSG += _ERRLON1
    _INSTANCE = getattr(Keywords, _name)()
    assert isinstance(_INSTANCE, BaseKwd), _ERRMSG

    _ERRMSG = _ERRLIN0
    _ERRMSG += f"Keywords.{_name} can not be <editable> and NOT <readable> "
    _ERRMSG += "at the same time"
    _ERRMSG += _ERRLON1
    assert not (_INSTANCE.editable and not _INSTANCE.readable), _ERRMSG

    _ERRMSG = _ERRLIN0
    _ERRMSG += f"Keywords.{_name} can not be <editable or readable> "
    _ERRMSG += "without indicating its compatible <extensions=()>"
    _ERRMSG += _ERRLON1
    _BOOLER = _INSTANCE.editable or _INSTANCE.readable
    _BOOLCL = _BOOLER and _name not in ('ExifTool', 'File')
    assert not (_BOOLCL and not _INSTANCE.extensions), _ERRMSG
