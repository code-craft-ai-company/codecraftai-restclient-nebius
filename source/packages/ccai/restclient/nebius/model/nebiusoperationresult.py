"""
    .. module:: nebiusoperationresult
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API model class :class:`NebiusOperationResult`.

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


class NebiusOperationResult(SchemaObject):
    """
        Typed model of a Nebius long-running operation status payload.
    """

    id = Field(str, required=True)
    done = Field(Optional[bool], required=False, default=None)
    status = Field(Optional[str], required=False, default=None)
    error = Field(Optional[str], required=False, default=None)
    resource_id = Field(Optional[str], required=False, default=None)
    metadata = Field(Optional[dict], required=False, default=None)
