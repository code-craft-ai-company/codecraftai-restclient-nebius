"""
    .. module:: nebiusfilesystemspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusFilesystemSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.restclient.base.schemaobject import SchemaObject
from automojo.restclient.base.schemafield import Field


class NebiusFilesystemSpec(SchemaObject):
    """
        Request payload to create a Nebius native shared filesystem.
    """

    parent_id = Field(str, required=True)
    name = Field(str, required=True)
    size_bytes = Field(int, required=True)
    labels = Field(Optional[dict], required=False, default=None)
