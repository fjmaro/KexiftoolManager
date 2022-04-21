"""kpyexif"""
import datetime
from pathlib import Path
from .pykernel import PyKernel
from .pygroups import Keywords


class PyExifKernel(PyKernel):
    """
    --------------------------------------------------------------------------
    Class for Exif metadata. It includes fast methods for exif-jpg oriented
    detection only.
    --------------------------------------------------------------------------
    """
    __KEYWORD = Keywords.Exif

    def __init__(self, exiftool_path=Path("exiftool"), logger=True,
                 log_path=Path.cwd()) -> None:
        super().__init__(exiftool_path=exiftool_path, logger=logger,
                         log_path=log_path)

    @property
    def has_exif_date_original_field(self) -> bool:
        """Check if the EXIF:DateTimeOriginal keyword exists"""
        return self.__KEYWORD.datetime_original in self._metadata

    @property
    def has_exif_modify_date(self) -> bool:
        """Check if the EXIF:ModifyDate exists (DateTime)"""
        if self.__KEYWORD.modify_date in self._metadata:
            try:
                self.get_exif_modify_date()
                return True
            except IndexError:
                return False
            except KeyError:
                return False
            except ValueError:
                return False
        return False

    @property
    def has_exif_original_date(self) -> bool:
        """Check if the EXIF:DateTimeOriginal exists (Original)"""
        if self.__KEYWORD.datetime_original in self._metadata:
            try:
                self.get_exif_original_date()
                return True
            except IndexError:
                return False
            except KeyError:
                return False
            except ValueError:
                return False
        return False

    @property
    def has_exif_digitized_date(self) -> bool:
        """Check if the EXIF:CreateDate exists (Digitized)"""
        # pylint: disable=protected-access
        if self.__KEYWORD._date_digitized in self._metadata:
            try:
                self.get_exif_digitized_date()
                return True
            except IndexError:
                return False
            except KeyError:
                return False
            except ValueError:
                return False
        return False

    def get_exif_camera_make(self) -> str:
        """get the EXIF:Make (camera make)"""
        if self.__KEYWORD.camera_make in self._metadata:
            return self._metadata[self.__KEYWORD.camera_make]
        return ""

    def get_exif_camera_model(self) -> str:
        """get the EXIF:Model (camera model)"""
        if self.__KEYWORD.camera_model in self._metadata:
            return self._metadata[self.__KEYWORD.camera_model]
        return ""

    def get_exif_modify_date(self) -> datetime.datetime:
        """get the EXIF:ModifyDate in datetime format (DateTime)"""
        values = self._metadata[self.__KEYWORD.modify_date].split()
        return self._metadates(values)

    def get_exif_original_date(self) -> datetime.datetime:
        """get the EXIF:DateTimeOriginal in datetime format"""
        values = self._metadata[self.__KEYWORD.datetime_original].split()
        return self._metadates(values)

    def get_exif_digitized_date(self) -> datetime.datetime:
        """get the EXIF:CreateDate in datetime format (Digitized)"""
        # pylint: disable=protected-access
        values = self._metadata[self.__KEYWORD._date_digitized].split()
        return self._metadates(values)

    def get_exif_date_original_as_str(self) -> str:
        """get the EXIF:DateTimeOriginal in string format"""
        return self._metadata[self.__KEYWORD.datetime_original]

    def set_exif_modify_date(self, date2add: datetime.datetime) -> None:
        """set the EXIF:ModifyDate field"""
        self._commands.append(self._setmetadates(
            self.__KEYWORD.modify_date, date2add))

    def set_exif_original_date(self, date2add: datetime.datetime) -> None:
        """set the EXIF:DateTimeOriginal field"""
        self._commands.append(self._setmetadates(
            self.__KEYWORD.datetime_original, date2add))

    def _set_exif_digitized_date(self, date2add: datetime.datetime) -> None:
        """
        ----------------------------------------------------------------------
        set the EXIF:CreateDate field NOTE: Not Always working, use DTOriginal
        - in ExifTool EXIF:CreateDate is the Exif:DateTimeDigitized.
        ----------------------------------------------------------------------
        """
        # pylint: disable=protected-access
        self._commands.append(self._setmetadates(
            self.__KEYWORD._date_digitized, date2add))
