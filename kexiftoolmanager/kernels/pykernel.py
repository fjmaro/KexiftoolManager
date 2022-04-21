"""
------------------------------------------------------------------------------
Python wrapper for 'ExifTool' by 'Phil Harvey' https://exiftool.org/ inspired
in 'PyExifTool' library by 'Smarnach' https://github.com/smarnach
------------------------------------------------------------------------------
"""
from typing import List, Dict, Optional
from pathlib import Path
import subprocess
import datetime
import logging
import json
import os

from kjmarotools.basics import filetools

from .pygroups import Keywords


class KernelPrivateTools:
    """
    --------------------------------------------------------------------------
    Functions and tools to be used by PyexifManager
    --------------------------------------------------------------------------
    """
    # pylint: disable=too-few-public-methods
    @staticmethod
    def _execute(arguments: list, timeout=30):
        """execute the commands in the terminal"""
        process = subprocess.run(args=arguments,
                                 stdout=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 encoding='utf8',
                                 check=False,
                                 timeout=timeout)
        return process.stdout

    @staticmethod
    def _logger(name: str, base_path=Path.cwd(), log_level="DEBUG"
                ) -> logging.Logger:
        """Initialize the logger"""
        log_file = base_path.joinpath(name + '.log')
        with open(log_file, "a", encoding="utf-8") as fle:
            fle.write("-" * 41 + "\n")
            fle.write("NEW EXECUTION: " + str(datetime.datetime.now()) + "\n")
            fle.write("-" * 41 + "\n")

        logger = logging.getLogger(name)
        logger.setLevel(log_level)

        fle_hlrs = [isinstance(x, logging.FileHandler
                               ) for x in logger.handlers]
        has_file_handlers = True in fle_hlrs

        cmd_hlrs = [isinstance(x, logging.StreamHandler
                               ) for x in logger.handlers]
        has_cmd_handlers = True in cmd_hlrs

        fmt_text = "%(asctime)s | %(levelname)-5.5s | %(message)s"
        log_formatter = logging.Formatter(fmt_text)

        if not has_file_handlers:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(log_formatter)
            file_handler.setLevel(log_level)
            logger.addHandler(file_handler)

        if not has_cmd_handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            console_handler.setLevel(log_level)
            logger.addHandler(console_handler)
        logger.info("Logger initialized in '%s.log'", logger.name)
        return logger

    @staticmethod
    def _filedates(values) -> datetime.datetime:
        """function to convert file date-fields to datetime"""
        ymd = [int(x) for x in values[0].split(":")]
        hms = [int(x) for x in values[1].split("+")[0].split(":")]
        znes = values[1].split("+")[1].split(":")
        return datetime.datetime(
            ymd[0], ymd[1], ymd[2], hms[0], hms[1], hms[2],
            tzinfo=datetime.timezone(datetime.timedelta(
                hours=int(znes[0]), minutes=int(znes[1]))))

    @staticmethod
    def _metadates(values) -> datetime.datetime:
        """function to convert exif date-fields to datetime"""
        try:
            ymd = [int(x) for x in values[0].split(":")]
            hms = [int(x) for x in values[1].split(":")]
            return datetime.datetime(ymd[0], ymd[1], ymd[2],
                                     hms[0], hms[1], hms[2])
        except ValueError:
            return datetime.datetime(1, 1, 1)

    @staticmethod
    def _setmetadates(kwrd: str, date2add: datetime.datetime) -> str:
        """function used to edit exif datetime fields"""
        bytes_kwd = ('-' + kwrd + '=')
        bytes_date = date2add.strftime("%Y:%m:%d %H:%M:%S")
        return bytes_kwd + bytes_date


class PyKernel(KernelPrivateTools):
    """
    --------------------------------------------------------------------------
                 PyExifManager(PyKernel) Docstring for Development
    --------------------------------------------------------------------------
    Warnings:
    - fast_***(): These functions are executed IMMEDIATELY. See 'kpyfile.py'
                  <fast_set_file_modify_date()> where 'os.utime()' is called.
                  Hence, save_file() is not needed for this functions to have
                  effect in the file given.
    --------------------------------------------------------------------------
    Development:
    - Constant <__KEYWORD> must be added to every new Child of this class
      containing the Child.Keyword assigned (see 'kpyexif.py' as example)

    - See 'kpyexif.py' as example of capabilities expansion and how to get/set
      information (always based on exiftool capabilities).

    - When including a new kernel it must be added to PyExifMgr(...) under
      'pyexifmgr.py' script. (see PyExifManager.__doc__ for further dev-info)
    --------------------------------------------------------------------------
    Structure:
    - Parent class:
        - PyKernel() [allocated in kernels.pykernel.py]

    - Childs class:
        - PyExifKernel(PyKernel) [allocated in kpyexif.py]
        - PyMovKernel(PyKernel) [allocated in kpymov.py]
        - ...
        - Py***Kernel(PyKernel) [to be placed in kpy***.py]
        - ...

    - Keywords: Placed in pygroups.py, it contains the Keywords used by the
                child Kernels to access the metadata fields.

    - Commands:
        self._commands: In this list the regular commands that will generate
                        a copy of the file original as <file_original.ext>
                        must be included.
    --------------------------------------------------------------------------
    Methods to implement:
    - is_*** -> Boolean properties of the file extension itself
    - has_*** -> Boolean properties indicating if a parameter exists
    - get_*** -> get_<exif/file/etc>_fields from the file (error if not found)
    - set_*** -> set_<exif/file/etc>_fields
    - fast_*** -> fast alternative @staticmethods for <is/has/get/set> methods
                  using alternatives to exiftool. WARNING, these actions are
                  executed IMMEDIATELY. eg: os.utime(), or see 'kpyfile.py'
    --------------------------------------------------------------------------
    Attributes:
        self._exiftool_path: Path (command to execute in CMD for exiftool)
        self._filepath: Path of the file loaded
        self._metadata: Dictionary with the metadada loadad
        self._commands: List of commands to be executed
        self.log = logger (if logger_enabled=True)
    --------------------------------------------------------------------------
    ExifTool useful Links:
    - https://exiftool.org/filename.html
    - https://www.exiftool.org/exiftool_pod.html
    --------------------------------------------------------------------------
    """
    def __init__(self, exiftool_path=Path("exiftool"), logger=True,
                 log_path=Path.cwd()) -> None:
        self._exiftool_path: Path = exiftool_path
        self._filepath: Optional[Path] = None
        self._metadata: Dict[str, str] = {}
        self._commands: List[str] = []
        self._log_enabled = logger

        if logger:
            self.log = self._logger('Exiftoolmgr', log_path)
        else:
            self.log = logging.getLogger("")

    @property
    def exiftool_version(self) -> str:
        """get the exiftool version for the given exiftool_path"""
        return self._execute([self._exiftool_path, "-ver"])

    @property
    def exiftool_detected(self) -> bool:
        """get if exiftool version detected in the given exiftool_path"""
        try:
            _ = self.exiftool_version
            return True
        except FileNotFoundError:
            return False

    @property
    def metadata(self) -> dict:
        """metadata of the file loaded"""
        return self._metadata

    @property
    def metadata_as_string(self) -> str:
        """return the metadata in string format"""
        if not self._metadata:
            return ""
        spacer = max([len(x) for x in list(self._metadata.keys())])
        out_str = ""
        for kwd in list(self._metadata.keys()):
            new_line = ("{:<" + str(spacer) + "} | ").format(kwd)
            out_str += new_line + str(self._metadata[kwd]) + "\n"
        return out_str

    @staticmethod
    def help_dev() -> Optional[str]:
        """docstring"""
        return PyKernel.__doc__

    def help(self) -> Optional[str]:
        """docstring"""
        return self.__doc__

    def load_file(self, file2load: Path, timeout=30) -> None:
        """Load the file's metadata"""
        assert file2load.is_file(), f"File not found -> {file2load}"
        if self._log_enabled:
            self.log.info("[ExiftoolMgr] Loading file: %s", file2load)

        self._filepath = file2load
        self._commands = []
        self._metadata = {}
        raw_mdta = self._execute([self._exiftool_path, '-G', '-J', file2load],
                                 timeout)

        load_success = False
        if Keywords.ExifTool.tool_version in raw_mdta:
            self._commands.append(str(self._exiftool_path))
            self._commands.append("-P")
            self._metadata = json.loads(raw_mdta)[0]
            load_success = True

        if self._log_enabled:
            if not load_success:
                self.log.error("File not loaded:    %s", file2load)
                self.log.error("File loading error: %s", raw_mdta)

    def save_file(self, output_filename="", overwrite=False,
                  timeout=30) -> bool:
        """
        ----------------------------------------------------------------------
        Save the file with the commands included in the same path.
        > Returns success=True/False
        ----------------------------------------------------------------------
        Options:
        > overwrite -> If true it overwrites the file, if not adds '-x' where
                       the 'x' is a number from 1 to infinite.
        > output_filename -> If empty it uses the file-loaded name, if not the
                             selected in 'output_filename'
        > timeout -> If the process is locked, after 30 seconds will continue
        ----------------------------------------------------------------------
        """
        if self._filepath is None:
            if self._log_enabled:
                self.log.warning("No file loaded to be saved")
            else:
                print("WARNING: No file loaded to be saved")
            return False

        if len(self._commands) == 2:
            self.log.warning("No commands to execute for %s", self._filepath)
            return False

        if not output_filename or output_filename == self._filepath.name:
            result = self.__save_samename(overwrite, timeout)
            name2log = self._filepath.name
        else:
            result = self.__save_newname(overwrite, output_filename, timeout)
            name2log = output_filename

        if self._log_enabled:
            self.log.info("[ExiftoolMgr] Writing file: %s <in> %s",
                          name2log, self._filepath.parent)
        return ('unchanged' not in result) and ('errors' not in result)

    def __save_samename(self, overwrite: bool, timeout=30) -> str:
        """save file with the same name"""
        assert self._filepath is not None, "File not loaded"

        # If overwrite=False (a new file must be generated)
        if not overwrite:
            new_file_path = filetools.itername(self._filepath)
            return self.__save_newname(False, new_file_path.name)

        # Ese execute the commands and delete the original
        self._commands.append(str(self._filepath))
        result = self._execute(self._commands, timeout)
        name2del = self._filepath.name + "_original"
        os.remove(self._filepath.parent.joinpath(name2del))

        # Log the results of the execution
        if self._log_enabled:
            self.__save_log(overwrite, self._filepath, result)
        return result

    def __save_newname(self, overwrite: bool, output_filename: str, timeout=30
                       ) -> str:
        """save file a new name"""
        assert self._filepath is not None, "File not loaded"
        new_file_path = self._filepath.parent.joinpath(output_filename)

        # If overwrite=True delete the file (if exist)
        if overwrite and new_file_path.is_file():
            os.remove(new_file_path)

        new_file_path = filetools.itername(new_file_path)
        self._commands.append("-filename=" + str(new_file_path))
        self._commands.append(str(self._filepath))
        result = self._execute(self._commands, timeout)

        # Log the results of the execution
        if self._log_enabled:
            self.__save_log(overwrite, new_file_path, result)
        return result

    def __save_log(self, overwrite, file_path_saved, result):
        """Log the results of the execution"""
        lst_result = [x.strip() for x in result.split("\n")]
        str_result = ", # ".join(lst_result)
        commands2log = [str(x) for x in self._commands]
        self.log.info("File saved in filepath: [overwrite=%5s] %s",
                      str(overwrite), file_path_saved)
        self.log.info("File Commands executed: %s", commands2log)
        self.log.info("File execution results: %s", str_result)
