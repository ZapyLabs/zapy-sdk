import sys
import textwrap
import traceback

from typing_extensions import TypedDict

from zapy.utils.singleton import SingletonMeta


class TracebackInfo(TypedDict):
    exception_type: str
    exception_message: str
    line: int
    stacktrace: str


def annotate_traceback(exc_obj: BaseException, script="", location=""):
    traceback_info = TracebackHandler().extract(script, location)
    exc_obj._parse_errors = traceback_info
    exc_obj.add_note(traceback_info["stacktrace"])
    return traceback_info


def recover_traceback(exc_obj: BaseException):
    return getattr(exc_obj, "_parse_errors", None)


def copy_traceback(exc_obj: BaseException, from_exc: BaseException):
    info = recover_traceback(from_exc)
    if info:
        exc_obj._parse_errors = info
        exc_obj.add_note(info["stacktrace"])
    return info


class TracebackHandler(metaclass=SingletonMeta):
    header = "Traceback (most recent call last):"

    def extract(self, script="", location="") -> TracebackInfo:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        frame_summary = traceback.extract_tb(exc_tb)[-1]
        if frame_summary.filename == "<string>":
            return self.extract_from_frame(frame_summary, exc_obj, script=script, location=location)
        else:
            return self.extract_from_error(exc_obj, location=location)

    def extract_from_frame(self, frame_summary: traceback.FrameSummary, exc_obj, script="", location=""):
        stacktrace = textwrap.dedent(
            f"""\
            {self.header}
              {location}, line {frame_summary.lineno}, in {frame_summary.name}
                {frame_summary.line or self.__extract_line(script, frame_summary.lineno)}
            {exc_obj.__class__.__name__}: {exc_obj}"""
        )
        return {
            "exception_type": exc_obj.__class__.__name__,
            "exception_message": str(exc_obj),
            "line": frame_summary.lineno,
            "stacktrace": stacktrace,
        }

    def extract_from_error(self, exc_obj, location=""):
        tracelines = traceback.format_exception_only(exc_obj)
        tracelines[0] = tracelines[0].replace('File "<string>"', location)
        tracelines.insert(0, self.header + "\n")
        return {
            "exception_type": exc_obj.__class__.__name__,
            "exception_message": str(exc_obj),
            "line": exc_obj.lineno if isinstance(exc_obj, SyntaxError) else None,
            "stacktrace": "".join(tracelines),
        }

    def __extract_line(self, script: str, line: int):
        if not script:
            return ""
        try:
            script_lines = script.split("\n")
            return script_lines[line - 1].strip()
        except Exception:
            return "<<Zapy: line omitted due to an error on extraction, check your line separation>>"
