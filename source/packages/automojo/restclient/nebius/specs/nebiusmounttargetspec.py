"""
    .. module:: nebiusmounttargetspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusMountTargetSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.restclient.base.schemaobject import SchemaObject
from automojo.restclient.base.schemafield import Field


class NebiusMountTargetSpec(SchemaObject):
    """
        Request payload to create a Nebius shared-filesystem mount target.
    """

    filesystem_id = Field(str, required=True)
    subnet_id = Field(str, required=True)
    mount_path = Field(Optional[str], required=False, default=None)
