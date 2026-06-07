"""
    .. module:: nebiusurl
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains URL-composition helpers for the
                   Nebius interop client.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import List

from urllib.parse import quote

from ccai.errors.exceptions import SemanticError


def compose_leaf(*, parts: List[str]) -> str:
    """
        Compose a percent-encoded API leaf path from path segments.

        Each segment is percent-encoded individually so that an identifier
        containing reserved characters cannot escape its segment.  An
        empty or ``None`` segment is an API-misuse condition and raises a
        :class:`SemanticError`.

        :param parts: Ordered list of path segments (e.g.
            ``["v1", "vpcs", vpc_id]``).

        :returns: The composed leaf path beginning with ``/``.

        :raises: :class:`SemanticError` when ``parts`` is ``None``, empty,
            or contains an empty/``None`` segment.
    """
    if parts is None:
        raise SemanticError("compose_leaf requires a non-None 'parts' list.")
    if len(parts) == 0:
        raise SemanticError("compose_leaf requires a non-empty 'parts' list.")

    encoded: List[str] = []
    for part in parts:
        if part is None:
            raise SemanticError(
                "compose_leaf received a None path segment."
            )
        if not isinstance(part, str):
            raise SemanticError(
                "compose_leaf path segments must all be strings."
            )
        if len(part) == 0:
            raise SemanticError(
                "compose_leaf received an empty path segment."
            )
        encoded.append(quote(part, safe=""))

    rtnval = "/" + "/".join(encoded)
    return rtnval
