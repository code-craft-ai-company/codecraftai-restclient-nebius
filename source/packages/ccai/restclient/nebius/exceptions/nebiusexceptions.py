"""
    .. module:: nebiusexceptions
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the exception types raised by the
                   Nebius interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


class NebiusAuthenticationError(RuntimeError):
    """
        Raised when the Nebius API rejects the supplied service-account
        credential, or when an HTTP 401/403 is reclassified from the
        transport layer.
    """


class NebiusCidrValidationError(ValueError):
    """
        Raised when a subnet CIDR is not contained within the CIDR of the
        VPC it is being created against.
    """


class NebiusAcceleratorNotAvailableError(RuntimeError):
    """
        Raised when a requested GPU platform/preset is not available in the
        chosen region; raised before the launch request is issued.
    """
