"""
    .. module:: disksgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`DisksGroup` api group
                   exposing the Nebius disk lifecycle endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, List, Optional, Tuple

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from automojo.restclient.nebius.nebiusurl import compose_leaf
from automojo.restclient.nebius.apigroups.groupsupport import (
    collect_pages, is_not_found, raise_for_status
)
from automojo.restclient.nebius.model.nebiusdisk import NebiusDisk
from automojo.restclient.nebius.model.nebiustaskhandle import NebiusTaskHandle
from automojo.restclient.nebius.specs.nebiusdiskspec import NebiusDiskSpec


def _operation_id_of(*, payload: Dict[str, Any]) -> str:
    """
        Extract the operation id from an async-call response payload.

        Nebius async calls return an operation envelope carrying an
        ``operation_id`` (or ``id``); a synchronous resource payload
        carries its own ``id``.

        :param payload: The response JSON payload.

        :returns: The operation identifier string.

        :raises: :class:`SemanticError` when no operation id is present.
    """
    op_id = payload.get("operation_id", None)
    if op_id is None:
        operation = payload.get("operation", None)
        if isinstance(operation, dict):
            op_id = operation.get("id", None)
    if op_id is None:
        op_id = payload.get("id", None)
    if op_id is None or len(str(op_id)) == 0:
        raise SemanticError(
            "Nebius async response did not carry an operation id."
        )
    rtnval = str(op_id)
    return rtnval


class DisksGroup(RestApiGroup):
    """
        :class:`DisksGroup` exposes the Nebius block-storage disk lifecycle.
        Create / attach / detach are async — each returns a
        :class:`NebiusTaskHandle` alongside the typed model.  Delete is a
        no-op on an unknown id.
    """

    BASE_LEAF = "/v1"

    def list(self, *, project_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusDisk]:
        """
            List every disk anchored to a project.

            :param project_id: The Nebius project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusDisk` models.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/disks"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "parent_id": project_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list disks")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusDisk] = []
        for entry in raw_items:
            out.append(NebiusDisk.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, project_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusDisk]:
        """
            Find a disk by name within a project.

            :param project_id: The Nebius project identifier.
            :param name: The disk name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusDisk`, or ``None``.
        """
        existing = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[NebiusDisk] = None
        for disk in existing:
            if disk.name == name:
                rtnval = disk
                break
        return rtnval

    def create(self, *, spec: NebiusDiskSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> Tuple[NebiusDisk, NebiusTaskHandle]:
        """
            Create a disk.

            :param spec: The :class:`NebiusDiskSpec` request payload.
            :param aspects: Behaviour control for the call.

            :returns: A tuple of the :class:`NebiusDisk` record and the
                :class:`NebiusTaskHandle` tracking creation.
        """
        client = self.client
        body: Dict[str, Any] = {
            "parent_id": spec.parent_id,
            "name": spec.name,
            "size_bytes": spec.size_bytes,
            "type": spec.type,
        }
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/disks",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create disk")
        payload = response.json()

        disk = NebiusDisk.from_dict(payload.get("resource", payload))
        handle = NebiusTaskHandle(operation_id=_operation_id_of(payload=payload),
                                  client=client)
        rtnval = (disk, handle)
        return rtnval

    def attach(self, *, disk_id: str, instance_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusTaskHandle:
        """
            Attach a disk to an instance.

            :param disk_id: The Nebius disk identifier.
            :param instance_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the attach.

            :raises: :class:`SemanticError` when an identifier is empty.
        """
        if disk_id is None or len(disk_id) == 0:
            raise SemanticError("'disk_id' must be a non-empty string.")
        if instance_id is None or len(instance_id) == 0:
            raise SemanticError("'instance_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "disks", disk_id, "attach"])
        body: Dict[str, Any] = {"instance_id": instance_id}
        response = client.request(method="POST", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response, action="attach disk")
        handle = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=response.json()),
            client=client,
        )
        rtnval = handle
        return rtnval

    def detach(self, *, disk_id: str, instance_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusTaskHandle:
        """
            Detach a disk from an instance.

            :param disk_id: The Nebius disk identifier.
            :param instance_id: The Nebius VM identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusTaskHandle` tracking the detach.

            :raises: :class:`SemanticError` when an identifier is empty.
        """
        if disk_id is None or len(disk_id) == 0:
            raise SemanticError("'disk_id' must be a non-empty string.")
        if instance_id is None or len(instance_id) == 0:
            raise SemanticError("'instance_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "disks", disk_id, "detach"])
        body: Dict[str, Any] = {"instance_id": instance_id}
        response = client.request(method="POST", leaf=leaf, json_body=body,
                                  aspects=aspects)
        raise_for_status(response=response, action="detach disk")
        handle = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=response.json()),
            client=client,
        )
        rtnval = handle
        return rtnval

    def delete(self, *, disk_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a disk.  A 404 is treated as already-removed.

            :param disk_id: The Nebius disk identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``disk_id`` is empty.
        """
        if disk_id is None or len(disk_id) == 0:
            raise SemanticError("'disk_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "disks", disk_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete disk")
        return
