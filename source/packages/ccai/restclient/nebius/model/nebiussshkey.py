"""
    .. module:: nebiussshkey
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusSshKey`.

    Hand-authored from the documented Nebius API per PLAN section 9.2a;
    see AGENTS.md "Codegen Decision".

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from ccai.restclient.base.schemaobject import SchemaObject
from ccai.restclient.base.schemafield import Field


class NebiusSshKey(SchemaObject):
    """
        Typed model of a registered Nebius SSH key.
    """

    id = Field(str, required=True)
    name = Field(Optional[str], required=False, default=None)
    public_key = Field(Optional[str], required=False, default=None)
    fingerprint = Field(Optional[str], required=False, default=None)
