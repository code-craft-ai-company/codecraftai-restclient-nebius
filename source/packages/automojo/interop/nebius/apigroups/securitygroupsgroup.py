"""
    .. module:: securitygroupsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SecurityGroupsGroup` api
                   group exposing the Nebius security-group endpoints.

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
from automojo.interop.nebius.model.nebiussecuritygroup import (
    NebiusSecurityGroup
)
from automojo.interop.nebius.specs.nebiussecuritygroupspec import (
    NebiusSecurityGroupSpec
)


class SecurityGroupsGroup(RestApiGroup):
    """
        :class:`SecurityGroupsGroup` exposes the Nebius security-group
        lifecycle — create (idempotent by name), rule-set replacement,
        list, and delete (no-op on an unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, vpc_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusSecurityGroup]:
        """
            List every security group anchored to a VPC.

            :param vpc_id: The Nebius VPC identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusSecurityGroup` models.

            :raises: :class:`SemanticError` when ``vpc_id`` is empty.
        """
        if vpc_id is None or len(vpc_id) == 0:
            raise SemanticError("'vpc_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/security-groups"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "vpc_id": vpc_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response,
                             action="list security groups")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusSecurityGroup] = []
        for entry in raw_items:
            out.append(NebiusSecurityGroup.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, vpc_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusSecurityGroup]:
        """
            Find a security group by name within a VPC.

            :param vpc_id: The Nebius VPC identifier.
            :param name: The security-group name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusSecurityGroup`, or ``None``.
        """
        existing = self.list(vpc_id=vpc_id, aspects=aspects)
        rtnval: Optional[NebiusSecurityGroup] = None
        for sg in existing:
            if sg.name == name:
                rtnval = sg
                break
        return rtnval

    def create(self, *, spec: NebiusSecurityGroupSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusSecurityGroup:
        """
            Create a security group idempotently.

            An existing security group of the same name in the same VPC is
            returned unchanged.

            :param spec: The :class:`NebiusSecurityGroupSpec` payload.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing
                :class:`NebiusSecurityGroup`.
        """
        existing = self.find_by_name(vpc_id=spec.vpc_id, name=spec.name,
                                     aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        body: Dict[str, Any] = {
            "vpc_id": spec.vpc_id,
            "name": spec.name,
        }
        if spec.ingress_rules is not None:
            body["ingress_rules"] = spec.ingress_rules
        if spec.egress_rules is not None:
            body["egress_rules"] = spec.egress_rules
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/security-groups",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create security group")
        rtnval = NebiusSecurityGroup.from_dict(response.json())
        return rtnval

    def set_rules(self, *, sg_id: str,
                  ingress: Optional[List[Dict[str, Any]]] = None,
                  egress: Optional[List[Dict[str, Any]]] = None,
                  aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                  ) -> NebiusSecurityGroup:
        """
            Replace the ingress and egress rule sets on a security group.

            :param sg_id: The Nebius security-group identifier.
            :param ingress: Replacement ingress rule dicts.
            :param egress: Replacement egress rule dicts.
            :param aspects: Behaviour control for the call.

            :returns: The updated :class:`NebiusSecurityGroup`.

            :raises: :class:`SemanticError` when ``sg_id`` is empty.
        """
        if sg_id is None or len(sg_id) == 0:
            raise SemanticError("'sg_id' must be a non-empty string.")

        effective_ingress = ingress if ingress is not None else []
        effective_egress = egress if egress is not None else []

        client = self.client
        leaf = compose_leaf(parts=["v1", "security-groups", sg_id, "rules"])
        body: Dict[str, Any] = {
            "ingress_rules": effective_ingress,
            "egress_rules": effective_egress,
        }
        response = client.request(method="PUT", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response,
                         action="set security group rules")
        rtnval = NebiusSecurityGroup.from_dict(response.json())
        return rtnval

    def delete(self, *, sg_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a security group.  A 404 is treated as already-removed.

            :param sg_id: The Nebius security-group identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``sg_id`` is empty.
        """
        if sg_id is None or len(sg_id) == 0:
            raise SemanticError("'sg_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "security-groups", sg_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete security group")
        return
