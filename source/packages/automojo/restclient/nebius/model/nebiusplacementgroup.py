"""
    .. module:: nebiusplacementgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusPlacementGroup`.

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


class NebiusPlacementGroup(SchemaObject):
    """
        Typed model of a Nebius IB-enabled placement group (GPU cluster).
    """

    id = Field(str, required=True)
    name = Field(Optional[str], required=False, default=None)
    parent_id = Field(Optional[str], required=False, default=None)
    interconnect = Field(Optional[str], required=False, default=None)
    status = Field(Optional[str], required=False, default=None)
    labels = Field(Optional[dict], required=False, default=None)
