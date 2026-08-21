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
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase

from ccai.errors.exceptions import SkipError


import os

from ccai.credentials.nebiusserviceaccountcredential import (
    NebiusServiceAccountCredential
)
from ccai.restclient.nebius.nebiusclient import NebiusClient


_RUN_LIVE = os.environ.get("RUN_LIVE_NEBIUS", "0") == "1"


def _build_live_client() -> NebiusClient:
    """
        Build a :class:`NebiusClient` from the ``NEBIUS_SA_TOKEN`` env var.

        :returns: A live-API :class:`NebiusClient`.
    """
    token = os.environ.get("NEBIUS_SA_TOKEN", None)
    if token is None or len(token) == 0:
        raise SkipError("NEBIUS_SA_TOKEN is not set.")

    credential = NebiusServiceAccountCredential(
        identifier="nebius-live", categories=["hpc-venue"], token=token,
    )
    rtnval = NebiusClient(credential=credential)
    return rtnval


def test_live_list_projects() -> None:
    """
        Enumerate projects against the live Nebius API.

        The client was a pytest fixture before this suite ran under
        testbase, which does not inject pytest fixtures -- the parameter
        was simply undefined, so the test errored rather than skipping.
        It is built here instead, after the gate.
    """
    if not _RUN_LIVE:
        raise SkipError("RUN_LIVE_NEBIUS != 1; live smoke test skipped.")

    live_client = _build_live_client()

    projects = live_client.projects.list()
    testbase.assert_true(isinstance(projects, list))
    return
