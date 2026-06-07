"""
    .. module:: imagesgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ImagesGroup` api group
                   exposing the Nebius image-catalog endpoint.

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
from ccai.restclient.nebius.model.nebiusimage import NebiusImage


class ImagesGroup(RestApiGroup):
    """
        :class:`ImagesGroup` exposes the Nebius boot-image catalog
        enumeration endpoint.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusImage]:
        """
            List every Nebius boot image.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusImage` models carrying name,
                family, version, and architecture.
        """
        client = self.client
        leaf = "/v1/images"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list images")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusImage] = []
        for entry in raw_items:
            out.append(NebiusImage.from_dict(entry))
        rtnval = out
        return rtnval
