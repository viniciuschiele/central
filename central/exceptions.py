"""
Exceptions raised by central.
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
    def __init__(self, library_name, library_site):
        super(LibraryRequiredError, self).__init__(
            'You need to install the %s library to use the S3Config. See %s' % (library_name, library_site)
        )


class SchedulerError(Exception):
    """
    An error related to the scheduler.
    """
