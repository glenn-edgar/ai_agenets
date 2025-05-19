MCP Client Documentation
Overview
The MCP (Model Control Plane) Client is a Python-based client designed to interact with an MCP server via the /mcp/call endpoint. It supports calling the get_time_in_timezone tool to retrieve the current time in a specified timezone. The client sends unauthenticated POST requests with JSON payloads and processes responses containing the tool result and a request ID. It is configured to communicate with a server at http://127.0.0.1:8080 by default.
Features

Sends POST requests to /mcp/call with tool name, parameters, and a timezone-aware UTC timestamp
Supports the get_time_in_timezone tool with a timezone parameter
Generates timestamps using datetime.now(timezone.utc) for compatibility with modern Python
Handles errors gracefully with detailed error messages
Returns results including time, timezone, and request ID
Uses type hints for better code clarity

Requirements

Python 3.8+
Dependencies:
requests



Install dependencies using:
pip install requests

Setup and Running

Save the client code as mcp_client.py.
Ensure the requests library is installed (see above).
Ensure the MCP server is running at http://127.0.0.1:8080 (see server documentation, artifact_id: 58a8b88a-99ba-49ab-a23b-236c0954c8d4).
Run the client:python mcp_client.py

The client will test the get_time_in_timezone tool with sample timezones (America/New_York, Europe/London, Asia/Tokyo).

Usage
The client provides a MCPClient class with methods to call tools and fetch timezone-specific times.
Initialization
from mcp_client import MCPClient

client = MCPClient(base_url="http://127.0.0.1:8080")

Getting Time in a Timezone
result = client.get_time_in_timezone("America/New_York")
if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(f"Time: {result['time']}, Request ID: {result['request_id']}")

Methods
MCPClient(base_url: str)
Initializes the client with the server’s base URL.

Parameters:
base_url (str): The MCP server URL (e.g., http://127.0.0.1:8080). Trailing slashes are removed.


Attributes:
base_url: The cleaned server URL
headers: JSON content-type header ({'Content-Type': 'application/json'})



call_tool(tool_name: str, parameters: Dict[str, Any]) -> Tuple[Any, str]
Calls a tool on the MCP server and returns the result and request ID.

Parameters:
tool_name (str): Name of the tool (e.g., get_time_in_timezone)
parameters (dict): Tool-specific parameters (e.g., {"timezone": "America/New_York"})


Returns:
Tuple of (response, request_id):
response: The tool’s result (e.g., {"time": "...", "timezone": "..."})
request_id: Unique ID for the request




Raises:
Exception: If the request fails (e.g., network error, server error)



get_time_in_timezone(timezone: str) -> Dict[str, str]
Fetches the current time in the specified timezone.

Parameters:
timezone (str): Timezone name (e.g., America/New_York)


Returns:
Dictionary with:
time (str): ISO 8601 time in the timezone
timezone (str): Requested timezone
request_id (str): Unique request ID
error (str, optional): Error message if the call fails




Example Output:{
    'time': '2025-05-19T06:53:00.123456-04:00',
    'timezone': 'America/New_York',
    'request_id': 'a1b2c3d4-5678-9012-3456-7890abcdef12'
}



Request Format
The client sends POST requests to http://127.0.0.1:8080/mcp/call with:

Content-Type: application/json
Body:{
  "tool_name": "get_time_in_timezone",
  "parameters": {
    "timezone": "America/New_York"
  },
  "timestamp": "2025-05-19T10:53:00.000000+00:00"
}



Response Handling
The client expects server responses in the format:
{
  "result": {
    "time": "2025-05-19T06:53:00.123456-04:00",
    "timezone": "America/New_York"
  },
  "request_id": "a1b2c3d4-5678-9012-3456-7890abcdef12"
}


Errors are caught and returned as:{
    'error': 'Failed to call tool get_time_in_timezone: <error message>',
    'timezone': '<requested timezone>',
    'request_id': None
}



Error Handling

Network errors (e.g., server unreachable) are caught and returned as errors in the result dictionary
Server errors (e.g., 400, 500) are propagated as exceptions and wrapped in the result
Invalid timezone names or server issues result in an error response from the server, which the client includes in the output

Notes

The client uses datetime.now(timezone.utc) to generate timezone-aware UTC timestamps, ensuring compatibility with Python 3.12+.
No authentication is implemented, matching the server’s configuration.
The default base_url is http://127.0.0.1:8080. Update it if the server runs on a different host or port.
The client assumes the server returns JSON with result and request_id fields. Adjust parsing if the server response format changes.
Compatible with the MCP server (artifact_id: 58a8b88a-99ba-49ab-a23b-236c0954c8d4).

Example Output
Running the client with the default main() function produces output like:
Time in America/New_York: 2025-05-19T06:53:00.123456-04:00 (Request ID: a1b2c3d4-5678-9012-3456-7890abcdef12)
Time in Europe/London: 2025-05-19T11:53:00.123456+01:00 (Request ID: b2c3d4e5-6789-0123-4567-8901bcdef234)
Time in Asia/Tokyo: 2025-05-19T19:53:00.123456+09:00 (Request ID: c3d4e5f6-7890-1234-5678-9012cdef3456)

Extending the Client
To support additional tools:

Add new methods similar to get_time_in_timezone, using call_tool with appropriate parameters.
Update the main() function or create new example usage.
Update this documentation with the new method’s details.

