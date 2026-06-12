"""
    .. module:: test_authentication
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for Nebius JWT exchange, token refresh, and HTTP
                   error reclassification.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import time

import pytest
import requests_mock as rm_module

from ccai.errors.exceptions import ConfigurationError

from ccai.credentials.basecredential import BaseCredential

from ccai.restclient.nebius.nebiusclient import NebiusClient
from ccai.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusAuthenticationError
)

from ccai.tests.restclient.nebius.testsupport import (
    TEST_BASE, TEST_HOST, fast_aspects, make_client, make_credential,
    register_token_exchange
)


def test_construction_rejects_non_nebius_credential():
    """
        A non-Nebius credential is rejected at construction time.
    """
    bogus = BaseCredential(identifier="x", categories=["other"])
    with pytest.raises(ConfigurationError):
        NebiusClient(credential=bogus, host=TEST_HOST)
    return


def test_jwt_exchange_mints_token_and_injects_bearer():
    """
        The first call exchanges the service-account JWT and injects the
        minted bearer on the resource request.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/projects".format(TEST_BASE),
                 json={"items": [{"id": "p1", "name": "proj"}]})

        projects = client.projects.list()

        history = mock.request_history
        assert history[0].path == "/oauth/token"
        resource_req = history[-1]
        auth_header = resource_req.headers.get("Authorization")
        assert auth_header == "Bearer minted-access-token-001"

    assert len(projects) == 1
    assert projects[0].id == "p1"
    return


def test_token_reused_within_lifetime():
    """
        A second call within the token lifetime does not re-mint.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/regions".format(TEST_BASE),
                 json={"items": [{"id": "r1"}]})

        client.regions.list()
        client.regions.list()

        token_calls = [r for r in mock.request_history
                       if r.path == "/oauth/token"]
        assert len(token_calls) == 1
    return


def test_token_reminted_when_expired():
    """
        When the cached token is past its refresh margin the client
        transparently re-mints it without surfacing the renewal.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/regions".format(TEST_BASE),
                 json={"items": [{"id": "r1"}]})

        client.regions.list()
        # Force the cached token to look expired.
        client._access_token_expiry = time.time() - 10.0
        client.regions.list()

        token_calls = [r for r in mock.request_history
                       if r.path == "/oauth/token"]
        assert len(token_calls) == 2
    return


def test_failed_exchange_raises_authentication_error():
    """
        A rejected token exchange raises NebiusAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        mock.post("{}/oauth/token".format(TEST_BASE), status_code=401,
                  json={"error": "invalid_grant"})
        with pytest.raises(NebiusAuthenticationError):
            client.projects.list()
    return


def test_persistent_401_reclassified():
    """
        A 401 that persists after a re-mint reclassifies into
        NebiusAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/projects".format(TEST_BASE), status_code=401,
                 json={"error": "unauthorized"})
        with pytest.raises(NebiusAuthenticationError):
            client.projects.list()
    return


def test_403_reclassified():
    """
        A 403 on a resource request reclassifies into
        NebiusAuthenticationError.
    """
    client = make_client()
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/projects".format(TEST_BASE), status_code=403,
                 json={"error": "forbidden"})
        with pytest.raises(NebiusAuthenticationError):
            client.projects.list()
    return
