"""
    .. module:: nebiusclient
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`NebiusClient` REST client
                   for the Nebius IaaS GPU-cloud API.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import json
import os
import time

from typing import Any, Dict, List, Optional, Union

from requests import Response, Session

from automojo.errors.exceptions import ConfigurationError, SemanticError

from automojo.credentials.basecredential import BaseCredential
from automojo.credentials.nebiusserviceaccountcredential import (
    NebiusServiceAccountCredential
)

from automojo.restclient.base.restclientbase import RestClientBase

from automojo.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from automojo.restclient.nebius.nebiusurl import compose_leaf
from automojo.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusAuthenticationError
)
from automojo.restclient.nebius.model.nebiusoperationresult import (
    NebiusOperationResult
)
from automojo.restclient.nebius.apigroups.projectsgroup import ProjectsGroup
from automojo.restclient.nebius.apigroups.regionsgroup import RegionsGroup
from automojo.restclient.nebius.apigroups.imagesgroup import ImagesGroup
from automojo.restclient.nebius.apigroups.vpcsgroup import VpcsGroup
from automojo.restclient.nebius.apigroups.subnetsgroup import SubnetsGroup
from automojo.restclient.nebius.apigroups.securitygroupsgroup import (
    SecurityGroupsGroup
)
from automojo.restclient.nebius.apigroups.sshkeysgroup import SshKeysGroup
from automojo.restclient.nebius.apigroups.disksgroup import DisksGroup
from automojo.restclient.nebius.apigroups.placementgroupsgroup import (
    PlacementGroupsGroup
)
from automojo.restclient.nebius.apigroups.vmsgroup import VmsGroup
from automojo.restclient.nebius.apigroups.filesystemsgroup import FilesystemsGroup
from automojo.restclient.nebius.apigroups.mounttargetsgroup import (
    MountTargetsGroup
)
from automojo.restclient.nebius.apigroups.tagsgroup import TagsGroup
from automojo.restclient.nebius.apigroups.operationsgroup import OperationsGroup


NEBIUS_API_HOST = "api.nebius.cloud"

# Lifetime of a minted access token in seconds; the token is re-minted when
# fewer than `aspects.token_refresh_margin_seconds` remain.
_ACCESS_TOKEN_LIFETIME_SECONDS = 3600


class NebiusClient(RestClientBase):
    """
        :class:`NebiusClient` is the typed, aspect-driven REST client for the
        Nebius IaaS GPU-cloud API.  It is built on :class:`RestClientBase`.

        Nebius authenticates with a service-account JWT which is exchanged
        for a short-lived access token; the client re-mints the token
        transparently when it nears expiry.  The API surface is exposed
        through api groups (``projects``, ``regions``, ``images``, ``vpcs``,
        ``subnets``, ``security_groups``, ``ssh_keys``, ``disks``,
        ``placement_groups``, ``vms``, ``filesystems``, ``mount_targets``,
        ``tags``, ``operations``).

        All HTTP behaviour is carried by :class:`AspectsNebius`; no
        behaviour-modifying decorators are used.
    """

    def __init__(self, *, credential: BaseCredential,
                 host: str = NEBIUS_API_HOST,
                 aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> None:
        """
            Initialize the Nebius REST client.

            :param credential: A :class:`NebiusServiceAccountCredential`.
            :param host: Override host name for the REST endpoint.
            :param aspects: Default :class:`AspectsNebius` applied when a
                call omits an explicit aspects argument.

            :returns: ``None``.

            :raises: :class:`ConfigurationError` when ``credential`` is not a
                :class:`NebiusServiceAccountCredential` or is missing
                required fields.
        """
        if not isinstance(credential, NebiusServiceAccountCredential):
            err_msg_lines = [
                "NebiusClient requires a NebiusServiceAccountCredential."
            ]
            err_msg_lines.append(
                "EXPECTED: NebiusServiceAccountCredential"
            )
            err_msg_lines.append(
                "FOUND: {}".format(type(credential).__name__)
            )
            err_msg = os.linesep.join(err_msg_lines)
            raise ConfigurationError(err_msg)

        if credential.token is None or len(credential.token) == 0:
            raise ConfigurationError(
                "NebiusClient requires a credential carrying a non-empty "
                "service-account token."
            )

        super().__init__(host=host, credential=credential, aspects=aspects)

        self._access_token: Optional[str] = None
        self._access_token_expiry: float = 0.0

        self._projects = ProjectsGroup(self)
        self._regions = RegionsGroup(self)
        self._images = ImagesGroup(self)
        self._vpcs = VpcsGroup(self)
        self._subnets = SubnetsGroup(self)
        self._security_groups = SecurityGroupsGroup(self)
        self._ssh_keys = SshKeysGroup(self)
        self._disks = DisksGroup(self)
        self._placement_groups = PlacementGroupsGroup(self)
        self._vms = VmsGroup(self)
        self._filesystems = FilesystemsGroup(self)
        self._mount_targets = MountTargetsGroup(self)
        self._tags = TagsGroup(self)
        self._operations = OperationsGroup(self)
        return

    # ------------------------------------------------------------------
    # API group accessors
    # ------------------------------------------------------------------

    @property
    def projects(self) -> ProjectsGroup:
        """
            The projects api group.

            :returns: The :class:`ProjectsGroup` instance.
        """
        rtnval = self._projects
        return rtnval

    @property
    def regions(self) -> RegionsGroup:
        """
            The regions api group.

            :returns: The :class:`RegionsGroup` instance.
        """
        rtnval = self._regions
        return rtnval

    @property
    def images(self) -> ImagesGroup:
        """
            The images api group.

            :returns: The :class:`ImagesGroup` instance.
        """
        rtnval = self._images
        return rtnval

    @property
    def vpcs(self) -> VpcsGroup:
        """
            The vpcs api group.

            :returns: The :class:`VpcsGroup` instance.
        """
        rtnval = self._vpcs
        return rtnval

    @property
    def subnets(self) -> SubnetsGroup:
        """
            The subnets api group.

            :returns: The :class:`SubnetsGroup` instance.
        """
        rtnval = self._subnets
        return rtnval

    @property
    def security_groups(self) -> SecurityGroupsGroup:
        """
            The security-groups api group.

            :returns: The :class:`SecurityGroupsGroup` instance.
        """
        rtnval = self._security_groups
        return rtnval

    @property
    def ssh_keys(self) -> SshKeysGroup:
        """
            The ssh-keys api group.

            :returns: The :class:`SshKeysGroup` instance.
        """
        rtnval = self._ssh_keys
        return rtnval

    @property
    def disks(self) -> DisksGroup:
        """
            The disks api group.

            :returns: The :class:`DisksGroup` instance.
        """
        rtnval = self._disks
        return rtnval

    @property
    def placement_groups(self) -> PlacementGroupsGroup:
        """
            The placement-groups api group.

            :returns: The :class:`PlacementGroupsGroup` instance.
        """
        rtnval = self._placement_groups
        return rtnval

    @property
    def vms(self) -> VmsGroup:
        """
            The vms api group.

            :returns: The :class:`VmsGroup` instance.
        """
        rtnval = self._vms
        return rtnval

    @property
    def filesystems(self) -> FilesystemsGroup:
        """
            The filesystems api group.

            :returns: The :class:`FilesystemsGroup` instance.
        """
        rtnval = self._filesystems
        return rtnval

    @property
    def mount_targets(self) -> MountTargetsGroup:
        """
            The mount-targets api group.

            :returns: The :class:`MountTargetsGroup` instance.
        """
        rtnval = self._mount_targets
        return rtnval

    @property
    def tags(self) -> TagsGroup:
        """
            The tags api group.

            :returns: The :class:`TagsGroup` instance.
        """
        rtnval = self._tags
        return rtnval

    @property
    def operations(self) -> OperationsGroup:
        """
            The operations api group.

            :returns: The :class:`OperationsGroup` instance.
        """
        rtnval = self._operations
        return rtnval

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _resolve_access_token(self, *, aspects: AspectsNebius,
                              force_remint: bool) -> str:
        """
            Resolve a current access token, re-minting transparently when
            the cached token nears expiry.

            :param aspects: Behaviour control supplying the refresh margin.
            :param force_remint: When ``True``, discard any cached token.

            :returns: A bearer access-token string.
        """
        margin = aspects.token_refresh_margin_seconds
        now_ts = time.time()

        needs_mint = force_remint
        if self._access_token is None:
            needs_mint = True
        elif now_ts >= (self._access_token_expiry - margin):
            needs_mint = True

        if needs_mint is True:
            self._access_token = self._mint_access_token(aspects=aspects,
                                                          now=now_ts)
            self._access_token_expiry = now_ts + _ACCESS_TOKEN_LIFETIME_SECONDS

        rtnval = self._access_token
        return rtnval

    def _mint_access_token(self, *, aspects: AspectsNebius,
                           now: float) -> str:
        """
            Exchange the service-account JWT for a short-lived access token.

            :param aspects: Behaviour control for the exchange call.
            :param now: Current epoch time used to stamp the request.

            :returns: The minted access-token string.

            :raises: :class:`NebiusAuthenticationError` when the exchange
                fails or the response omits the access token.
        """
        credential: NebiusServiceAccountCredential = self._credential

        exchange_url = "{}/oauth/token".format(self._host_url)
        body = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": credential.token,
        }

        send_timeouts = (aspects.connection_timeout,
                         aspects.inactivity_timeout)

        session = Session()
        session.verify = self._verify_certificate

        response: Response = session.post(
            exchange_url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            timeout=send_timeouts,
            verify=self._verify_certificate,
        )

        if response.status_code not in (200, 201):
            err_msg_lines = [
                "Nebius rejected the service-account token exchange."
            ]
            err_msg_lines.append("STATUS: {}".format(response.status_code))
            err_msg_lines.append("RESPONSE:")
            err_msg_lines.append(response.text)
            err_msg = os.linesep.join(err_msg_lines)
            raise NebiusAuthenticationError(err_msg)

        payload = response.json()
        token_value = payload.get("access_token", None)
        if token_value is None or len(token_value) == 0:
            err_msg_lines = [
                "Nebius token exchange response missing 'access_token'."
            ]
            err_msg_lines.append("RESPONSE:")
            err_msg_lines.append(response.text)
            err_msg = os.linesep.join(err_msg_lines)
            raise NebiusAuthenticationError(err_msg)

        rtnval = token_value
        return rtnval

    def _authenticated_session(self, *, aspects: AspectsNebius,
                               force_remint: bool) -> Session:
        """
            Build a :class:`Session` carrying a current bearer token.

            :param aspects: Behaviour control.
            :param force_remint: When ``True``, force a token re-mint.

            :returns: A :class:`Session` ready to issue authenticated calls.
        """
        token = self._resolve_access_token(aspects=aspects,
                                            force_remint=force_remint)

        session = Session()
        session.verify = self._verify_certificate
        session.headers.update({
            "Authorization": "Bearer {}".format(token),
            "Accept": "application/json",
        })

        rtnval = session
        return rtnval

    # ------------------------------------------------------------------
    # Transport
    # ------------------------------------------------------------------

    def request(self, *, method: str, leaf: str,
                params: Optional[Dict[str, str]] = None,
                json_body: Optional[Union[Dict[str, Any], list]] = None,
                headers: Optional[Dict[str, str]] = None,
                aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS) -> Response:
        """
            Issue a single REST call against the Nebius API.

            The call attaches the resolved bearer token and implements a
            mint-once-then-retry behaviour on a 401 response.  An HTTP
            401/403 that persists is reclassified into
            :class:`NebiusAuthenticationError`.

            :param method: HTTP method to invoke.
            :param leaf: API leaf path beginning with ``/``.
            :param params: Optional query-string parameters.
            :param json_body: Optional dict/list serialized as the body.
            :param headers: Optional additional request headers.
            :param aspects: Behaviour control for the call.

            :returns: The :class:`Response` object from the call.

            :raises: :class:`SemanticError` when ``leaf`` is empty;
                :class:`NebiusAuthenticationError` on a persistent
                401/403.
        """
        if leaf is None or len(leaf) == 0:
            raise SemanticError("NebiusClient.request requires a non-empty "
                                "'leaf'.")

        attempt = 0
        response: Optional[Response] = None

        while True:
            session = self._authenticated_session(
                aspects=aspects, force_remint=(attempt > 0)
            )
            response = self._send(method=method, leaf=leaf, params=params,
                                  json_body=json_body, headers=headers,
                                  session=session, aspects=aspects)

            if response.status_code != 401:
                break

            if attempt >= 1:
                break

            attempt = attempt + 1

        if response.status_code in (401, 403):
            err_msg_lines = [
                "Nebius API rejected the request with an auth failure."
            ]
            err_msg_lines.append("METHOD: {}".format(method))
            err_msg_lines.append("LEAF: {}".format(leaf))
            err_msg_lines.append("STATUS: {}".format(response.status_code))
            err_msg_lines.append("RESPONSE:")
            err_msg_lines.append(response.text)
            err_msg = os.linesep.join(err_msg_lines)
            raise NebiusAuthenticationError(err_msg)

        rtnval = response
        return rtnval

    def _send(self, *, method: str, leaf: str,
              params: Optional[Dict[str, str]],
              json_body: Optional[Union[Dict[str, Any], list]],
              headers: Optional[Dict[str, str]],
              session: Session, aspects: AspectsNebius) -> Response:
        """
            Perform the actual HTTP send through the supplied session.

            :param method: HTTP method to invoke.
            :param leaf: API leaf path beginning with ``/``.
            :param params: Optional query-string parameters.
            :param json_body: Optional dict/list serialized as the body.
            :param headers: Optional additional request headers.
            :param session: The session to send through.
            :param aspects: Behaviour control.

            :returns: The :class:`Response` object from the send.
        """
        call_url = self._format_call_url(leaf)
        send_timeouts = (aspects.connection_timeout,
                         aspects.inactivity_timeout)

        body_bytes: Optional[bytes] = None
        send_headers: Dict[str, str] = {}
        if headers is not None:
            send_headers.update(headers)

        if json_body is not None:
            body_bytes = json.dumps(json_body).encode("utf-8")
            if "Content-Type" not in send_headers:
                send_headers["Content-Type"] = "application/json"

        response: Response = session.request(
            method=method, url=call_url, params=params, data=body_bytes,
            headers=send_headers, timeout=send_timeouts,
            verify=self._verify_certificate,
        )
        rtnval = response
        return rtnval

    # ------------------------------------------------------------------
    # Operations support (consumed by NebiusTaskHandle)
    # ------------------------------------------------------------------

    def get_operation(self, *, operation_id: str,
                      aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                      ) -> NebiusOperationResult:
        """
            Fetch the current status of a long-running Nebius operation.

            :param operation_id: The Nebius operation identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusOperationResult`.
        """
        rtnval = self._operations.get(operation_id=operation_id,
                                      aspects=aspects)
        return rtnval
