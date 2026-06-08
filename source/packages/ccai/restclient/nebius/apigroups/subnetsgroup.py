"""
    .. module:: subnetsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SubnetsGroup` api group
                   exposing the Nebius subnet lifecycle endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import ipaddress
import os

from typing import Any, Dict, List, Optional

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from ccai.restclient.nebius.nebiusurl import compose_leaf
from ccai.restclient.nebius.apigroups.groupsupport import (
    collect_pages, is_not_found, raise_for_status
)
from ccai.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusCidrValidationError
)
from ccai.restclient.nebius.model.nebiussubnet import NebiusSubnet
from ccai.restclient.nebius.model.nebiusvpc import NebiusVpc
from ccai.restclient.nebius.specs.nebiussubnetspec import NebiusSubnetSpec


def cidr_contained(*, parent_cidr: str, child_cidr: str) -> bool:
    """
        Return whether ``child_cidr`` is fully contained in ``parent_cidr``.

        :param parent_cidr: The containing CIDR block string.
        :param child_cidr: The candidate child CIDR block string.

        :returns: ``True`` when the child is a subnet of the parent.

        :raises: :class:`NebiusCidrValidationError` when either string
            fails to parse as a CIDR network.
    """
    try:
        parent_net = ipaddress.ip_network(parent_cidr, strict=False)
        child_net = ipaddress.ip_network(child_cidr, strict=False)
    except (TypeError, ValueError) as xcpt:
        err_msg_lines = ["Failed to parse a CIDR block."]
        err_msg_lines.append("PARENT: {!r}".format(parent_cidr))
        err_msg_lines.append("CHILD: {!r}".format(child_cidr))
        err_msg_lines.append("CAUSE: {}".format(xcpt))
        err_msg = os.linesep.join(err_msg_lines)
        raise NebiusCidrValidationError(err_msg) from None

    rtnval = child_net.subnet_of(parent_net)
    return rtnval


class SubnetsGroup(RestApiGroup):
    """
        :class:`SubnetsGroup` exposes the Nebius subnet lifecycle — create
        (idempotent by name, with CIDR-containment validation against the
        owning VPC), list (cursor-paged), and delete (no-op on an unknown
        id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, vpc_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusSubnet]:
        """
            List every subnet anchored to a VPC.

            :param vpc_id: The Nebius VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusSubnet` models.

            :raises: :class:`SemanticError` when ``vpc_id`` is empty.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/subnets"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "vpc_id": vpc_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list subnets")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusSubnet] = []
        for entry in raw_items:
            out.append(NebiusSubnet.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, vpc_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusSubnet]:
        """
            Find a subnet by name within a VPC.

            :param vpc_id: The Nebius VPC identifier.
            :param name: The subnet name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusSubnet`, or ``None``.
        """
        existing = self.list(vpc_id=vpc_id, aspects=aspects)
        rtnval: Optional[NebiusSubnet] = None
        for subnet in existing:
            if subnet.name == name:
                rtnval = subnet
                break
        return rtnval

    def _get_vpc(self, *, vpc_id: str,
                 aspects: AspectsNebius) -> NebiusVpc:
        """
            Fetch the owning VPC so its CIDR can bound subnet validation.

            :param vpc_id: The Nebius VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: The :class:`NebiusVpc` model.
        """
        client = self.client
        leaf = compose_leaf(parts=["v1", "vpcs", vpc_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get vpc for subnet")
        rtnval = NebiusVpc.from_dict(response.json())
        return rtnval

    def create(self, *, spec: NebiusSubnetSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusSubnet:
        """
            Create a subnet idempotently.

            The subnet CIDR is validated for containment within the owning
            VPC's CIDR before any create request is issued.  An existing
            subnet of the same name in the same VPC is returned unchanged.

            :param spec: The :class:`NebiusSubnetSpec` request payload.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing :class:`NebiusSubnet`.

            :raises: :class:`NebiusCidrValidationError` when the subnet
                CIDR is not contained within the VPC CIDR.
        """
        owning_vpc = self._get_vpc(vpc_id=spec.vpc_id, aspects=aspects)
        contained = cidr_contained(parent_cidr=owning_vpc.ipv4_cidr_block,
                                   child_cidr=spec.ipv4_cidr_block)
        if contained is False:
            err_msg_lines = [
                "Subnet CIDR is not contained within the VPC CIDR."
            ]
            err_msg_lines.append("VPC_CIDR: {}".format(
                owning_vpc.ipv4_cidr_block))
            err_msg_lines.append("SUBNET_CIDR: {}".format(
                spec.ipv4_cidr_block))
            err_msg = os.linesep.join(err_msg_lines)
            raise NebiusCidrValidationError(err_msg)

        existing = self.find_by_name(vpc_id=spec.vpc_id, name=spec.name,
                                     aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        body: Dict[str, Any] = {
            "vpc_id": spec.vpc_id,
            "name": spec.name,
            "ipv4_cidr_block": spec.ipv4_cidr_block,
            "zone_id": spec.zone_id,
        }
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/subnets",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create subnet")
        rtnval = NebiusSubnet.from_dict(response.json())
        return rtnval

    def delete(self, *, subnet_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a subnet.  A 404 is treated as already-removed.

            :param subnet_id: The Nebius subnet identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``subnet_id`` is empty.
        """
        if subnet_id is None or len(subnet_id) == 0:
            raise SemanticError("'subnet_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "subnets", subnet_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete subnet")
        return
