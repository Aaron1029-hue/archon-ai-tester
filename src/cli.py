"""
Command-line interface for the Archon Agent Tester.
"""
import logging
import sys
import os
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

from .archon_agent_tester import ArchonTester
from .core.models import TestType
from .core.exceptions import ArchonAgentTesterError


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("archon_agent_tester")

# Create Typer app
app = typer.Typer(help="Archon Agent Tester CLI")
console = Console()


@app.command()
def test(
    agent_id: str = typer.Argument(..., help="ID of the agent to test"),
    test_type: str = typer.Option("functional", help="Type of tests to run"),
    report_format: str = typer.Option("html", help="Format for the test report"),
    archon_api_key: Optional[str] = typer.Option(None, help="Archon API key"),
    openrouter_api_key: Optional[str] = typer.Option(None, help="OpenRouter API key"),
):
    """
    Test an Archon agent.
    """
    try:
        # Get API keys from environment if not provided
        archon_key = archon_api_key or os.environ.get("ARCHON_API_KEY")
        openrouter_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        
        if not archon_key:
            console.print("[bold red]Error:[/bold red] Archon API key is required")
            sys.exit(1)
        
        if not openrouter_key:
            console.print("[bold red]Error:[/bold red] OpenRouter API key is required")
            sys.exit(1)
        
        # Initialize the tester
        tester = ArchonTester(
            archon_api_key=archon_key,
            openrouter_api_key=openrouter_key,
        )
        
        # Test the agent
        console.print(f"[bold]Testing agent {agent_id} with {test_type} tests...[/bold]")
        test_run = tester.test_agent(agent_id, test_type)
        
        # Print summary
        console.print("\n[bold]Test Results:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Metric")
        table.add_column("Value")
        
        table.add_row("Status", test_run.status.value)
        table.add_row("Total Tests", str(test_run.summary.get("total", 0)))
        table.add_row("Passed", str(test_run.summary.get("passed", 0)))
        table.add_row("Failed", str(test_run.summary.get("failed", 0)))
        table.add_row("Error", str(test_run.summary.get("error", 0)))
        table.add_row("Skipped", str(test_run.summary.get("skipped", 0)))
        
        console.print(table)
        
        # Generate report
        report_path = tester.generate_report(test_run, format=report_format)
        console.print(f"\n[bold]Report generated:[/bold] {report_path}")
        
    except ArchonAgentTesterError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.exception("Unexpected error")
        sys.exit(1)


@app.command()
def list_agents(
    limit: int = typer.Option(10, help="Maximum number of agents to list"),
    offset: int = typer.Option(0, help="Offset for pagination"),
    archon_api_key: Optional[str] = typer.Option(None, help="Archon API key"),
):
    """
    List agents from Archon.
    """
    try:
        # Get API key from environment if not provided
        archon_key = archon_api_key or os.environ.get("ARCHON_API_KEY")
        
        if not archon_key:
            console.print("[bold red]Error:[/bold red] Archon API key is required")
            sys.exit(1)
        
        # Initialize the tester
        tester = ArchonTester(archon_api_key=archon_key)
        
        # List agents
        console.print(f"[bold]Listing agents (limit={limit}, offset={offset})...[/bold]")
        agents = tester.list_agents(limit=limit, offset=offset)
        
        # Print agents
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Created At")
        
        for agent in agents:
            table.add_row(
                agent.get("id", ""),
                agent.get("name", ""),
                agent.get("description", ""),
                agent.get("created_at", ""),
            )
        
        console.print(table)
        
    except ArchonAgentTesterError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.exception("Unexpected error")
        sys.exit(1)


@app.command()
def list_models(
    openrouter_api_key: Optional[str] = typer.Option(None, help="OpenRouter API key"),
):
    """
    List available models from OpenRouter.
    """
    try:
        # Get API key from environment if not provided
        openrouter_key = openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        
        if not openrouter_key:
            console.print("[bold red]Error:[/bold red] OpenRouter API key is required")
            sys.exit(1)
        
        # Initialize the tester
        tester = ArchonTester(openrouter_api_key=openrouter_key)
        
        # List models
        console.print("[bold]Listing available models...[/bold]")
        models = tester.list_available_models()
        
        # Print models
        table = Table(show_header=True, header_style="bold")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Provider")
        table.add_column("Context Size")
        
        for model in models:
            table.add_row(
                model.get("id", ""),
                model.get("name", ""),
                model.get("provider", {}).get("name", ""),
                str(model.get("context_length", "")),
            )
        
        console.print(table)
        
    except ArchonAgentTesterError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.exception("Unexpected error")
        sys.exit(1)


@app.command()
def create_test_case(
    name: str = typer.Option(..., help="Name of the test case"),
    description: str = typer.Option(..., help="Description of the test case"),
    test_type: str = typer.Option("functional", help="Type of test"),
    prompt: str = typer.Option(..., help="Prompt to send to the agent"),
    output_file: str = typer.Option("test_case.json", help="File to save the test case to"),
):
    """
    Create a custom test case.
    """
    try:
        # Initialize the tester
        tester = ArchonTester()
        
        # Create the test case
        test_case = tester.create_custom_test_case(
            name=name,
            description=description,
            test_type=TestType(test_type.lower()),
            inputs={"prompt": prompt},
            evaluation_criteria={"response_not_empty": "The agent should provide a non-empty response"},
        )
        
        # Save to file
        import json
        with open(output_file, "w") as f:
            json.dump(test_case.dict(), f, indent=2, default=str)
        
        console.print(f"[bold]Test case created and saved to {output_file}[/bold]")
        
    except ArchonAgentTesterError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        logger.exception("Unexpected error")
        sys.exit(1)


def main():
    """
    Main entry point for the CLI.
    """
    app()