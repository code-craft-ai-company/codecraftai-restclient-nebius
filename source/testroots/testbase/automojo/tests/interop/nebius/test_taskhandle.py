"""
    .. module:: test_taskhandle
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Tests for NebiusTaskHandle terminal-state correctness.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import pytest
import requests_mock as rm_module

from automojo.errors.exceptions import SemanticError

from automojo.interop.nebius.model.nebiustaskhandle import NebiusTaskHandle

from automojo.tests.interop.nebius.testsupport import (
    TEST_BASE, make_client, register_token_exchange
)


def test_task_handle_rejects_empty_operation_id():
    """
        NebiusTaskHandle construction rejects an empty operation id.
    """
    client = make_client()
    with pytest.raises(SemanticError):
        NebiusTaskHandle(operation_id="", client=client)
    return


def test_wait_reaches_done_after_running_states():
    """
        ``wait`` polls through RUNNING states then returns the DONE
        terminal result.
    """
    client = make_client()
    handle = NebiusTaskHandle(operation_id="op-1", client=client)
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        responses = [
            {"json": {"id": "op-1", "status": "RUNNING"}},
            {"json": {"id": "op-1", "status": "RUNNING"}},
            {"json": {"id": "op-1", "status": "DONE",
                      "resource_id": "vm-99"}},
        ]
        mock.get("{}/v1/operations/op-1".format(TEST_BASE), responses)

        result = handle.wait(aspects=client.aspects)

    assert result.status == "DONE"
    assert result.resource_id == "vm-99"
    assert handle.is_done() is True
    return


def test_wait_terminates_on_failed():
    """
        ``wait`` terminates on a FAILED status.
    """
    client = make_client()
    handle = NebiusTaskHandle(operation_id="op-2", client=client)
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/operations/op-2".format(TEST_BASE),
                 json={"id": "op-2", "status": "FAILED",
                       "error": "capacity exhausted"})

        result = handle.wait(aspects=client.aspects)

    assert result.status == "FAILED"
    assert result.error == "capacity exhausted"
    return


def test_wait_times_out_when_never_terminal():
    """
        ``wait`` raises TimeoutError when the budget is exhausted before a
        terminal state is observed.
    """
    client = make_client()
    handle = NebiusTaskHandle(operation_id="op-3", client=client)
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/operations/op-3".format(TEST_BASE),
                 json={"id": "op-3", "status": "RUNNING"})

        with pytest.raises(TimeoutError):
            handle.wait(aspects=client.aspects)
    return


def test_done_flag_without_explicit_status():
    """
        A raw payload with ``done=True`` and no error normalises to DONE.
    """
    client = make_client()
    handle = NebiusTaskHandle(operation_id="op-4", client=client)
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/operations/op-4".format(TEST_BASE),
                 json={"id": "op-4", "done": True,
                       "metadata": {"resource_id": "disk-7"}})

        result = handle.wait(aspects=client.aspects)

    assert result.status == "DONE"
    assert result.resource_id == "disk-7"
    return
