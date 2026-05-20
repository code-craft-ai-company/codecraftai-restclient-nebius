"""
    .. module:: testsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Shared helpers for the Nebius interop client tests.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from automojo.credentials.nebiusserviceaccountcredential import (
    NebiusServiceAccountCredential
)

from automojo.restclient.nebius.aspectsnebius import AspectsNebius
from automojo.restclient.nebius.nebiusclient import NebiusClient


TEST_HOST = "api.nebius.test"
TEST_BASE = "https://{}".format(TEST_HOST)


def make_credential() -> NebiusServiceAccountCredential:
    """
        Build a deterministic Nebius service-account credential.

        :returns: A :class:`NebiusServiceAccountCredential`.
    """
    rtnval = NebiusServiceAccountCredential(
        identifier="nebius-test", categories=["hpc-venue"],
        token="svc-account-jwt-assertion",
    )
    return rtnval


def fast_aspects() -> AspectsNebius:
    """
        Build aspects with a short polling budget for deterministic tests.

        :returns: An :class:`AspectsNebius`.
    """
    rtnval = AspectsNebius(completion_timeout=2.0, completion_interval=0.01)
    return rtnval


def make_client() -> NebiusClient:
    """
        Build a :class:`NebiusClient` bound to the test host.

        :returns: A :class:`NebiusClient`.
    """
    rtnval = NebiusClient(credential=make_credential(), host=TEST_HOST,
                          aspects=fast_aspects())
    return rtnval


def register_token_exchange(*, mock) -> None:
    """
        Register the service-account JWT exchange endpoint on a mocker.

        :param mock: A ``requests_mock`` Mocker.

        :returns: ``None``.
    """
    mock.post("{}/oauth/token".format(TEST_BASE),
              json={"access_token": "minted-access-token-001",
                    "expires_in": 3600})
    return
