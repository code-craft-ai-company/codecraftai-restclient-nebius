"""
    .. module:: test_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Property-based tests (hypothesis) for the Nebius interop
                   client — paging traversal, URL composition, idempotent
                   retry, CIDR containment, and task-handle terminal-state
                   correctness.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


import ipaddress

import pytest
import requests_mock as rm_module

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.restclient.nebius.nebiusurl import compose_leaf
from ccai.restclient.nebius.apigroups.subnetsgroup import cidr_contained
from ccai.restclient.nebius.apigroups.groupsupport import collect_pages
from ccai.restclient.nebius.model.nebiustaskhandle import NebiusTaskHandle
from ccai.restclient.nebius.exceptions.nebiusexceptions import (
    NebiusCidrValidationError
)

from ccai.tests.restclient.nebius.testsupport import (
    TEST_BASE, make_client, register_token_exchange
)


# ----------------------------------------------------------------------
# 1. Paging cursor traversal
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 60},page_sizes=st.lists(st.integers(min_value=0, max_value=5),
                           min_size=1, max_size=8))
def test_paging_traversal_visits_every_item(page_sizes):
    """
        ``collect_pages`` visits every item across an arbitrary number of
        cursor-linked pages exactly once and in order.
    """
    expected = []
    pages = []
    counter = 0
    for index, size in enumerate(page_sizes):
        items = []
        for _ in range(size):
            items.append({"id": "item-{}".format(counter)})
            expected.append("item-{}".format(counter))
            counter = counter + 1
        page = {"items": items}
        if index < len(page_sizes) - 1:
            page["next_page_token"] = "tok-{}".format(index)
        pages.append(page)

    page_iter = iter(pages)

    def _fetch(cursor):
        rtnval = next(page_iter)
        return rtnval

    collected = collect_pages(fetch_page=_fetch)
    observed = [entry["id"] for entry in collected]
    assert observed == expected
    return


# ----------------------------------------------------------------------
# 2. URL composition — encoding + rejection
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 80},segments=st.lists(st.text(min_size=1, max_size=12),
                         min_size=1, max_size=5))
def test_compose_leaf_is_deterministic_and_segmented(segments):
    """
        ``compose_leaf`` is deterministic and produces exactly one segment
        per input part (per-segment percent-encoding prevents escapes).
    """
    first = compose_leaf(parts=list(segments))
    second = compose_leaf(parts=list(segments))
    assert first == second
    assert first.startswith("/")
    # The number of '/' separators equals the segment count because each
    # segment is individually percent-encoded (no embedded slashes survive).
    assert first.count("/") == len(segments)
    return


@given(
    constraints={"max_examples": 40},prefix=st.lists(st.text(min_size=1, max_size=6), max_size=3),
       suffix=st.lists(st.text(min_size=1, max_size=6), max_size=3))
def test_compose_leaf_rejects_empty_segment(prefix, suffix):
    """
        ``compose_leaf`` rejects an empty/None identifier with SemanticError
        regardless of surrounding valid segments.
    """
    parts = list(prefix) + [""] + list(suffix)
    with pytest.raises(SemanticError):
        compose_leaf(parts=parts)
    return


# ----------------------------------------------------------------------
# 3. Idempotent retry semantics
# ----------------------------------------------------------------------

@given(repeat=st.integers(min_value=2, max_value=6), constraints={"max_examples": 30})
def test_idempotent_create_never_posts_when_present(repeat):
    """
        Repeated ``vpcs.create`` calls against an existing VPC never POST,
        regardless of how many times the call is repeated.
    """
    from ccai.restclient.nebius.specs.nebiusvpcspec import NebiusVpcSpec

    client = make_client()
    spec = NebiusVpcSpec(parent_id="proj-1", name="vpc-x",
                         ipv4_cidr_block="10.0.0.0/16")
    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/vpcs".format(TEST_BASE),
                 json={"items": [{"id": "vpc-x-id", "name": "vpc-x",
                                  "ipv4_cidr_block": "10.0.0.0/16"}]})
        post_marker = mock.post("{}/v1/vpcs".format(TEST_BASE),
                                json={"id": "unused"})

        results = []
        for _ in range(repeat):
            results.append(client.vpcs.create(spec=spec))

        assert post_marker.called is False

    ids = {vpc.id for vpc in results}
    assert ids == {"vpc-x-id"}
    return


# ----------------------------------------------------------------------
# 4. CIDR containment
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 80},parent_prefix=st.integers(min_value=8, max_value=20),
       extra_bits=st.integers(min_value=1, max_value=8),
       host_index=st.integers(min_value=0, max_value=4))
def test_subnet_of_parent_is_contained(parent_prefix, extra_bits,
                                       host_index):
    """
        Any network carved from inside a parent network is reported as
        contained; the same network shifted out of range is not.
    """
    parent = ipaddress.ip_network("10.0.0.0/{}".format(parent_prefix))
    child_prefix = parent_prefix + extra_bits
    children = list(parent.subnets(prefixlen_diff=extra_bits))
    child = children[host_index % len(children)]

    contained = cidr_contained(parent_cidr=str(parent),
                               child_cidr=str(child))
    assert contained is True

    # A network in a disjoint address block is never contained.
    disjoint = ipaddress.ip_network("192.168.0.0/{}".format(child_prefix),
                                    strict=False)
    assert cidr_contained(parent_cidr=str(parent),
                          child_cidr=str(disjoint)) is False
    return


@given(bad=st.text(min_size=1, max_size=10), constraints={"max_examples": 30})
def test_cidr_containment_rejects_unparseable(bad):
    """
        ``cidr_contained`` raises NebiusCidrValidationError on a CIDR string
        that does not parse.
    """
    try:
        ipaddress.ip_network(bad, strict=False)
    except (TypeError, ValueError):
        with pytest.raises(NebiusCidrValidationError):
            cidr_contained(parent_cidr="10.0.0.0/16", child_cidr=bad)
    return


# ----------------------------------------------------------------------
# 5. NebiusTaskHandle.wait terminal-state correctness
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 40},running_count=st.integers(min_value=0, max_value=6),
       terminal=st.sampled_from(["DONE", "FAILED", "CANCELLED"]))
def test_wait_returns_first_terminal_state(running_count, terminal):
    """
        ``wait`` returns exactly the first terminal status observed after
        an arbitrary run of non-terminal RUNNING states.
    """
    client = make_client()
    handle = NebiusTaskHandle(operation_id="op-prop", client=client)
    responses = []
    for _ in range(running_count):
        responses.append({"json": {"id": "op-prop", "status": "RUNNING"}})
    responses.append({"json": {"id": "op-prop", "status": terminal}})

    with rm_module.Mocker() as mock:
        register_token_exchange(mock=mock)
        mock.get("{}/v1/operations/op-prop".format(TEST_BASE), responses)

        result = handle.wait(aspects=client.aspects)

    assert result.status == terminal
    assert result.done is True
    return
