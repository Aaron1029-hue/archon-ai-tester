"""
Core data models for the Archon Agent Tester.
"""
from enum import Enum
from typing import Dict, List, Optional, Union
from datetime import datetime

from pydantic import BaseModel, Field, validator


class TestStatus(str, Enum):
    """Test status enum."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestType(str, Enum):
    """Types of tests that can be run."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SAFETY = "safety"
    CUSTOM = "custom"


class TestCase(BaseModel):
    """
    Definition of a test case for an AI agent.
    """
    id: str
    name: str
    description: str
    test_type: TestType
    inputs: Dict[str, Union[str, List[str], Dict]]
    expected_outputs: Optional[Dict[str, Union[str, List[str], Dict]]] = None
    evaluation_criteria: Dict[str, Union[str, float, Dict]]
    tags: List[str] = Field(default_factory=list)
    timeout: int = 30
    
    @validator("evaluation_criteria")
    def validate_criteria(cls, v):
        """Ensure evaluation criteria are valid."""
        if not v:
            raise ValueError("At least one evaluation criterion must be provided")
        return v


class TestResult(BaseModel):
    """
    Result of a test case execution.
    """
    test_case_id: str
    agent_id: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    inputs: Dict
    actual_outputs: Optional[Dict] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    logs: List[str] = Field(default_factory=list)
    
    @validator("end_time", always=True)
    def set_end_time(cls, v, values):
        """Set end_time to now if status is not pending or running."""
        if v is None and values.get("status") not in [TestStatus.PENDING, TestStatus.RUNNING]:
            return datetime.now()
        return v
    
    @validator("duration_ms", always=True)
    def calculate_duration(cls, v, values):
        """Calculate duration based on start and end time."""
        if v is None and values.get("end_time") and values.get("start_time"):
            start = values.get("start_time")
            end = values.get("end_time")
            if end and start:
                return int((end - start).total_seconds() * 1000)
        return v


class TestSuite(BaseModel):
    """
    A collection of test cases.
    """
    id: str
    name: str
    description: str
    test_cases: List[str]  # List of test case IDs
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TestRun(BaseModel):
    """
    A complete test run with multiple test results.
    """
    id: str
    agent_id: str
    test_suite_id: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[str] = Field(default_factory=list)  # List of test result IDs
    summary: Dict[str, int] = Field(default_factory=dict)
    
    @validator("summary", always=True)
    def calculate_summary(cls, v, values):
        """Calculate summary statistics if not provided."""
        if not v and values.get("results"):
            # This would typically be filled in by the test runner
            return {
                "total": len(values.get("results", [])),
                "pending": 0,
                "passed": 0,
                "failed": 0,
                "error": 0,
                "skipped": 0,
            }
        return v