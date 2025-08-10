# FocusForge MCP Endpoint Tests
# Run these curl commands to test the MCP integration

echo "🚀 Testing FocusForge MCP Integration"
echo "====================================="

# Test 1: Health check (should show MCP status)
echo ""
echo "1️⃣ Testing health endpoint..."
curl -s http://localhost:8000/health | python -m json.tool

# Test 2: MCP Status
echo ""
echo "2️⃣ Testing MCP status..."
curl -s http://localhost:8000/api/v1/mcp/status | python -m json.tool

# Test 3: List MCP Tools
echo ""
echo "3️⃣ Testing MCP tools list..."
curl -s http://localhost:8000/api/v1/mcp/tools | python -m json.tool

# Test 4: MCP Health Check
echo ""
echo "4️⃣ Testing MCP health..."
curl -s http://localhost:8000/api/v1/mcp/health | python -m json.tool

# Test 5: Task Breakdown via MCP
echo ""
echo "5️⃣ Testing MCP task breakdown..."
curl -s -X POST http://localhost:8000/api/v1/mcp/agents/task-breakdown-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "task_data": {
      "title": "Write API documentation",
      "description": "Create comprehensive documentation for all endpoints",
      "duration_minutes": 90
    }
  }' | python -m json.tool

# Test 6: Motivation via MCP
echo ""
echo "6️⃣ Testing MCP motivation..."
curl -s -X POST http://localhost:8000/api/v1/mcp/agents/motivation-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "current_mood": "tired",
    "challenge": "feeling overwhelmed with tasks"
  }' | python -m json.tool

# Test 7: Task Analysis via MCP
echo ""
echo "7️⃣ Testing MCP task analysis..."
curl -s -X POST http://localhost:8000/api/v1/mcp/agents/task-analysis-mcp \
  -H "Content-Type: application/json" \
  -d '{
    "task_data": {
      "title": "Implement user authentication",
      "description": "Add JWT-based auth system",
      "duration_minutes": 120
    },
    "user_skill_level": "intermediate"
  }' | python -m json.tool

# Test 8: Toggle MCP
echo ""
echo "8️⃣ Testing MCP toggle..."
curl -s -X POST http://localhost:8000/api/v1/mcp/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}' | python -m json.tool

echo ""
echo "✨ MCP endpoint testing completed!"
echo "====================================="
