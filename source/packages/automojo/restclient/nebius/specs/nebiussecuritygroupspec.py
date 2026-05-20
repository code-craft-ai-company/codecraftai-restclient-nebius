"""
    .. module:: nebiussecuritygroupspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusSecurityGroupSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.restclient.base.schemaobject import SchemaObject
from automojo.restclient.base.schemafield import Field


class NebiusSecurityGroupSpec(SchemaObject):
    """
        Request payload to create a Nebius security group.
    """

    vpc_id = Field(str, required=True)
    name = Field(str, required=True)
    ingress_rules = Field(Optional[list], required=False, default=None)
    egress_rules = Field(Optional[list], required=False, default=None)
    labels = Field(Optional[dict], required=False, default=None)
