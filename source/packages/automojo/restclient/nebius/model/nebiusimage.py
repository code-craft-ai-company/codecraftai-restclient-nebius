"""
    .. module:: nebiusimage
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusImage`.

    Hand-authored from the documented Nebius API per PLAN section 9.2a;
    see AGENTS.md "Codegen Decision".

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.restclient.base.schemaobject import SchemaObject
from automojo.restclient.base.schemafield import Field


class NebiusImage(SchemaObject):
    """
        Typed model of a Nebius boot image.
    """

    id = Field(str, required=True)
    name = Field(Optional[str], required=False, default=None)
    family = Field(Optional[str], required=False, default=None)
    version = Field(Optional[str], required=False, default=None)
    architecture = Field(Optional[str], required=False, default=None)
    status = Field(Optional[str], required=False, default=None)
