"""
    .. module:: nebiusvm
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusVm`.

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


class NebiusVm(SchemaObject):
    """
        Typed model of a Nebius virtual machine.
    """

    id = Field(str, required=True)
    name = Field(Optional[str], required=False, default=None)
    parent_id = Field(Optional[str], required=False, default=None)
    platform = Field(Optional[str], required=False, default=None)
    preset = Field(Optional[str], required=False, default=None)
    subnet_id = Field(Optional[str], required=False, default=None)
    status = Field(Optional[str], required=False, default=None)
    placement_group_id = Field(Optional[str], required=False, default=None)
    metadata = Field(Optional[dict], required=False, default=None)
    labels = Field(Optional[dict], required=False, default=None)
