"""
    .. module:: nebiusvmspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusVmSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.restclient.base.schemaobject import SchemaObject
from automojo.restclient.base.schemafield import Field


class NebiusVmSpec(SchemaObject):
    """
        Request payload to launch a Nebius virtual machine.
    """

    parent_id = Field(str, required=True)
    name = Field(str, required=True)
    platform = Field(str, required=True)
    preset = Field(str, required=True)
    subnet_id = Field(str, required=True)
    image_id = Field(str, required=True)
    region_id = Field(Optional[str], required=False, default=None)
    ssh_key_ids = Field(Optional[list], required=False, default=None)
    placement_group_id = Field(Optional[str], required=False, default=None)
    metadata = Field(Optional[dict], required=False, default=None)
    labels = Field(Optional[dict], required=False, default=None)
