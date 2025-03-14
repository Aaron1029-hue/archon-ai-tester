"""
Client for interacting with the Archon API.
"""
import logging
from typing import Dict, List, Optional, Any, Union

import httpx

from ..core.config import settings
from ..core.exceptions import ArchonAPIError, AgentNotFoundError


logger = logging.getLogger(__name__)


class ArchonClient:
    """
    Client for interacting with the Archon API.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the Archon client.
        
        Args:
            api_key: Archon API key. If not provided, it will be loaded from settings.
            base_url: Archon API base URL. If not provided, it will be loaded from settings.
        """
        self.api_key = api_key or settings.archon_api_key.get_secret_value()
        self.base_url = base_url or settings.archon_api_base_url
        self.client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=settings.default_timeout,
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def _handle_response(self, response: httpx.Response) -> Dict:
        """
        Handle the API response.
        
        Args:
            response: The HTTP response.
            
        Returns:
            The response data.
            
        Raises:
            ArchonAPIError: If the response status code is not 2xx.
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise AgentNotFoundError(f"Agent not found: {e.response.text}")
            raise ArchonAPIError(f"API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise ArchonAPIError(f"Error processing response: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Dict:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The agent data.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the API.
        """
        try:
            response = self.client.get(f"/agents/{agent_id}")
            return self._handle_response(response)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error getting agent {agent_id}: {str(e)}")
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return.
            offset: Offset for pagination.
            
        Returns:
            List of agents.
            
        Raises:
            ArchonAPIError: If there is an error with the API.
        """
        try:
            response = self.client.get("/agents", params={"limit": limit, "offset": offset})
            return self._handle_response(response)
        except Exception as e:
            raise ArchonAPIError(f"Error listing agents: {str(e)}")
    
    def invoke_agent(self, agent_id: str, inputs: Dict[str, Any]) -> Dict:
        """
        Invoke an agent with the given inputs.
        
        Args:
            agent_id: The ID of the agent.
            inputs: The inputs for the agent.
            
        Returns:
            The agent's response.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the API.
        """
        try:
            response = self.client.post(f"/agents/{agent_id}/invoke", json={"inputs": inputs})
            return self._handle_response(response)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error invoking agent {agent_id}: {str(e)}")
    
    def get_agent_metrics(self, agent_id: str) -> Dict:
        """
        Get metrics for an agent.
        
        Args:
            agent_id: The ID of the agent.
            
        Returns:
            The agent metrics.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the API.
        """
        try:
            response = self.client.get(f"/agents/{agent_id}/metrics")
            return self._handle_response(response)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error getting metrics for agent {agent_id}: {str(e)}")
    
    def update_agent_metadata(self, agent_id: str, metadata: Dict[str, Any]) -> Dict:
        """
        Update metadata for an agent.
        
        Args:
            agent_id: The ID of the agent.
            metadata: The metadata to update.
            
        Returns:
            The updated agent data.
            
        Raises:
            AgentNotFoundError: If the agent is not found.
            ArchonAPIError: If there is an error with the API.
        """
        try:
            response = self.client.patch(f"/agents/{agent_id}", json={"metadata": metadata})
            return self._handle_response(response)
        except AgentNotFoundError:
            raise
        except Exception as e:
            raise ArchonAPIError(f"Error updating metadata for agent {agent_id}: {str(e)}")