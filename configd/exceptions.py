"""
Exceptions raised by configd.
"""


class ConfigError(Exception):
    """
    An error related to the config.
    """


class DecoderError(Exception):
    """
    An error related to the decoder.
    """


class InterpolatorError(Exception):
    """
    An error related to the interpolator.
    """


class LibraryRequiredError(Exception):
    """
    A external library is required.
    """


class SchedulerError(Exception):
    """
    An error related to the scheduler.
    """
