class JowrException(Exception):
    """jowr custom Exception."""


class CaptureNotOpenError(JowrException):
    """The capture object is not opened/accessible"""
