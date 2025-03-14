"""
Main module for the Archon Agent Tester.
"""
import logging
import uuid
from typing import Dict, List, Optional, Any, Union

from .core.models import TestCase, TestResult, TestSuite, TestRun, TestStatus, TestType
from .core.exceptions import (
    ArchonAgentTesterError, ConfigurationError, ArchonAPIError, OpenRouterAPIError,
    TestCaseNotFoundError, TestSuiteNotFoundError, AgentNotFoundError,
    TestExecutionError, EvaluationError, ReportGenerationError,
)
from .archon.client import ArchonClient
from .archon.adapter import ArchonAdapter
from .openrouter.client import OpenRouterClient
from .execution.engine import TestExecutionEngine
from .reporting.generators import ReportGenerator


logger = logging.getLogger(__name__)


class ArchonTester:
    """
    Main class for testing Archon agents.
    """
    
    def __init__(
        self,
        archon_api_key: Optional[str] = None,
        openrouter_api_key: Optional[str] = None,
        archon_api_base_url: Optional[str] = None,
        openrouter_api_base_url: Optional[str] = None,
    ):
        """
        Initialize the Archon tester.
        
        Args:
            archon_api_key: API key for Archon.
            openrouter_api_key: API key for OpenRouter.
            archon_api_base_url: Base URL for the Archon API.
            openrouter_api_base_url: Base URL for the OpenRouter API.
        """
        # Initialize clients
        self.archon_client = ArchonClient(
            api_key=archon_api_key,
            base_url=archon_api_base_url,
        )
        self.openrouter_client = OpenRouterClient(
            api_key=openrouter_api_key,
            base_url=openrouter_api_base_url,
        )
        
        # Initialize adapter
        self.adapter = ArchonAdapter(client=self.archon_client)
        
        # Initialize execution engine
        self.execution_engine = TestExecutionEngine(
            archon_client=self.archon_client,
            openrouter_client=self.openrouter_client,
        )
        
        # Initialize report generator
        self.report_generator = ReportGenerator()
        
        # Storage for test cases, suites, and runs
        self.test_cases: Dict[str, TestCase] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_runs: Dict[str, TestRun] = {}
    
    def test_agent(
        self,
        agent_id: str,
        test_suite: Union[str, TestSuite] = "functional",
    ) -> TestRun:
        """
        Test an agent.
        
        Args:
            agent_id: ID of the agent to test.
            test_suite: Type of tests to run or a TestSuite object.
            
        Returns:
            The test run.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            TestSuiteNotFoundError: If the test suite is not found.
            ArchonAgentTesterError: If there is an error testing the agent.
        """
        try:
            # Verify the agent exists
            agent = self.archon_client.get_agent(agent_id)
            
            # Determine the test suite
            suite_to_run: TestSuite
            if isinstance(test_suite, str):
                # Generate a test suite based on the type
                test_cases = self.adapter.generate_test_cases_for_agent(agent_id, TestType(test_suite))
                
                # Register the test cases
                for test_case in test_cases:
                    self.test_cases[test_case.id] = test_case
                    self.execution_engine.register_test_case(test_case)
                
                # Create a test suite
                suite_name = f"{agent['name']} - {test_suite.capitalize()} Tests"
                suite_to_run = self.adapter.create_test_suite(
                    agent_id=agent_id,
                    test_cases=test_cases,
                    name=suite_name,
                    description=f"{test_suite.capitalize()} tests for {agent['name']}",
                )
                
                # Register the test suite
                self.test_suites[suite_to_run.id] = suite_to_run
                self.execution_engine.register_test_suite(suite_to_run)
            else:
                # Use the provided test suite
                suite_to_run = test_suite
                
                # Ensure the test suite is registered
                if suite_to_run.id not in self.test_suites:
                    self.test_suites[suite_to_run.id] = suite_to_run
                    self.execution_engine.register_test_suite(suite_to_run)
            
            # Execute the test suite
            test_run = self.execution_engine.execute_test_suite(suite_to_run.id, agent_id)
            
            # Store the test run
            self.test_runs[test_run.id] = test_run
            
            # Update the agent with the test results
            self.adapter.update_agent_with_test_results(agent_id, test_run)
            
            return test_run
        except (AgentNotFoundError, TestSuiteNotFoundError):
            raise
        except Exception as e:
            raise ArchonAgentTesterError(f"Error testing agent {agent_id}: {str(e)}")
    
    def generate_report(
        self,
        test_run: Union[str, TestRun],
        format: str = "json",
    ) -> str:
        """
        Generate a report for a test run.
        
        Args:
            test_run: The test run ID or TestRun object.
            format: The format of the report (json, html, markdown, csv).
            
        Returns:
            The path to the generated report.
            
        Raises:
            TestRunNotFoundError: If the test run is not found.
            ReportGenerationError: If there is an error generating the report.
        """
        try:
            # Get the test run
            run_to_report: TestRun
            if isinstance(test_run, str):
                # Look up the test run by ID
                if test_run not in self.test_runs:
                    raise TestRunNotFoundError(f"Test run {test_run} not found")
                run_to_report = self.test_runs[test_run]
            else:
                # Use the provided test run
                run_to_report = test_run
                
                # Ensure the test run is registered
                if run_to_report.id not in self.test_runs:
                    self.test_runs[run_to_report.id] = run_to_report
            
            # Ensure the test suites and cases are registered with the report generator
            self.report_generator.test_cases.update(self.test_cases)
            self.report_generator.test_suites.update(self.test_suites)
            self.report_generator.test_runs[run_to_report.id] = run_to_report
            
            # Generate the report
            return self.report_generator.generate_report(run_to_report.id, format)
        except TestRunNotFoundError:
            raise
        except Exception as e:
            raise ReportGenerationError(f"Error generating report: {str(e)}")
    
    def list_available_models(self) -> List[Dict]:
        """
        List available models from OpenRouter.
        
        Returns:
            List of available models.
            
        Raises:
            OpenRouterAPIError: If there is an error with the OpenRouter API.
        """
        try:
            return self.openrouter_client.list_models()
        except Exception as e:
            raise OpenRouterAPIError(f"Error listing models: {str(e)}")
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List agents from Archon.
        
        Args:
            limit: Maximum number of agents to return.
            offset: Offset for pagination.
            
        Returns:
            List of agents.
            
        Raises:
            ArchonAPIError: If there is an error with the Archon API.
        """
        try:
            return self.archon_client.list_agents(limit=limit, offset=offset)
        except Exception as e:
            raise ArchonAPIError(f"Error listing agents: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Dict:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent.
            
        Returns:
            The agent data.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the Archon API.
        """
        try:
            return self.archon_client.get_agent(agent_id)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error getting agent {agent_id}: {str(e)}")
    
    def get_agent_metrics(self, agent_id: str) -> Dict:
        """
        Get metrics for an agent.
        
        Args:
            agent_id: ID of the agent.
            
        Returns:
            The agent metrics.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the Archon API.
        """
        try:
            return self.archon_client.get_agent_metrics(agent_id)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error getting metrics for agent {agent_id}: {str(e)}")
    
    def create_custom_test_case(
        self,
        name: str,
        description: str,
        test_type: TestType,
        inputs: Dict[str, Any],
        expected_outputs: Optional[Dict[str, Any]] = None,
        evaluation_criteria: Dict[str, Any] = None,
        tags: List[str] = None,
        timeout: int = 30,
    ) -> TestCase:
        """
        Create a custom test case.
        
        Args:
            name: Name of the test case.
            description: Description of the test case.
            test_type: Type of the test.
            inputs: Inputs for the test.
            expected_outputs: Expected outputs for the test.
            evaluation_criteria: Evaluation criteria for the test.
            tags: Tags for the test.
            timeout: Timeout for the test in seconds.
            
        Returns:
            The created test case.
        """
        # Generate a unique ID for the test case
        test_case_id = str(uuid.uuid4())
        
        # Set default evaluation criteria if not provided
        if evaluation_criteria is None:
            evaluation_criteria = {"response_not_empty": "The agent should provide a non-empty response"}
        
        # Set default tags if not provided
        if tags is None:
            tags = [test_type.value, "custom"]
        
        # Create the test case
        test_case = TestCase(
            id=test_case_id,
            name=name,
            description=description,
            test_type=test_type,
            inputs=inputs,
            expected_outputs=expected_outputs,
            evaluation_criteria=evaluation_criteria,
            tags=tags,
            timeout=timeout,
        )
        
        # Register the test case
        self.test_cases[test_case.id] = test_case
        self.execution_engine.register_test_case(test_case)
        
        return test_case
    
    def create_custom_test_suite(
        self,
        name: str,
        description: str,
        test_cases: List[TestCase],
        tags: List[str] = None,
    ) -> TestSuite:
        """
        Create a custom test suite.
        
        Args:
            name: Name of the test suite.
            description: Description of the test suite.
            test_cases: Test cases to include in the suite.
            tags: Tags for the test suite.
            
        Returns:
            The created test suite.
        """
        # Generate a unique ID for the test suite
        test_suite_id = str(uuid.uuid4())
        
        # Set default tags if not provided
        if tags is None:
            tags = ["custom"]
        
        # Create the test suite
        test_suite = TestSuite(
            id=test_suite_id,
            name=name,
            description=description,
            test_cases=[tc.id for tc in test_cases],
            tags=tags,
        )
        
        # Register the test suite
        self.test_suites[test_suite.id] = test_suite
        self.execution_engine.register_test_suite(test_suite)
        
        return test_suite