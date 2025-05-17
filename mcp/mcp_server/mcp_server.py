from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import pytz
import uuid

app = FastAPI()

class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    timestamp: str

def get_time_in_timezone(timezone: str) -> Dict[str, str]:
    """Get current time in the specified timezone."""
    try:
        # Validate timezone
        tz = pytz.timezone(timezone)
        # Get current time in specified timezone
        current_time = datetime.now(tz)
        return {
            "time": current_time.isoformat(),
            "timezone": timezone
        }
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(status_code=400, detail=f"Invalid timezone: {timezone}")

@app.post("/mcp/call")
async def handle_tool_call(request: ToolCallRequest):
    """
    Handle MCP tool call requests.
    Expects tool_name, parameters, and timestamp in the request body.
    """
    try:
        # Validate timestamp format
        try:
            datetime.fromisoformat(request.timestamp)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid timestamp format")

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Handle supported tools
        if request.tool_name == "get_time_in_timezone":
            if "timezone" not in request.parameters:
                raise HTTPException(status_code=400, detail="Missing timezone parameter")
            
            result = get_time_in_timezone(request.parameters["timezone"])
            return {
                "result": result,
                "request_id": request_id
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.tool_name}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)