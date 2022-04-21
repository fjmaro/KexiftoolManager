"""
------------------------------------------------------------------------------
Python wrapper for 'ExifTool' by 'Phil Harvey' https://exiftool.org/ inspired
in 'PyExifTool' library by 'Smarnach' https://github.com/smarnach
------------------------------------------------------------------------------
"""
import datetime
from typing import Tuple, Type
from pathlib import Path

from .kernels.pykernel import PyKernel, Keywords
from .kernels import BaseKwd, kpyexif, kpymov


class ExifToolManager(kpyexif.PyExifKernel, kpymov.PyMovKernel):
    """
    --------------------------------------------------------------------------
                           ExifToolMgr Docstring
    --------------------------------------------------------------------------
    Warnings:
    - fast_***(): These functions are executed IMMEDIATELY. See 'kpyfile.py'
                  <fast_set_file_modify_date()> where 'os.utime()' is called.
                  Hence, save_file() is not needed for this functions to have
                  effect in the file given.
    --------------------------------------------------------------------------
    Development:
    - For further development see 'PyKernel' docstring in 'kernel.py' or call:
        - ExifToolMgr.help_dev()
    - Then add the functions to this class functions:
        - has_metadata_create_date
        - get_metadata_create_date
        - set_metadata_create_date
    --------------------------------------------------------------------------
    Arguments:
    - exiftool_path -> Exiftool must be installed or in PATH variables under
                       'exiftool' name. Alternatively, the file location path
                       can be included in this field
    - logger -> Used for debugging, it generates a logging file if True[bool]
    --------------------------------------------------------------------------
    Main Methods:
    - metadata -> Dictionary with all metadata
    - load_file() -> load file to read/write/edit
    - save_file() -> Save the changes added with 'set_***' functions
    --------------------------------------------------------------------------
    Basic Methods:
    - is_*** -> Boolean properties of the file extension itself
    - has_*** -> Boolean properties indicating if a parameter exists
    - get_*** -> get_<exif/file/etc>_fields from the file (error if not found)
    - set_*** -> set_<exif/file/etc>_fields
    --------------------------------------------------------------------------
    ExifTool useful Links:
    - https://exiftool.org/filename.html
    - https://www.exiftool.org/exiftool_pod.html
    --------------------------------------------------------------------------
    """
    # pylint: disable=protected-access
    def __init__(self, exiftool_path=Path("exiftool"), logger=True,
                 log_path=Path.cwd()) -> None:
        super().__init__(exiftool_path=exiftool_path, logger=logger,
                         log_path=log_path)

        # Get the Readable and Dditable formats based on PyExifManager.Parents
        self._readable_formats = self.fast_readable_formats()
        self._editable_formats = self.fast_editable_formats()

        # Get the BaseClases and Keywords
        self._bases: Tuple[Type[PyKernel], ...] = ()
        self._keywords: Tuple[Type[BaseKwd], ...] = ()
        for child in ExifToolManager.__bases__:
            child_kwd = getattr(child, "_" + child.__name__ + "__KEYWORD")
            self._keywords += (child_kwd, )
            self._bases += (child, )

    @property
    def readable_extensions(self) -> Tuple[str, ...]:
        """get all the readable formats"""
        return self._readable_formats

    @property
    def editable_extensions(self) -> Tuple[str, ...]:
        """get all the editable formats"""
        return self._editable_formats

    @property
    def has_readable_metadate(self) -> bool:
        """return if the metadata creation date is readable"""
        assert self._filepath is not None, "file not loaded"
        return self._filepath.suffix[1:].upper() in self._readable_formats

    @property
    def has_editable_metadate(self) -> bool:
        """return if the metadata creation date is editable"""
        assert self._filepath is not None, "file not loaded"
        return self._filepath.suffix[1:].upper() in self._editable_formats

    @property
    def has_metadata_date_original_field(self) -> bool:
        """
        Get if the field containing the original date exist
        """
        if not self.has_readable_metadate:
            return False
        if self.has_exif_date_original_field:
            return True
        if self.has_mov_create_date_field:
            return True
        return False

    @property
    def has_metadata_date_original(self) -> bool:
        """
        Function to scan if the file has createdate
        > Include more cases if added to 'kernels'
        """
        if not self.has_readable_metadate:
            return False
        if self.has_exif_original_date:
            return True
        if self.has_mov_create_date:
            return True
        return False

    @staticmethod
    def fast_readable_formats() -> Tuple[str, ...]:
        """Get the Readable formats based on PyExifManager.Parents"""
        readable_formats: Tuple[str, ...] = ()
        for chld in ExifToolManager.__bases__:
            kwrd: BaseKwd = getattr(chld, "_" + chld.__name__ + "__KEYWORD")
            if kwrd.readable:
                readable_formats += kwrd.extensions
        return readable_formats

    @staticmethod
    def fast_editable_formats() -> Tuple[str, ...]:
        """Get the Editable formats based on PyExifManager.Parents"""
        editable_formats: Tuple[str, ...] = ()
        for chld in ExifToolManager.__bases__:
            kwrd: BaseKwd = getattr(chld, "_" + chld.__name__ + "__KEYWORD")
            if kwrd.editable:
                editable_formats += kwrd.extensions
        return editable_formats

    @staticmethod
    def fast_has_readable_metadate(filename: Path) -> bool:
        """return if the metadata creation date is readable"""
        extn = filename.suffix[1:].upper()
        return extn in ExifToolManager.fast_readable_formats()

    @staticmethod
    def fast_has_editable_metadate(filename: Path) -> bool:
        """return if the metadata creation date is editable"""
        extn = filename.suffix[1:].upper()
        return extn in ExifToolManager.fast_editable_formats()

    def get_date_original(self) -> datetime.datetime:
        """
        Function to return the file has createdate
        > Include more cases if added to 'kernels'
        """
        if self.has_exif_original_date:
            return self.get_exif_original_date()
        if self.has_mov_create_date:
            return self.get_mov_create_date()

        err_msg = "No metadata! call 'self.has_metadata_create_date' "
        err_msg += "for avoiding this error"
        assert False, err_msg

    def get_date_original_as_str(self) -> str:
        """
        Function to return the file has createdate
        > Include more cases if added to 'kernels'
        """
        if self.has_exif_date_original_field:
            return self.get_exif_date_original_as_str()
        if self.has_mov_create_date_field:
            return self.get_mov_create_date_as_str()
        return ""

    def set_date_original(self, date2add: datetime.datetime):
        """set the metadata creation date"""
        assert self._filepath is not None, "file not loaded"
        extension = self._filepath.suffix[1:].upper()

        if extension in Keywords.Exif.extensions:
            self.set_exif_original_date(date2add)

        elif extension in Keywords.QuickTime.extensions:
            self.set_mov_create_date(date2add)

        else:
            err_msg = "No compatible file to set metadata createdate! call "
            err_msg += "'self.has_editable_metadate' for avoiding this error"
            assert False, err_msg


# ----------------------------------------------------------------------------
#                                 AUTOTEST
# ----------------------------------------------------------------------------
# Verify that every <ExifToolMgr.Childs> has a valid constant <__KEYWORD>
# ----------------------------------------------------------------------------
_ERRSZE = 109
_ERRLIN0 = "\n" + "-" * _ERRSZE + "\nERROR: "
_ERRLON1 = "\n" + "-" * _ERRSZE
for _child in ExifToolManager.__bases__:
    try:
        _kwd = getattr(_child, "_" + _child.__name__ + "__KEYWORD")
        _ERRMSG = _ERRLIN0
        _ERRMSG += f"{_child}.__KEYWORD is not a <BaseKwd> subclass"
        _ERRMSG += _ERRLON1
        assert issubclass(_kwd, BaseKwd), _ERRMSG
    except AttributeError:
        _ERRMSG = _ERRLIN0
        _ERRMSG += f"{_child} has not the mandatory attribute <__KEYWORD>."
        _ERRMSG += _ERRLON1
        assert False, _ERRMSG
