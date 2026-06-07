"""
    .. module:: regionsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`RegionsGroup` api group
                   exposing the Nebius region-enumeration endpoint.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from typing import Any, Dict, List, Optional

from ccai.restclient.base.restapigroup import RestApiGroup

from ccai.restclient.nebius.aspectsnebius import (
    AspectsNebius, DEFAULT_NEBIUS_ASPECTS
)
from ccai.restclient.nebius.apigroups.groupsupport import (
    collect_pages, raise_for_status
)
from ccai.restclient.nebius.model.nebiusregion import NebiusRegion


class RegionsGroup(RestApiGroup):
    """
        :class:`RegionsGroup` exposes the Nebius region enumeration
        endpoint.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusRegion]:
        """
            List every Nebius region.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusRegion` models.
        """
        client = self.client
        leaf = "/v1/regions"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list regions")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusRegion] = []
        for entry in raw_items:
            out.append(NebiusRegion.from_dict(entry))
        rtnval = out
        return rtnval
