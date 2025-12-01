from typing import List, Union
from pydantic import BaseModel, Field, HttpUrl
from awm.models.allocation import AllocationInfo
from awm.models.tool import ToolInfo
from awm.models.deployment import DeploymentInfo
from fastapi import Request


class Page(BaseModel):
    """Page Base class for pagination"""
    from_: int = Field(..., alias="from", description="Index of the first element to return")
    limit: int = Field(..., description="Maximum number of elements to return")
    count: int = Field(..., description="Total number of elements")
    self_: HttpUrl | None = Field(None, alias="self", description="Endpoint that returned this page")
    prevPage: HttpUrl | None = Field(None, description="Endpoint that returns the previous page")
    nextPage: HttpUrl | None = Field(None, description="Endpoint that returns the next page")

    model_config = {"populate_by_name": True}

    def set_next_and_prev_pages(self, request: Request, all_nodes: bool):
        base_url = request.url.scheme + "://" + request.url.hostname + request.url.path
        if all_nodes:
            base_url += "?allNodes=true&"
        else:
            base_url += "?"
        if self.from_ + self.limit < self.count:
            self.nextPage = HttpUrl(f"{base_url}from={self.from_ + self.limit}&limit={self.limit}")
        if self.from_ > 0 and self.count > 0:
            self.prevPage = HttpUrl(f"{base_url}from={max(0, self.from_ - self.limit)}&limit={self.limit}")


class PageOfAllocations(Page):
    """Page of Allocations"""
    elements: List[AllocationInfo]


class PageOfDeployments(Page):
    """Page of Deployments"""
    elements: List[DeploymentInfo]


class PageOfTools(Page):
    """Page of Tools"""
    elements: List[ToolInfo]


class PageOfItems(Page):
    """Generic Page of any item"""
    elements: List[Union[AllocationInfo, DeploymentInfo, ToolInfo]]
