"""
Custom exceptions for the Archon Agent Tester.
"""


class ArchonAgentTesterError(Exception):
    """Base exception for all Archon Agent Tester errors."""
    pass


class ConfigurationError(ArchonAgentTesterError):
    """Raised when there is an error in the configuration."""
    pass


class ArchonAPIError(ArchonAgentTesterError):
    """Raised when there is an error with the Archon API."""
    pass


class OpenRouterAPIError(ArchonAgentTesterError):
    """Raised when there is an error with the OpenRouter API."""
    pass


class TestCaseNotFoundError(ArchonAgentTesterError):
    """Raised when a test case is not found."""
    pass


class TestSuiteNotFoundError(ArchonAgentTesterError):
    """Raised when a test suite is not found."""
    pass


class AgentNotFoundError(ArchonAgentTesterError):
    """Raised when an agent is not found."""
    pass


class TestExecutionError(ArchonAgentTesterError):
    """Raised when there is an error executing a test."""
    pass


class EvaluationError(ArchonAgentTesterError):
    """Raised when there is an error evaluating test results."""
    pass


class ReportGenerationError(ArchonAgentTesterError):
    """Raised when there is an error generating a report."""
    pass