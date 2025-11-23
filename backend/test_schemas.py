"""
Test script to validate API schemas
"""

import json
from app.models.api_schemas import (
    TaskCreationRequest, TaskCreationResponse,
    MCPToolsResponse, MCPToolInfo,
    ProcessingMode, MCPToolCategory
)

def test_task_creation_request():
    """Test TaskCreationRequest schema"""
    request_data = {
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the project",
        "duration_minutes": 120,
        "priority": "high",
        "tags": ["documentation", "project"],
        "auto_breakdown": True,
        "preferences": {"focus_music": True}
    }
    
    request = TaskCreationRequest(**request_data)
    print("✅ TaskCreationRequest schema validation passed")
    print(f"Request: {request.dict()}")
    return request

def test_task_creation_response():
    """Test TaskCreationResponse schema"""
    response_data = {
        "success": True,
        "processing": ProcessingMode.IMMEDIATE,
        "user_id": "user123",
        "planned_actions": 3,
        "user_context_enhanced": True,
        "similar_tasks_found": 2
    }
    
    response = TaskCreationResponse(**response_data)
    print("✅ TaskCreationResponse schema validation passed")
    print(f"Response: {response.dict()}")
    return response

def test_mcp_tools_response():
    """Test MCPToolsResponse schema"""
    tool_info = MCPToolInfo(
        name="task_breakdown",
        description="Break down complex tasks",
        parameters={"title": {"type": "string", "required": True}},
        category="ai_agents"
    )
    
    response_data = {
        "success": True,
        "tools": [tool_info],
        "tools_by_category": {"ai_agents": [tool_info]},
        "tool_count": 1
    }
    
    response = MCPToolsResponse(**response_data)
    print("✅ MCPToolsResponse schema validation passed")
    print(f"Response: {response.dict()}")
    return response

def main():
    """Run all schema tests"""
    print("🧪 Testing API Schemas...")
    print("-" * 50)
    
    try:
        test_task_creation_request()
        print()
        
        test_task_creation_response()
        print()
        
        test_mcp_tools_response()
        print()
        
        print("🎉 All schema tests passed!")
        
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        raise

if __name__ == "__main__":
    main()
