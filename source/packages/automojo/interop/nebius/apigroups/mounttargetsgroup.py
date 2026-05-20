"""
    .. module:: mounttargetsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`MountTargetsGroup` api
                   group exposing the Nebius shared-filesystem mount-target
                   endpoints.

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
from automojo.interop.nebius.model.nebiusmounttarget import NebiusMountTarget
from automojo.interop.nebius.specs.nebiusmounttargetspec import (
    NebiusMountTargetSpec
)


class MountTargetsGroup(RestApiGroup):
    """
        :class:`MountTargetsGroup` exposes the Nebius shared-filesystem
        mount-target lifecycle — create (attach a filesystem to a subnet),
        list, and delete (no-op on an unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, filesystem_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusMountTarget]:
        """
            List every mount target for a shared filesystem.

            :param filesystem_id: The Nebius filesystem identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusMountTarget` models.

            :raises: :class:`SemanticError` when the identifier is empty.
        """
        if filesystem_id is None or len(filesystem_id) == 0:
            raise SemanticError(
                "'filesystem_id' must be a non-empty string."
            )

        client = self.client
        leaf = "/v1/mount-targets"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "filesystem_id": filesystem_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list mount targets")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusMountTarget] = []
        for entry in raw_items:
            out.append(NebiusMountTarget.from_dict(entry))
        rtnval = out
        return rtnval

    def create(self, *, spec: NebiusMountTargetSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> NebiusMountTarget:
        """
            Create a mount target idempotently.

            An existing mount target attaching the same filesystem to the
            same subnet is returned unchanged.

            :param spec: The :class:`NebiusMountTargetSpec` payload.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing :class:`NebiusMountTarget`.
        """
        existing_targets = self.list(filesystem_id=spec.filesystem_id,
                                     aspects=aspects)
        for target in existing_targets:
            if target.subnet_id == spec.subnet_id:
                rtnval = target
                return rtnval

        client = self.client
        body: Dict[str, Any] = {
            "filesystem_id": spec.filesystem_id,
            "subnet_id": spec.subnet_id,
        }
        if spec.mount_path is not None:
            body["mount_path"] = spec.mount_path

        response = client.request(method="POST", leaf="/v1/mount-targets",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create mount target")
        rtnval = NebiusMountTarget.from_dict(response.json())
        return rtnval

    def delete(self, *, mount_target_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a mount target.  A 404 is treated as already-removed.

            :param mount_target_id: The Nebius mount-target identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when the identifier is empty.
        """
        if mount_target_id is None or len(mount_target_id) == 0:
            raise SemanticError(
                "'mount_target_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(parts=["v1", "mount-targets", mount_target_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete mount target")
        return
