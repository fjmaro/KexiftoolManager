"""kpymov"""
import datetime
from pathlib import Path
from .pykernel import PyKernel
from .pygroups import Keywords


class PyMovKernel(PyKernel):
    """
    --------------------------------------------------------------------------
    Class for Mov
    --------------------------------------------------------------------------
    """
    __KEYWORD = Keywords.QuickTime

    def __init__(self, exiftool_path=Path("exiftool"), logger=True,
                 log_path=Path.cwd()) -> None:
        super().__init__(exiftool_path=exiftool_path, logger=logger,
                         log_path=log_path)

    @property
    def has_mov_create_date_field(self) -> bool:
        """Check if the QuickTime:CreateDate field exists"""
        return self.__KEYWORD.create_date in self._metadata

    @property
    def has_mov_create_date(self) -> bool:
        """Check if the QuickTime:CreateDate exists"""
        if self.__KEYWORD.create_date in self._metadata:
            try:
                self.get_mov_create_date()
                return True
            except IndexError:
                return False
            except KeyError:
                return False
            except ValueError:
                return False
        return False

    def get_mov_create_date(self) -> datetime.datetime:
        """get the QuickTime:CreateDate in datetime format"""
        values = self._metadata[self.__KEYWORD.create_date].split()
        return self._metadates(values)

    def get_mov_create_date_as_str(self) -> str:
        """get the QuickTime:CreateDate in datetime format"""
        return self._metadata[self.__KEYWORD.create_date]

    def get_mov_comment(self) -> str:
        """get the QuickTime:Comment format"""
        values = self._metadata[self.__KEYWORD.comment]
        return values

    def set_mov_create_date(self, date2add: datetime.datetime) -> None:
        """set the QuickTime:CreateDate field"""
        self._commands.append(self._setmetadates(
            self.__KEYWORD.create_date, date2add))

    def set_mov_comment(self, comment: str) -> None:
        """set the QuickTime:Comment field"""
        self._commands.append(f'-{self.__KEYWORD.comment}={comment}')
