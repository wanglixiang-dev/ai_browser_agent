from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: int
    goal: str
    tool: str
    input: str | dict | None = None
    expected_output: str
    status: str = "pending"
    observation: str | dict | list | None = None
    error: str | None = None


class TaskPlan(BaseModel):
    task: str
    steps: list[PlanStep] = Field(default_factory=list)


class ExecutionResult(BaseModel):
    task: str
    steps: list[PlanStep]
    final_report_path: str | None = None
    final_answer: str | None = None
    failed: bool = False
    error: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
