"""
    .. module:: test_smoke_live
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Gated live smoke test against a real Nebius API.

    This module is skipped unless ``RUN_LIVE_NEBIUS=1`` is set in the
    environment.  When enabled it requires ``NEBIUS_SA_TOKEN`` to carry a
    valid service-account JWT and exercises a read-only project enumeration.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

import pytest

from automojo.credentials.nebiusserviceaccountcredential import (
    NebiusServiceAccountCredential
)
from automojo.restclient.nebius.nebiusclient import NebiusClient


_RUN_LIVE = os.environ.get("RUN_LIVE_NEBIUS", "0") == "1"


@pytest.fixture
def live_client() -> NebiusClient:
    """
        Build a :class:`NebiusClient` from the ``NEBIUS_SA_TOKEN`` env var.

        :returns: A live-API :class:`NebiusClient`.
    """
    token = os.environ.get("NEBIUS_SA_TOKEN", None)
    if token is None or len(token) == 0:
        pytest.skip("NEBIUS_SA_TOKEN is not set.")

    credential = NebiusServiceAccountCredential(
        identifier="nebius-live", categories=["hpc-venue"], token=token,
    )
    rtnval = NebiusClient(credential=credential)
    return rtnval


@pytest.mark.skipif(not _RUN_LIVE,
                    reason="RUN_LIVE_NEBIUS != 1; live smoke test skipped.")
def test_live_list_projects(live_client) -> None:
    """
        Enumerate projects against the live Nebius API.
    """
    projects = live_client.projects.list()
    assert isinstance(projects, list)
    return
