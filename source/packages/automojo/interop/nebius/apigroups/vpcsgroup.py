"""
    .. module:: vpcsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VpcsGroup` api group
                   exposing the Nebius VPC lifecycle endpoints.

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
from automojo.interop.nebius.model.nebiusvpc import NebiusVpc
from automojo.interop.nebius.specs.nebiusvpcspec import NebiusVpcSpec


class VpcsGroup(RestApiGroup):
    """
        :class:`VpcsGroup` exposes the Nebius VPC lifecycle — create
        (idempotent by name within a project), list (cursor-paged), and
        delete (no-op on an unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, project_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusVpc]:
        """
            List every VPC anchored to a project.

            :param project_id: The Nebius project (parent) identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusVpc` models.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/vpcs"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "parent_id": project_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list vpcs")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusVpc] = []
        for entry in raw_items:
            out.append(NebiusVpc.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, project_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusVpc]:
        """
            Find a VPC by name within a project.

            :param project_id: The Nebius project identifier.
            :param name: The VPC name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusVpc`, or ``None``.
        """
        existing = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[NebiusVpc] = None
        for vpc in existing:
            if vpc.name == name:
                rtnval = vpc
                break
        return rtnval

    def create(self, *, spec: NebiusVpcSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusVpc:
        """
            Create a VPC idempotently.

            An existing VPC of the same name within the same project is
            returned unchanged.

            :param spec: The :class:`NebiusVpcSpec` request payload.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing :class:`NebiusVpc`.
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
            "ipv4_cidr_block": spec.ipv4_cidr_block,
        }
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/vpcs",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create vpc")
        rtnval = NebiusVpc.from_dict(response.json())
        return rtnval

    def delete(self, *, vpc_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a VPC.  A 404 is treated as already-removed.

            :param vpc_id: The Nebius VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``vpc_id`` is empty.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "vpcs", vpc_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete vpc")
        return
