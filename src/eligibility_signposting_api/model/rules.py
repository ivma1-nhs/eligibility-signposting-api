from __future__ import annotations

from typing import NewType

from pydantic import BaseModel, Field

Campaign = NewType("Campaign", str)
BucketName = NewType("BucketName", str)


class IterationCohort(BaseModel):
    cohort_label: str | None = Field(None, alias="CohortLabel")
    priority: int | None = Field(None, alias="Priority")

    model_config = {"populate_by_name": True}


class IterationRule(BaseModel):
    type: str | None = Field(None, alias="Type")
    name: str | None = Field(None, alias="Name")
    description: str | None = Field(None, alias="Description")
    priority: int | None = Field(None, alias="Priority")
    attribute_level: str | None = Field(None, alias="AttributeLevel")
    attribute_name: str | None = Field(None, alias="AttributeName")
    operator: str | None = Field(None, alias="Operator")
    comparator: str | None = Field(None, alias="Comparator")
    attribute_target: str | None = Field(None, alias="AttributeTarget")
    comms_routing: str | None = Field(None, alias="CommsRouting")

    model_config = {"populate_by_name": True}


class Iteration(BaseModel):
    id: str = Field(..., alias="ID")
    default_comms_routing: str | None = Field(None, alias="DefaultCommsRouting")
    version: int | None = Field(None, alias="Version")
    name: str | None = Field(None, alias="Name")
    iteration_date: str | None = Field(None, alias="IterationDate")
    iteration_number: int | None = Field(None, alias="IterationNumber")
    comms_type: str | None = Field(None, alias="CommsType")
    approval_minimum: int | None = Field(None, alias="ApprovalMinimum")
    approval_maximum: int | None = Field(None, alias="ApprovalMaximum")
    type: str | None = Field(None, alias="Type")
    iteration_cohorts: list[IterationCohort] | None = Field(None, alias="IterationCohorts")
    iteration_rules: list[IterationRule] | None = Field(None, alias="IterationRules")

    model_config = {"populate_by_name": True}


class CampaignConfig(BaseModel):
    id: str = Field(..., alias="ID")
    version: int = Field(..., alias="Version")
    name: str = Field(..., alias="Name")
    type: str | None = Field(None, alias="Type")
    target: str | None = Field(None, alias="Target")
    manager: str | None = Field(None, alias="Manager")
    approver: str | None = Field(None, alias="Approver")
    reviewer: str | None = Field(None, alias="Reviewer")
    iteration_frequency: str | None = Field(None, alias="IterationFrequency")
    iteration_type: str | None = Field(None, alias="IterationType")
    iteration_time: str | None = Field(None, alias="IterationTime")
    default_comms_routing: str | None = Field(None, alias="DefaultCommsRouting")
    start_date: str | None = Field(None, alias="StartDate")
    end_date: str | None = Field(None, alias="EndDate")
    approval_minimum: int | None = Field(None, alias="ApprovalMinimum")
    approval_maximum: int | None = Field(None, alias="ApprovalMaximum")
    iterations: list[Iteration] | None = Field(None, alias="Iterations")

    model_config = {"populate_by_name": True}


class Rules(BaseModel):
    campaign_config: CampaignConfig = Field(..., alias="CampaignConfig")

    model_config = {"populate_by_name": True}
