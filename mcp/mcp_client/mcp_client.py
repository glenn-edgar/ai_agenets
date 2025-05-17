import json
import requests
from typing import Dict, Any, Tuple
from datetime import datetime, timezone

class MCPClient:
    def __init__(self, base_url: str):
        """Initialize MCP client with base URL."""
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Content-Type': 'application/json'
        }

    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[Any, str]:
        """
        Call a tool with given parameters and return response and request ID.
        
        Args:
            tool_name (str): Name of the tool to call
            parameters (dict): Parameters for the tool
            
        Returns:
            Tuple containing (response, request_id)
        """
        try:
            payload = {
                'tool_name': tool_name,
                'parameters': parameters,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(
                f'{self.base_url}/mcp/call',
                headers=self.headers,
                json=payload
            )
            
            response.raise_for_status()
            response_data = response.json()
            
            return response_data.get('result'), response_data.get('request_id')
            
        except requests.RequestException as e:
            raise Exception(f"Failed to call tool {tool_name}: {str(e)}")

    def get_time_in_timezone(self, timezone: str) -> Dict[str, str]:
        """
        Get current time in specified timezone.
        
        Args:
            timezone (str): Timezone name (e.g., 'America/New_York')
            
        Returns:
            Dict containing time information
        """
        try:
            response, request_id = self.call_tool(
                tool_name="get_time_in_timezone",
                parameters={"timezone": timezone.strip()}
            )
            
            return {
                'time': response.get('time'),
                'timezone': timezone,
                'request_id': request_id
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'timezone': timezone,
                'request_id': None
            }

def main():
    # Example usage
    client = MCPClient(
        base_url="http://127.0.0.1:8080"
    )
    
    # Test with a few timezones
    timezones = ["America/New_York", "Europe/London", "Asia/Tokyo"]
    
    for tz in timezones:
        result = client.get_time_in_timezone(tz)
        if 'error' in result:
            print(f"Error for {tz}: {result['error']}")
        else:
            print(f"Time in {tz}: {result['time']} (Request ID: {result['request_id']})")

if __name__ == "__main__":
    main()