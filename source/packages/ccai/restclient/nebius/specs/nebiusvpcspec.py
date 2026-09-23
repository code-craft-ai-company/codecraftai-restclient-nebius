"""
    .. module:: nebiusvpcspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusVpcSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional

from ccai.restclient.base.schemaobject import SchemaObject
from ccai.restclient.base.schemafield import Field


class NebiusVpcSpec(SchemaObject):
    """
        Request payload to create a Nebius VPC network.
    """

    parent_id = Field(str, required=True)
    name = Field(str, required=True)
    ipv4_cidr_block = Field(str, required=True)
    labels = Field(Optional[dict], required=False, default=None)
