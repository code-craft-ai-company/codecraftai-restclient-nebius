"""
    .. module:: placementgroupsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`PlacementGroupsGroup` api
                   group exposing the Nebius IB-enabled placement-group
                   (GPU cluster) endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.interop.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from automojo.interop.nebius.nebiusurl import compose_leaf
from automojo.interop.nebius.apigroups.groupsupport import (
    collect_pages, is_not_found, raise_for_status
)
from automojo.interop.nebius.model.nebiusplacementgroup import (
    NebiusPlacementGroup
)
from automojo.interop.nebius.specs.nebiusplacementgroupspec import (
    NebiusPlacementGroupSpec
)


class PlacementGroupsGroup(RestApiGroup):
    """
        :class:`PlacementGroupsGroup` exposes the Nebius IB-enabled
        placement-group (GPU cluster) lifecycle — create (idempotent by
        name, carrying the interconnect kind), list, and delete (no-op on an
        unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, project_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusPlacementGroup]:
        """
            List every placement group anchored to a project.

            :param project_id: The Nebius project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusPlacementGroup` models.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/placement-groups"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "parent_id": project_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response,
                             action="list placement groups")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusPlacementGroup] = []
        for entry in raw_items:
            out.append(NebiusPlacementGroup.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, project_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusPlacementGroup]:
        """
            Find a placement group by name within a project.

            :param project_id: The Nebius project identifier.
            :param name: The placement-group name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusPlacementGroup`, or
                ``None``.
        """
        existing = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[NebiusPlacementGroup] = None
        for pg in existing:
            if pg.name == name:
                rtnval = pg
                break
        return rtnval

    def create(self, *, spec: NebiusPlacementGroupSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusPlacementGroup:
        """
            Create an IB-enabled placement group idempotently.

            An existing placement group of the same name in the same
            project is returned unchanged.

            :param spec: The :class:`NebiusPlacementGroupSpec` payload.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing
                :class:`NebiusPlacementGroup`.
        """
        existing = self.find_by_name(project_id=spec.parent_id,
                                     name=spec.name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        body: Dict[str, Any] = {
            "parent_id": spec.parent_id,
            "name": spec.name,
            "interconnect": spec.interconnect,
        }
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/placement-groups",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create placement group")
        rtnval = NebiusPlacementGroup.from_dict(response.json())
        return rtnval

    def delete(self, *, placement_group_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a placement group.  A 404 is treated as already-removed.

            :param placement_group_id: The Nebius placement-group id.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when the identifier is empty.
        """
        if placement_group_id is None or len(placement_group_id) == 0:
            raise SemanticError(
                "'placement_group_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(parts=["v1", "placement-groups",
                                   placement_group_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete placement group")
        return
