"""
    .. module:: filesystemsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`FilesystemsGroup` api
                   group exposing the Nebius native shared-filesystem
                   endpoints.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


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
from ccai.restclient.nebius.model.nebiusfilesystem import NebiusFilesystem
from ccai.restclient.nebius.model.nebiustaskhandle import NebiusTaskHandle
from ccai.restclient.nebius.specs.nebiusfilesystemspec import (
    NebiusFilesystemSpec
)


class FilesystemsGroup(RestApiGroup):
    """
        :class:`FilesystemsGroup` exposes the Nebius native shared-filesystem
        lifecycle — create (idempotent by name, async), list, and delete
        (no-op on an unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *, project_id: str,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusFilesystem]:
        """
            List every shared filesystem anchored to a project.

            :param project_id: The Nebius project identifier.
            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusFilesystem` models.

            :raises: :class:`SemanticError` when ``project_id`` is empty.
        """
        if project_id is None or len(project_id) == 0:
            raise SemanticError("'project_id' must be a non-empty string.")

        client = self.client
        leaf = "/v1/file-storages"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {
                "parent_id": project_id,
                "page_size": str(aspects.page_size),
            }
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list filesystems")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusFilesystem] = []
        for entry in raw_items:
            out.append(NebiusFilesystem.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, project_id: str, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusFilesystem]:
        """
            Find a shared filesystem by name within a project.

            :param project_id: The Nebius project identifier.
            :param name: The filesystem name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusFilesystem`, or ``None``.
        """
        existing = self.list(project_id=project_id, aspects=aspects)
        rtnval: Optional[NebiusFilesystem] = None
        for fs in existing:
            if fs.name == name:
                rtnval = fs
                break
        return rtnval

    def get(self, *, filesystem_id: str,
            aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
            ) -> NebiusFilesystem:
        """
            Retrieve a single shared filesystem by identifier.

            :param filesystem_id: The Nebius filesystem identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusFilesystem` model.

            :raises: :class:`SemanticError` when the identifier is empty.
        """
        if filesystem_id is None or len(filesystem_id) == 0:
            raise SemanticError(
                "'filesystem_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(parts=["v1", "file-storages", filesystem_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get filesystem")
        rtnval = NebiusFilesystem.from_dict(response.json())
        return rtnval

    def create(self, *, spec: NebiusFilesystemSpec,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
               ) -> Tuple[NebiusFilesystem, NebiusTaskHandle]:
        """
            Create a shared filesystem idempotently.

            An existing filesystem of the same name in the same project is
            returned with a task handle that is already complete-pollable.

            :param spec: The :class:`NebiusFilesystemSpec` payload.
            :param aspects: Behaviour control for the call.

            :returns: A tuple of the :class:`NebiusFilesystem` record and
                a :class:`NebiusTaskHandle`.
        """
        existing = self.find_by_name(project_id=spec.parent_id,
                                     name=spec.name, aspects=aspects)
        client = self.client
        if existing is not None:
            handle = NebiusTaskHandle(operation_id=existing.id,
                                      client=client)
            rtnval = (existing, handle)
            return rtnval

        body: Dict[str, Any] = {
            "parent_id": spec.parent_id,
            "name": spec.name,
            "size_bytes": spec.size_bytes,
        }
        if spec.labels is not None:
            body["labels"] = spec.labels

        response = client.request(method="POST", leaf="/v1/file-storages",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="create filesystem")
        payload = response.json()

        fs = NebiusFilesystem.from_dict(payload.get("resource", payload))
        handle = NebiusTaskHandle(
            operation_id=_operation_id_of(payload=payload), client=client,
        )
        rtnval = (fs, handle)
        return rtnval

    def delete(self, *, filesystem_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete a shared filesystem.  A 404 is treated as
            already-removed.

            :param filesystem_id: The Nebius filesystem identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when the identifier is empty.
        """
        if filesystem_id is None or len(filesystem_id) == 0:
            raise SemanticError(
                "'filesystem_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(parts=["v1", "file-storages", filesystem_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete filesystem")
        return
