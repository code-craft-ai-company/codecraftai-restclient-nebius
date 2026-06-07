"""
    .. module:: tagsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`TagsGroup` api group
                   exposing the Nebius resource-labelling endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from ccai.restclient.nebius.nebiusurl import compose_leaf
from ccai.restclient.nebius.apigroups.groupsupport import raise_for_status


# Nebius labels resources under one of these resource-type sub-paths.
_RESOURCE_TYPE_PATHS = {
    "vpc": "vpcs",
    "subnet": "subnets",
    "security_group": "security-groups",
    "disk": "disks",
    "placement_group": "placement-groups",
    "vm": "instances",
    "instance": "instances",
    "filesystem": "file-storages",
}


def neutral_tags_to_labels(*, neutral_tags: List[Dict[str, str]]
                           ) -> Dict[str, str]:
    """
        Translate the neutral ``List[Dict[str, str]]`` tag shape into the
        Nebius labels dict.

        :param neutral_tags: A list of single-entry ``{key: value}`` dicts.

        :returns: A flat labels dict.

        :raises: :class:`SemanticError` when an entry is not a single-key
            dict or a duplicate key is detected.
    """
    labels: Dict[str, str] = {}
    for entry in neutral_tags:
        if not isinstance(entry, dict):
            raise SemanticError(
                "Neutral tag entry must be a dict; got {!r}.".format(entry)
            )
        if len(entry) != 1:
            raise SemanticError(
                "Neutral tag entry must be a single-key dict; got "
                "{!r}.".format(entry)
            )
        for key, value in entry.items():
            if key in labels:
                raise SemanticError(
                    "Duplicate tag key in neutral tag set: {!r}.".format(key)
                )
            labels[key] = value
    rtnval = labels
    return rtnval


class TagsGroup(RestApiGroup):
    """
        :class:`TagsGroup` exposes the Nebius resource-labelling endpoint.
        ``apply`` translates the neutral tag shape into the Nebius labels
        dict and PATCHes the resource.
    """

    BASE_LEAF = "/v1"

    def apply(self, *, resource_type: str, resource_id: str,
              tags: List[Dict[str, str]],
              aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Apply a tag set to a Nebius resource.

            :param resource_type: Neutral resource-type string (e.g.
                ``vpc``, ``subnet``, ``vm``).
            :param resource_id: The Nebius resource identifier.
            :param tags: The neutral ``List[Dict[str, str]]`` tag set.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``resource_id`` is empty or
                ``resource_type`` is unknown.
        """
        if resource_id is None or len(resource_id) == 0:
            raise SemanticError("'resource_id' must be a non-empty string.")

        path_segment = _RESOURCE_TYPE_PATHS.get(resource_type, None)
        if path_segment is None:
            raise SemanticError(
                "Unknown Nebius resource_type {!r}; known: {}.".format(
                    resource_type,
                    ", ".join(sorted(_RESOURCE_TYPE_PATHS.keys())),
                )
            )

        labels = neutral_tags_to_labels(neutral_tags=tags)

        client = self.client
        leaf = compose_leaf(parts=["v1", path_segment, resource_id])
        body: Dict[str, Any] = {"labels": labels}
        response = client.request(method="PATCH", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response, action="apply tags")
        return
