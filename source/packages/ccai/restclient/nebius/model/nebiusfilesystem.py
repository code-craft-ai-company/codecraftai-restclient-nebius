"""
    .. module:: nebiusfilesystem
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusFilesystem`.

    Hand-authored from the documented Nebius API per PLAN section 9.2a;
    see AGENTS.md "Codegen Decision".

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional

from ccai.restclient.base.schemaobject import SchemaObject
from ccai.restclient.base.schemafield import Field


class NebiusFilesystem(SchemaObject):
    """
        Typed model of a Nebius native shared filesystem.
    """

    id = Field(str, required=True)
    name = Field(Optional[str], required=False, default=None)
    parent_id = Field(Optional[str], required=False, default=None)
    size_bytes = Field(Optional[int], required=False, default=None)
    status = Field(Optional[str], required=False, default=None)
    labels = Field(Optional[dict], required=False, default=None)
