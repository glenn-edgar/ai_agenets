# Configure Claude Desktop for MCP Server Integration

This guide explains how to configure Claude Desktop to communicate with a custom MCP server. We'll use the example of an `mcp_timezone_server.py` script that allows Claude to fetch the current time in different timezones.

## 1. Locate and Edit the Claude Desktop Configuration File

First, you need to find or create the Claude Desktop configuration file. The location depends on your operating system:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `C:\Users\\AppData\Roaming\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

If the file doesn’t exist, you'll need to create it.

## 2. Configure the MCP Server in `claude_desktop_config.json`

You have two primary ways to configure how Claude Desktop interacts with your MCP server: either let Claude Desktop manage the server process or run the server manually and tell Claude Desktop how to connect to it.

### Option A: Claude Desktop Manages the MCP Server (Recommended for Simplicity)

In this setup, Claude Desktop will start your MCP server script automatically when needed.

Add the following configuration to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "timezone": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_timezone_server.py"],
      "env": {}
    }
  }
}
```

**Customize the configuration:**

- `command`: Replace `"python"` with the specific command for your Python interpreter if needed (e.g., `"python3"` or an absolute path like `"/usr/bin/python3"`). You can find your Python executable path by running `which python` or `which python3` in your terminal.
- `args`: Replace `"/absolute/path/to/mcp_timezone_server.py"` with the full, absolute path to your `mcp_timezone_server.py` script (e.g., `"/home/gedgar/ai_agenets/mcp_server/mcp_timezone_server.py"`).
- `env`: This object can be used to set environment variables for the server process. For now, an empty object `{}` is fine. (See section 3 for more on `env`).

**Behavior:**

- Claude Desktop will attempt to spawn a new process by running `python /absolute/path/to/mcp_timezone_server.py` (or your specified command and args).
- It expects the server to start listening on its predefined port (e.g., port 8000, as typically defined in `mcp_timezone_server.py`).
- **Assumption:** This configuration assumes the server is *not* already running. Claude Desktop will manage its lifecycle.

**Pros:** Simplifies setup as Claude manages the server.

**Cons:** Less control over server options (e.g., port, logging); potential issues if Claude restarts the server unexpectedly.

### Option B: Manually Run the MCP Server (Advanced Control)

In this setup, you start the MCP server yourself, and Claude Desktop connects to the already running instance.

Start your MCP server manually. For example:

```bash
python /home/gedgar/ai_agenets/mcp_server/mcp_timezone_server.py
```

Or, for a more production-like setup using Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 mcp_timezone_server:app
```

Ensure the server is running and listening on the correct host and port (e.g., `http://localhost:8000`).

Modify `claude_desktop_config.json` to connect to the running server:

```json
{
  "mcpServers": {
    "timezone": {
      "url": "http://localhost:8000",
      "env": {}
    }
  }
}
```

- `url`: This tells Claude to communicate with an already-running server at the specified address. Adjust `http://localhost:8000` if your server runs on a different port or host.

**Pros:** More control over the server (e.g., using Gunicorn, custom logging); avoids port conflicts if Claude tries to start an already running server.

**Cons:** You must manage the server process manually (start/stop, handle crashes).

After configuring, **save the `claude_desktop_config.json` file and restart Claude Desktop.**

## 3. Understanding the `env` Parameter

The `env` parameter within the `mcpServers` section specifies environment variables to be set when Claude Desktop launches the MCP server process (primarily relevant for Option A).

```json
"env": {
  "DEBUG": "true",
  "API_KEY": "your-secret-key"
}
```

- **Purpose:** Allows you to configure the server’s behavior (e.g., debug modes, API keys, custom paths) without modifying its code.
- **Usage with command/args (Option A):** When Claude launches the server, it sets these environment variables for the server's process. Your Python script can then access them using `os.getenv("DEBUG")`.
- **Usage with url (Option B):** The `env` parameter in `claude_desktop_config.json` is generally ignored because Claude Desktop doesn't launch the server process itself. Environment variables must be set when you manually start the server (e.g., `export DEBUG=true` before running the Python script, or `DEBUG=true gunicorn ...`).

Your provided example: `"env": {}` means no custom environment variables are being passed from the Claude Desktop configuration.

## 4. How the Integration Works

The MCP server exposes several endpoints that Claude Desktop interacts with.

### Key MCP Server Endpoints

- **/mcp/tools:**
  - **Method:** GET
  - **Purpose:** Claude queries this endpoint to discover the available tools, their descriptions, and parameters.
  - **Example Response from mcp_timezone_server.py:**

    ```json
    {
      "tools": [{
        "name": "get_time_in_timezone",
        "description": "Returns the current time in the specified timezone.",
        "parameters": {
          "timezone": {"type": "string", "description": "The timezone name (e.g., 'America/New_York')"}
        }
      }]
    }
    ```

- **/mcp/call:**
  - **Method:** POST
  - **Purpose:** Claude sends a request to this endpoint to execute a specific tool with given parameters.
  - **Example Request from Claude:**

    ```json
    {
      "tool": "get_time_in_timezone",
      "parameters": {"timezone": "America/New_York"},
      "request_id": "some-unique-uuid"
    }
    ```

  - **Expected Immediate HTTP Response from Server:**  
    A `200 OK` status with a simple JSON body like `{"status": "success"}` to acknowledge the request.  
    Errors (e.g., invalid timezone) should return an appropriate HTTP error code (e.g., 400) and an error message:  
    `{"error": "Invalid timezone: America/Invalid"}`

- **/mcp/sse:**
  - **Method:** GET
  - **Purpose:** Claude establishes a Server-Sent Events (SSE) connection to this endpoint to receive asynchronous responses (tool results) from the server.
  - **MIME Type:** `text/event-stream`

### Triggers for Claude-to-Server Communication

Claude sends HTTP requests (events) to the MCP server’s endpoints under these conditions:

- **Tool Discovery (Startup/Interaction):**
  - **Trigger:** Claude Desktop starts (if configured to initialize MCP servers), the user interacts with the hammer icon (indicating MCP tools) in the chat interface, or a prompt suggests potential tool usage.
  - **Process:** Claude sends a GET request to `/mcp/tools`.

- **User Prompt Requiring a Tool:**
  - **Trigger:** Claude’s NLP detects a user prompt matching a tool's functionality.
  - **Process:**  
    User types: "Get the current time in America/New_York."  
    Claude parses this and sends a POST request to `/mcp/call` with the tool name and parameters.  
    The server processes the request and sends the result back via the `/mcp/sse` stream.

- **Server-Sent Events (SSE) Connection:**
  - **Trigger:** Claude needs to receive asynchronous updates.
  - **Process:** Claude sends a GET request to `/mcp/sse` to open an SSE stream. The server keeps this connection open to push events.

### Server-Sent Events (SSE) for Asynchronous Responses

SSE allows the server to push real-time updates to Claude Desktop over a single, long-lived HTTP connection.

**How it works in `mcp_timezone_server.py`:**

- The `/mcp/sse` endpoint is set up to stream data.
- When a tool call is made via `/mcp/call` (e.g., to get the time), the server processes it.
- The result is formatted (e.g.,  
  `{"type": "tool_response", "request_id": "some-unique-uuid", "data": {"time": "2025-05-17 17:15:00 EDT"}}`)  
  and put into a queue.
- The `/mcp/sse` stream handler picks up this data from the queue and sends it to Claude as an SSE event:

  ```
  data: {"type": "tool_response", "request_id": "some-unique-uuid", "data": {"time": "2025-05-17 17:15:00 EDT"}}
  ```

- Periodic "ping" events (`data: {"type": "ping", "data": {}}`) are sent to keep the connection alive if no tool responses are pending.
- **Claude's Role:** Claude listens to this stream, parses the JSON data from `tool_response` events, and displays the result.

## 5. Testing the Integration

- **Ensure Dependencies:** Confirm necessary Python libraries are installed (e.g., Flask, pytz for the timezone server):

  ```bash
  pip install flask pytz
  ```

- **Configure and Restart:** Ensure `claude_desktop_config.json` is correctly set up (as per section 2) and restart Claude Desktop.
- **Check for Hammer Icon:** Open Claude Desktop. Look for a hammer icon in the chat input box. This indicates that Claude has detected and connected to the MCP server. Clicking it might trigger a `/mcp/tools` request.
- **Test with a Prompt:** Type a prompt that should trigger your tool. For the timezone server:  
  `"Get the current time in America/New_York."`  
  Claude should respond with the current time, e.g., `"2025-05-17 17:15:23 EDT"` (adjusting for the actual current time and timezone).  
  Other examples: `"What time is it in Tokyo?"`, `"Current time in America/Los_Angeles."`
- **Check Server Logs:**  
  If you're running the server manually (Option B), check its console output for incoming requests (`GET /mcp/tools`, `POST /mcp/call`, `GET /mcp/sse`) and any errors.  
  If Claude manages the server (Option A), logging might be less direct, but issues often manifest as the hammer icon not appearing or tools not working.

## 6. Potential Issues and Debugging

- **Port Conflict:**
  - **Symptom:** Error like "Address already in use" if Claude (Option A) tries to start the server on a port that's already occupied, or if you try to manually start the server on an occupied port.
  - **Fix:**
    - If using Option A, ensure nothing else is using the server's port (e.g., 8000). Stop the conflicting process or change the port in `mcp_timezone_server.py` and restart Claude.
    - If using Option B, this is less likely to be a Claude-side issue, but ensure your manual server starts correctly.
    - Check port usage: `netstat -tuln | grep 8000` (Linux/macOS).

- **Path Errors (for Option A):**
  - **Symptom:** Hammer icon doesn't appear; Claude can't start the server.
  - **Fix:** Double-check the command and args (absolute path to the script) in `claude_desktop_config.json`. Ensure the Python script is executable (`chmod +x mcp_timezone_server.py`).

- **Server Not Starting (for Option A):**
  - **Symptom:** Similar to path errors.
  - **Fix:** Verify the Python command is correct (e.g., `python` vs `python3`). Check script permissions.

- **Prompt Misinterpretation:**
  - **Symptom:** Claude doesn't trigger the tool even if the server seems to be running.
  - **Fix:** Ensure your prompt is clear and matches the tool's intended functionality. Check server logs for `/mcp/tools` requests to confirm Claude recognizes the tool and its description.

- **Verifying SSE Events:**
  - Run the MCP server manually.
  - Use `curl http://localhost:8000/mcp/sse` in a terminal. You should see ping events and then tool responses when you trigger a call from Claude.
  - Alternatively, open `http://localhost:8000/mcp/sse` in a browser and check the Network tab in developer tools.

## 7. Production Considerations

If running the MCP server manually for production (Option B):

- Use a robust WSGI server like Gunicorn:

  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 mcp_timezone_server:app
  ```

- Manage the server process using a process manager (e.g., systemd, Docker).
- Consider securing MCP endpoints (HTTPS, authentication), though this is beyond the scope of the basic `mcp_timezone_server.py`.

---

This structured guide should help you successfully configure and use your MCP server with Claude Desktop. Remember to adjust paths and commands based on your specific environment and the current date/time for expected outputs.

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/56907441/af282867-1fc7-4b71-9edc-c4ca74bfd5da/paste.txt

---
Answer from Perplexity: pplx.ai/share
