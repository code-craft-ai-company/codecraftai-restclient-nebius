"""
    .. module:: sshkeysgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`SshKeysGroup` api group
                   exposing the Nebius SSH-key endpoints.

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
from automojo.interop.nebius.model.nebiussshkey import NebiusSshKey


class SshKeysGroup(RestApiGroup):
    """
        :class:`SshKeysGroup` exposes the Nebius SSH-key lifecycle —
        register (idempotent by name), list, and delete (no-op on an
        unknown id).
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusSshKey]:
        """
            List every registered SSH key.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusSshKey` models.
        """
        client = self.client
        leaf = "/v1/ssh-keys"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list ssh keys")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusSshKey] = []
        for entry in raw_items:
            out.append(NebiusSshKey.from_dict(entry))
        rtnval = out
        return rtnval

    def find_by_name(self, *, name: str,
                     aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                     ) -> Optional[NebiusSshKey]:
        """
            Find a registered SSH key by name.

            :param name: The SSH-key name to match.
            :param aspects: Behaviour control for the call.

            :returns: The matching :class:`NebiusSshKey`, or ``None``.
        """
        existing = self.list(aspects=aspects)
        rtnval: Optional[NebiusSshKey] = None
        for key in existing:
            if key.name == name:
                rtnval = key
                break
        return rtnval

    def register(self, *, name: str, public_key: str,
                 aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                 ) -> NebiusSshKey:
        """
            Register an SSH key idempotently.

            An existing key of the same name is returned unchanged.

            :param name: The name to register the key under.
            :param public_key: The OpenSSH-format public-key material.
            :param aspects: Behaviour control for the call.

            :returns: The created or pre-existing :class:`NebiusSshKey`.

            :raises: :class:`SemanticError` when ``name`` is empty.
        """
        if name is None or len(name) == 0:
            raise SemanticError("'name' must be a non-empty string.")

        existing = self.find_by_name(name=name, aspects=aspects)
        if existing is not None:
            rtnval = existing
            return rtnval

        client = self.client
        body: Dict[str, Any] = {"name": name, "public_key": public_key}
        response = client.request(method="POST", leaf="/v1/ssh-keys",
                                  json_body=body, aspects=aspects)
        raise_for_status(response=response, action="register ssh key")
        rtnval = NebiusSshKey.from_dict(response.json())
        return rtnval

    def delete(self, *, key_id: str,
               aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Delete an SSH key.  A 404 is treated as already-removed.

            :param key_id: The Nebius SSH-key identifier.
            :param aspects: Behaviour control for the call.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``key_id`` is empty.
        """
        if key_id is None or len(key_id) == 0:
            raise SemanticError("'key_id' must be a non-empty string.")

        client = self.client
        leaf = compose_leaf(parts=["v1", "ssh-keys", key_id])
        response = client.request(method="DELETE", leaf=leaf, aspects=aspects)

        if is_not_found(response=response):
            return
        raise_for_status(response=response, action="delete ssh key")
        return
