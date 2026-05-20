"""
    .. module:: operationsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`OperationsGroup` api
                   group exposing the Nebius long-running operations
                   endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Dict

from automojo.errors.exceptions import SemanticError

from automojo.restclient.base.restapigroup import RestApiGroup

from automojo.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from automojo.restclient.nebius.nebiusurl import compose_leaf
from automojo.restclient.nebius.apigroups.groupsupport import raise_for_status
from automojo.restclient.nebius.model.nebiusoperationresult import (
    NebiusOperationResult
)


# Mapping from raw Nebius operation states onto the normalised status set
# carried by NebiusOperationResult.  Unknown states map to RUNNING so a
# task handle keeps polling rather than terminating prematurely.
_RAW_STATE_MAP = {
    "PENDING": "RUNNING",
    "RUNNING": "RUNNING",
    "DONE": "DONE",
    "FAILED": "FAILED",
    "CANCELLED": "CANCELLED",
}


class OperationsGroup(RestApiGroup):
    """
        :class:`OperationsGroup` exposes the Nebius operations endpoint.
        Every async resource mutation returns an operation id;
        :class:`NebiusTaskHandle` polls this group to observe completion.
    """

    BASE_LEAF = "/v1"

    def get(self, *, operation_id: str,
            aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
            ) -> NebiusOperationResult:
        """
            Fetch the current status of a long-running operation.

            The raw Nebius payload uses a ``done`` boolean plus a textual
            state; this method normalises the state into the
            ``RUNNING/DONE/FAILED/CANCELLED`` set carried by
            :class:`NebiusOperationResult`.

            :param operation_id: The Nebius operation identifier.
            :param aspects: Behaviour control for the call.

            :returns: A :class:`NebiusOperationResult`.

            :raises: :class:`SemanticError` when ``operation_id`` is empty.
        """
        if operation_id is None or len(operation_id) == 0:
            raise SemanticError(
                "'operation_id' must be a non-empty string."
            )

        client = self.client
        leaf = compose_leaf(parts=["v1", "operations", operation_id])
        response = client.request(method="GET", leaf=leaf, aspects=aspects)
        raise_for_status(response=response, action="get operation")

        payload = response.json()
        normalised = self._normalise(payload=payload,
                                     operation_id=operation_id)
        rtnval = normalised
        return rtnval

    @staticmethod
    def _normalise(*, payload: Dict[str, Any],
                   operation_id: str) -> NebiusOperationResult:
        """
            Normalise a raw operation payload into a NebiusOperationResult.

            :param payload: The raw operation JSON payload.
            :param operation_id: The operation identifier.

            :returns: A normalised :class:`NebiusOperationResult`.
        """
        raw_state = payload.get("status", None)
        done_flag = payload.get("done", None)

        if raw_state is not None:
            status = _RAW_STATE_MAP.get(str(raw_state).upper(), "RUNNING")
        elif done_flag is True:
            error_value = payload.get("error", None)
            if error_value is not None:
                status = "FAILED"
            else:
                status = "DONE"
        else:
            status = "RUNNING"

        resource_id = payload.get("resource_id", None)
        metadata = payload.get("metadata", None)
        if resource_id is None and isinstance(metadata, dict):
            resource_id = metadata.get("resource_id", None)

        error_text = payload.get("error", None)
        if error_text is not None and not isinstance(error_text, str):
            error_text = str(error_text)

        rtnval = NebiusOperationResult(
            id=payload.get("id", operation_id),
            done=(status in ("DONE", "FAILED", "CANCELLED")),
            status=status,
            error=error_text,
            resource_id=resource_id,
            metadata=metadata,
        )
        return rtnval
