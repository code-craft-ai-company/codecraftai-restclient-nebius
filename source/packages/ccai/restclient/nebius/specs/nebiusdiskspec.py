"""
    .. module:: nebiusdiskspec
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Hand-authored typed Nebius API request payload :class:`NebiusDiskSpec`.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Optional

from ccai.restclient.base.schemaobject import SchemaObject
from ccai.restclient.base.schemafield import Field


class NebiusDiskSpec(SchemaObject):
    """
        Request payload to create a Nebius block-storage disk.
    """

    parent_id = Field(str, required=True)
    name = Field(str, required=True)
    size_bytes = Field(int, required=True)
    type = Field(str, required=True)
    labels = Field(Optional[dict], required=False, default=None)
