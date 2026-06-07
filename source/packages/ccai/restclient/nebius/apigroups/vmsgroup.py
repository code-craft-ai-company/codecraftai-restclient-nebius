"""
    .. module:: vmsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`VmsGroup` api group
                   exposing the Nebius virtual-machine lifecycle endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import os

from typing import Any, Dict, List, Optional, Tuple

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from ccai.restclient.nebius.nebiusurl import compose_leaf
from ccai.restclient.nebius.apigroups.disksgroup import _operation_id_of
from ccai.restclient.nebius.apigroups.groupsupport import (
    collect_pages, is_not_found, raise_for_status
)
from ccai.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusAcceleratorNotAvailableError
)
from ccai.restclient.nebius.model.nebiustaskhandle import NebiusTaskHandle
from ccai.restclient.nebius.model.nebiusvm import NebiusVm
from ccai.restclient.nebius.specs.nebiusvmspec import NebiusVmSpec


class VmsGroup(RestApiGroup):
    """
        :class:`VmsGroup` exposes the Nebius virtual-machine lifecycle.

        ``launch`` checks GPU-platform availability in the chosen region
        before issuing the request and returns the typed model alongside a
        :class:`NebiusTaskHandle`.  Power and terminate operations follow
        HTTP semantics, with idempotent terminate.
    """

    BASE_LEAF = "/v1"

    def list(self, *, project_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusVm]:
        """
            List every VM anchored to a project.

            :param project_id: The Nebius project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusVm` models.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/instances"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "parent_id": project_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list vms")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusVm] = []
        for entry in raw_items:
            out.append(NebiusVm.from_dict(entry))
        rtnval = out
        return rtnval

    def get(self, *, vm_id: str,
            aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> NebiusVm:
        """
            Retrieve a single VM by identifier.

            :param vm_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusVm` model.

            :raises: :class:`SemanticError` when ``vm_id`` is empty.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "instances", vm_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get vm")
        rtnval = NebiusVm.from_dict(response.json())
        return rtnval

    def find_by_name(self, *, project_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusVm]:
        """
            Find a VM by name within a project.

            :param project_id: The Nebius project identifier.
            :param name: The VM name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusVm`, or ``None``.
        """
        existing = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[NebiusVm] = None
        for vm in existing:
            if vm.name == name:
                rtnval = vm
                break
        return rtnval

    def available_platforms(self, *, region_id: str,
                             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                             ) -> List[str]:
        """
            List the compute platform identifiers available in a region.

            :param region_id: The Nebius region identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of available platform identifier strings.

            :raises: :class:`SemanticError` when ``region_id`` is empty.
        """
        if region_id is None or len(region_id) == 0:
            raise SemanticError("'region_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/platforms"
        params = {"region_id": region_id}
        response = client.request(method="GET", leaf=leaf, params=params,
                                  aspects=aspects)
        raise_for_status(response=response, action="list platforms")

        payload = response.json()
        raw_items = payload.get("items", [])
        out: List[str] = []
        for entry in raw_items:
            platform_id = entry.get("id", None)
            if platform_id is not None:
                out.append(platform_id)
        rtnval = out
        return rtnval

    def launch(self, *, spec: NebiusVmSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> Tuple[NebiusVm, NebiusTaskHandle]:
        """
            Launch a virtual machine.

            When ``spec.region_id`` is set, the requested GPU platform is
            checked against the platforms available in that region; an
            unavailable platform raises
            :class:`NebiusAcceleratorNotAvailableError` before the launch
            request is issued.

            :param spec: The :class:`NebiusVmSpec` request payload.
            :param aspects: Behaviour control for the call.

            :returns: A tuple of the :class:`NebiusVm` record and the
                :class:`NebiusTaskHandle` tracking the launch.

            :raises: :class:`NebiusAcceleratorNotAvailableError` when the
                GPU platform is unavailable in the chosen region.
        """
        if spec.region_id is not None and len(spec.region_id) > 0:
            available = self.available_platforms(region_id=spec.region_id,
                                                  aspects=aspects)
            if spec.platform not in available:
                err_msg_lines = [
                    "Requested GPU platform is unavailable in the region."
                ]
                err_msg_lines.append("PLATFORM: {}".format(spec.platform))
                err_msg_lines.append("REGION: {}".format(spec.region_id))
                err_msg_lines.append(
                    "AVAILABLE: {}".format(", ".join(sorted(available)))
                )
                err_msg = os.linesep.join(err_msg_lines)
                raise NebiusAcceleratorNotAvailableError(err_msg)

        client = self.client
        body: Dict[str, Any] = {
            "parent_id": spec.parent_id,
            "name": spec.name,
            "platform": spec.platform,
            "preset": spec.preset,
            "subnet_id": spec.subnet_id,
            "image_id": spec.image_id,
        }
        if spec.ssh_key_ids is not None:
            body["ssh_key_ids"] = spec.ssh_key_ids
        if spec.placement_group_id is not None:
            body["placement_group_id"] = spec.placement_group_id
        if spec.metadata is not None:
            body["metadata"] = spec.metadata
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/instances",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="launch vm")
        payload = response.json()

        vm = NebiusVm.from_dict(payload.get("resource", payload))
        handle = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=payload), client=client,
        )
        rtnval = (vm, handle)
        return rtnval

    def power_on(self, *, vm_id: str,
                 aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                 ) -> NebiusTaskHandle:
        """
            Power a VM on.

            :param vm_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the power-on.

            :raises: :class:`SemanticError` when ``vm_id`` is empty.
        """
        rtnval = self._power_action(vm_id=vm_id, action="start",
                                    aspects=aspects)
        return rtnval

    def power_off(self, *, vm_id: str,
                  aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                  ) -> NebiusTaskHandle:
        """
            Power a VM off.

            :param vm_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the power-off.

            :raises: :class:`SemanticError` when ``vm_id`` is empty.
        """
        rtnval = self._power_action(vm_id=vm_id, action="stop",
                                    aspects=aspects)
        return rtnval

    def _power_action(self, *, vm_id: str, action: str,
                      aspects: AspectsNebius) -> NebiusTaskHandle:
        """
            Issue a power action against a VM.

            :param vm_id: The Nebius VM identifier.
            :param action: The power action sub-path (``start``/``stop``).
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the action.

            :raises: :class:`SemanticError` when ``vm_id`` is empty.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "instances", vm_id, action])
        response = client.request(method="POST", leaf=leaf, aspects=aspects)
        raise_for_status(response=response,
                         action="power {} vm".format(action))
        handle = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=response.json()),
            client=client,
        )
        rtnval = handle
        return rtnval

    def terminate(self, *, vm_id: str,
                  aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                  ) -> Optional[NebiusTaskHandle]:
        """
            Terminate a VM.  A 404 is treated as already-terminated and
            yields ``None`` (idempotent terminate).

            :param vm_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the terminate,
                or ``None`` when the VM was already absent.

            :raises: :class:`SemanticError` when ``vm_id`` is empty.
        """
        if vm_id is None or len(vm_id) == 0:
            raise SemanticError("'vm_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "instances", vm_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            rtnval: Optional[NebiusTaskHandle] = None
            return rtnval

        raise_for_status(response=response, action="terminate vm")
        rtnval = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=response.json()),
            client=client,
        )
        return rtnval
