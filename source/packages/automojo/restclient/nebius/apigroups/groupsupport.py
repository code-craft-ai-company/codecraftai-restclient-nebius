"""
    .. module:: groupsupport
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains shared helpers for the Nebius api
                   groups — HTTP status reclassification and cursor paging.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


import os

from typing import Any, Callable, Dict, Iterator, List, Optional

from requests import Response

from automojo.errors.exceptions import SemanticError

from automojo.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusAuthenticationError
)


def raise_for_status(*, response: Response, action: str) -> None:
    """
        Reclassify a non-success Nebius HTTP response into a typed error.

        A 2xx is a no-op.  401/403 reclassify into
        :class:`NebiusAuthenticationError`.  Any other non-2xx code raises
        a :class:`SemanticError` with the response body for context.

        :param response: The :class:`Response` to inspect.
        :param action: Short description of the attempted action, used in
            the error message.

        :returns: ``None``.

        :raises: :class:`NebiusAuthenticationError`, :class:`SemanticError`.
    """
    status = response.status_code
    if 200 <= status < 300:
        return

    if status in (401, 403):
        err_msg_lines = ["Nebius rejected an authenticated request."]
        err_msg_lines.append("ACTION: {}".format(action))
        err_msg_lines.append("STATUS: {}".format(status))
        err_msg_lines.append("RESPONSE:")
        err_msg_lines.append(response.text)
        err_msg = os.linesep.join(err_msg_lines)
        raise NebiusAuthenticationError(err_msg)

    err_msg_lines = ["Nebius API call failed."]
    err_msg_lines.append("ACTION: {}".format(action))
    err_msg_lines.append("STATUS: {}".format(status))
    err_msg_lines.append("RESPONSE:")
    err_msg_lines.append(response.text)
    err_msg = os.linesep.join(err_msg_lines)
    raise SemanticError(err_msg)


def is_not_found(*, response: Response) -> bool:
    """
        Return whether a response indicates a missing resource.

        :param response: The :class:`Response` to inspect.

        :returns: ``True`` when the status code is 404.
    """
    rtnval = response.status_code == 404
    return rtnval


def iter_pages(*, fetch_page: Callable[[Optional[str]], Dict[str, Any]],
               items_field: str = "items",
               cursor_field: str = "next_page_token") -> Iterator[Dict[str, Any]]:
    """
        Traverse a cursor-paginated Nebius list endpoint.

        :param fetch_page: Callable accepting the current page token
            (``None`` on the first call) and returning a page dict.
        :param items_field: Name of the field holding the item list.
        :param cursor_field: Name of the field holding the next page token;
            an empty or absent value terminates traversal.

        :returns: An iterator over the items across every page.

        :raises: :class:`SemanticError` when a page omits the items field.
    """
    cursor: Optional[str] = None
    while True:
        page = fetch_page(cursor)
        if items_field not in page:
            err_msg_lines = ["Nebius list page missing the items field."]
            err_msg_lines.append("FIELD: {}".format(items_field))
            err_msg = os.linesep.join(err_msg_lines)
            raise SemanticError(err_msg)

        items = page[items_field]
        if items is None:
            items = []
        for item in items:
            yield item

        cursor = page.get(cursor_field, None)
        if cursor is None or len(cursor) == 0:
            break
    return


def collect_pages(*, fetch_page: Callable[[Optional[str]], Dict[str, Any]],
                  items_field: str = "items",
                  cursor_field: str = "next_page_token"
                  ) -> List[Dict[str, Any]]:
    """
        Collect every item from a cursor-paginated Nebius list endpoint.

        :param fetch_page: Callable accepting the current page token.
        :param items_field: Name of the field holding the item list.
        :param cursor_field: Name of the field holding the next page token.

        :returns: A list of all item dicts across every page.
    """
    out: List[Dict[str, Any]] = []
    for item in iter_pages(fetch_page=fetch_page, items_field=items_field,
                           cursor_field=cursor_field):
        out.append(item)
    rtnval = out
    return rtnval
