"""
    .. module:: projectsgroup
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Module that contains the :class:`ProjectsGroup` api group
                   exposing the Nebius project-enumeration endpoint.

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
from ccai.restclient.nebius.model.nebiusproject import NebiusProject


class ProjectsGroup(RestApiGroup):
    """
        :class:`ProjectsGroup` exposes the Nebius project enumeration
        endpoint.  Projects are the apex parent-id used to anchor every
        other resource.
    """

    BASE_LEAF = "/v1"

    def list(self, *,
             aspects: AspectsNebius = DEFAULT_NEBIUS_ASPECTS
             ) -> List[NebiusProject]:
        """
            List every project visible to the credential.

            :param aspects: Behaviour control for the call.

            :returns: A list of :class:`NebiusProject` models.
        """
        client = self.client
        leaf = "/v1/projects"

        def _fetch(cursor: Optional[str]) -> Dict[str, Any]:
            params: Dict[str, str] = {"page_size": str(aspects.page_size)}
            if cursor is not None:
                params["page_token"] = cursor
            response = client.request(method="GET", leaf=leaf,
                                      params=params, aspects=aspects)
            raise_for_status(response=response, action="list projects")
            rtnval = response.json()
            return rtnval

        raw_items = collect_pages(fetch_page=_fetch)
        out: List[NebiusProject] = []
        for entry in raw_items:
            out.append(NebiusProject.from_dict(entry))
        rtnval = out
        return rtnval
