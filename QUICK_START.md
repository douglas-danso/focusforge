# FocusForge Memory-Chain-Planner Quick Start

## Prerequisites

- Python 3.8+
- MongoDB running locally
- Redis (optional, for background tasks)
- OpenAI API key

## 1. Install Dependencies

```powershell
pip install -r backend/requirements.txt
```

## 2. Set Environment Variables

```powershell
# Set environment variables (Windows PowerShell)
$env:MONGODB_URI = "mongodb://localhost:27017"
$env:OPENAI_API_KEY = "your_openai_api_key_here"
$env:REDIS_URL = "redis://localhost:6379"  # Optional
$env:ENABLE_BACKGROUND_TASKS = "true"      # Optional
```

## 3. Start the Backend

```powershell
cd backend
python main.py
```

The API will be available at: http://localhost:8000

## 4. Explore the API

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 5. Test the Memory-Chain-Planner Architecture

### Create an Enhanced Task
```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/tasks/create-enhanced" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Learn Memory-Chain-Planner architecture",
       "description": "Study the new architecture implementation",
       "priority": "high",
       "user_id": "user123"
     }'
```

### Execute Chains Directly
```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/chains/execute/task_breakdown" \
     -H "Content-Type: application/json" \
     -d '{
       "task": "Implement AI productivity system",
       "user_id": "user123"
     }'
```

### Get User Memory Context
```bash
curl -X GET "http://localhost:8000/api/v1/orchestrator/memory/user-context/user123"
```

### Plan Actions
```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/planner/actions/user123" \
     -H "Content-Type: application/json" \
     -d '{
       "goal": "Complete daily tasks efficiently",
       "context": {"urgency": "high", "energy_level": "medium"}
     }'
```

## 6. Start Background Workers (Optional)

In separate PowerShell windows:

```powershell
# Start worker
python -c "from app.core.background_tasks import start_worker; start_worker()"

# Start scheduler
python -c "from app.core.background_tasks import start_scheduler; start_scheduler()"
```

## 7. Key Endpoints to Try

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/api/v1/orchestrator/tasks/create-enhanced` | Enhanced task creation | POST |
| `/api/v1/orchestrator/daily-optimization` | Daily optimization workflow | POST |
| `/api/v1/orchestrator/focus-session` | Focus session with rituals | POST |
| `/api/v1/orchestrator/chains/execute/{chain_name}` | Execute specific chain | POST |
| `/api/v1/orchestrator/planner/actions/{user_id}` | Get planned actions | GET |
| `/api/v1/orchestrator/memory/user-context/{user_id}` | User memory context | GET |

## 8. Architecture Features to Explore

### Memory System
- Short-term memory for session data
- Working memory for active tasks
- Long-term memory for user patterns
- Semantic memory for intelligent search

### Chain Processing
- Task breakdown with AI analysis
- Motivation generation
- Proof validation
- Batch chain execution

### Intelligent Planning
- Action dependency resolution
- Priority-based execution
- Background processing
- Retry mechanisms

### Unified MCP Integration
- 15+ productivity tools
- Consistent interface
- Rate limiting
- Error handling

## 9. Monitoring & Health

Check system health:
```bash
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/api/v1/orchestrator/status"
```

## 10. Frontend (Optional)

To run the frontend:

```powershell
cd frontend
npm install
npm start
```

Frontend will be available at: http://localhost:3000

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running
   - Check connection string in environment variables

2. **Redis Connection Warning**
   - Redis is optional for basic functionality
   - Background tasks will use fallback mode without Redis

3. **OpenAI API Error**
   - Verify API key is set correctly
   - Check API key permissions and usage limits

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+)

### Debug Mode

Run with debug logging:
```powershell
$env:LOG_LEVEL = "DEBUG"
python main.py
```

## Next Steps

1. **Explore the API**: Use the Swagger UI to test all endpoints
2. **Review Architecture**: Read `MEMORY_CHAIN_PLANNER_ARCHITECTURE.md`
3. **Customize Chains**: Modify chains in `app/core/chains.py`
4. **Add Tools**: Extend the MCP system in `app/core/mcp_adapter.py`
5. **Deploy**: Follow deployment guides for production setup

Happy coding with the Memory-Chain-Planner architecture! 🚀
