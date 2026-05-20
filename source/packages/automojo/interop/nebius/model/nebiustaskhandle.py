"""
    .. module:: nebiustaskhandle
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`NebiusTaskHandle` class
                   used to poll Nebius long-running operations.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict, Optional

import time

from automojo.errors.exceptions import SemanticError

from automojo.interop.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from automojo.interop.nebius.model.nebiusoperationresult import (
    NebiusOperationResult
)


# Terminal operation status strings reported by the Nebius operations API.
_TERMINAL_STATUSES = frozenset({"DONE", "FAILED", "CANCELLED"})


class NebiusTaskHandle:
    """
        :class:`NebiusTaskHandle` is the typed handle returned for every
        async Nebius operation.  It implements the ``ITaskHandle`` polling
        shape — :meth:`wait` polls the operations endpoint per the supplied
        :class:`AspectsNebius` until a terminal state is reached or the
        completion budget is exhausted.

        The handle holds a back-reference to the owning client so it can
        re-issue the operation-status GET; no behaviour-modifying decorators
        are used.
    """

    def __init__(self, *, operation_id: str, client: Any) -> None:
        """
            Initialize a Nebius task handle.

            :param operation_id: The Nebius operation identifier to poll.
            :param client: The owning :class:`NebiusClient` instance.

            :returns: ``None``.

            :raises: :class:`SemanticError` when ``operation_id`` is empty.
        """
        if operation_id is None or len(operation_id) == 0:
            raise SemanticError(
                "NebiusTaskHandle requires a non-empty 'operation_id'."
            )

        self._operation_id = operation_id
        self._client = client
        self._last_result: Optional[NebiusOperationResult] = None
        return

    @property
    def operation_id(self) -> str:
        """
            The Nebius operation identifier this handle polls.

            :returns: The operation identifier string.
        """
        rtnval = self._operation_id
        return rtnval

    def task_id(self) -> str:
        """
            Return the vendor task identifier.

            :returns: The operation identifier string.
        """
        rtnval = self._operation_id
        return rtnval

    def is_done(self) -> bool:
        """
            Return whether the most recently observed status is terminal.

            Does not poll the network.

            :returns: ``True`` when the last observed status is terminal.
        """
        rtnval = False
        if self._last_result is not None:
            if self._last_result.status in _TERMINAL_STATUSES:
                rtnval = True
        return rtnval

    def poll_once(self, *,
                  aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
                  ) -> NebiusOperationResult:
        """
            Issue a single operation-status GET and return the result.

            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusOperationResult`.
        """
        result = self._client.get_operation(operation_id=self._operation_id,
                                             aspects=aspects)
        self._last_result = result
        return result

    def wait(self, *, aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> NebiusOperationResult:
        """
            Poll the operations endpoint until the operation reaches a
            terminal state or the completion budget is exhausted.

            :param aspects: Behaviour control supplying the polling interval
                and completion timeout.

            :returns: A :class:`NebiusOperationResult` describing the
                terminal state.

            :raises: :class:`SemanticError` when the aspects supply a
                non-positive interval or timeout; :class:`TimeoutError`
                when the budget is exhausted.
        """
        interval = aspects.completion_interval
        timeout = aspects.completion_timeout

        if interval <= 0:
            raise SemanticError(
                "NebiusTaskHandle.wait requires completion_interval > 0."
            )
        if timeout <= 0:
            raise SemanticError(
                "NebiusTaskHandle.wait requires completion_timeout > 0."
            )

        start = time.monotonic()
        deadline = start + timeout

        rtnval: Optional[NebiusOperationResult] = None
        while True:
            result = self.poll_once(aspects=aspects)

            if result.status in _TERMINAL_STATUSES:
                rtnval = result
                break

            now = time.monotonic()
            if now >= deadline:
                err_msg = (
                    "NebiusTaskHandle.wait timed out after {0}s for "
                    "operation {1!r} (last status {2!r})."
                ).format(timeout, self._operation_id, result.status)
                raise TimeoutError(err_msg)

            time.sleep(interval)

        return rtnval
