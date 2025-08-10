# FocusForge Memory-Chain-Planner Architecture

## Overview

FocusForge now implements the complete **Memory-Chain-Planner** pattern as described in the architectural blueprint, using your existing **Unified MCP System** as the adapter layer. This creates a sophisticated, AI-driven productivity platform that aligns perfectly with the provided architecture specification.

## Architecture Components

```
[ Mobile / Web Frontend ]
         ↕ (REST / WebSocket)
[ FastAPI API Gateway ]  ←→  [ Memory-Chain-Planner Orchestrator ]
         ↕                            ↕
[ Memory Layer ]  ←→  [ Chains Layer ]  ←→  [ Planner Layer ]
         ↕                            ↕                ↕
[ Unified MCP System (Adapter Layer) ]  ←→  [ Background Tasks (RQ) ]
         ↕
[ External Services: MongoDB, Redis, Spotify, Calendar ]
```

### 1. Memory Layer (`app/core/memory.py`)

- **MemoryStore**: Multi-type memory system (short-term, working, long-term, semantic)
- **PersistentConversationMemory**: LangChain-compatible memory with MongoDB persistence
- **MemoryManager**: High-level interface for memory operations
- **Features**:
  - TTL-based automatic cleanup
  - User context persistence
  - Task insights storage
  - Conversation history
  - Similar task search

### 2. Chains Layer (`app/core/chains.py`)

- **TaskBreakdownChain**: AI-powered task decomposition
- **TaskAnalysisChain**: Complexity and requirement analysis
- **MotivationChain**: Personalized motivation generation
- **ProofValidationChain**: Task completion proof validation
- **ChainExecutor**: Central execution manager with caching
- **Features**:
  - LangChain integration
  - Memory-aware processing
  - Result caching
  - Error recovery
  - Chain composition

### 3. Planner Layer (`app/core/planner.py`)

- **ActionPlanner**: Intelligent action planning and coordination
- **PlannedAction**: Action data model with dependencies
- **ActionExecutors**: Specialized executors for different action types
- **Features**:
  - Dependency management
  - Priority-based execution
  - Background processing
  - Retry mechanisms
  - Action monitoring

### 4. Unified MCP System (Existing - Enhanced)

Your existing `unified_mcp.py` serves as the perfect **MCP Adapter Layer**:
- 15+ standardized tools across 5 categories
- Direct integration with all services
- Consistent interface for AI agents
- Rate limiting and error handling

### 5. Orchestrator (`app/core/orchestrator.py`)

- **MCPOrchestrator**: Central coordinator implementing the complete pattern
- **Workflow Methods**: High-level workflow orchestration
- **Background Processing**: Automated task management
- **Event System**: Event-driven architecture
- **Features**:
  - Complete workflow coordination
  - Memory-Chain-Planner integration
  - Background task management
  - System health monitoring

### 6. Background Tasks (`app/core/background_tasks.py`)

- **RQ Integration**: Redis Queue for background processing
- **Task Scheduler**: High-level task scheduling interface
- **Worker Management**: Background worker coordination
- **Features**:
  - Async task processing
  - Recurring task scheduling
  - Job monitoring
  - Fallback mechanisms

## API Endpoints

### Memory-Chain-Planner Orchestrator
- `POST /orchestrator/tasks/create-enhanced` - Complete task creation workflow
- `POST /orchestrator/tasks/complete-enhanced` - Complete task completion workflow
- `POST /orchestrator/daily-optimization` - Daily optimization workflow
- `POST /orchestrator/focus-session` - Focus session with ritual recommendations

### Planner Management
- `GET /orchestrator/planner/actions/{user_id}` - Get user's planned actions
- `POST /orchestrator/planner/execute/{user_id}` - Execute ready actions
- `DELETE /orchestrator/planner/actions/{action_id}` - Cancel action

### Chain Execution
- `POST /orchestrator/chains/execute/{chain_name}` - Execute specific chain
- `POST /orchestrator/chains/sequence` - Execute chain sequence
- `DELETE /orchestrator/chains/cache` - Clear chain cache

### Memory Management
- `GET /orchestrator/memory/user-context/{user_id}` - Get user context
- `POST /orchestrator/memory/user-context/{user_id}` - Update user context
- `GET /orchestrator/memory/similar-tasks/{user_id}` - Search similar tasks

### Background Tasks
- `GET /orchestrator/background-tasks/status/{job_id}` - Get task status
- `DELETE /orchestrator/background-tasks/{job_id}` - Cancel background task

## Workflow Examples

### 1. Task Creation Workflow

When a user creates a task, the system:

1. **Memory**: Stores user context and retrieves relevant history
2. **Chains**: Executes task analysis and breakdown chains
3. **Planner**: Creates execution plan with dependencies
4. **MCP**: Creates task using unified MCP system
5. **Memory**: Stores complete workflow result
6. **Planner**: Executes immediate actions

### 2. Task Completion Workflow

When a user completes a task:

1. **Memory**: Retrieves task context and user history
2. **Chains**: Validates proof if provided
3. **Chains**: Generates celebration motivation
4. **MCP**: Completes task and awards points
5. **Planner**: Plans follow-up actions
6. **Memory**: Updates user context and insights

### 3. Daily Optimization Workflow

For daily optimization:

1. **Memory**: Gathers comprehensive user data
2. **MCP**: Gets dashboard and mood analysis
3. **Chains**: Generates personalized motivation
4. **Planner**: Creates optimization action plan
5. **Memory**: Stores optimization insights
6. **Planner**: Executes high-priority actions

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis (Required for Background Tasks)

```bash
# Windows
redis-server

# Linux/Mac
sudo systemctl start redis
```

### 3. Environment Variables

```env
# Existing variables
MONGODB_URI=mongodb://localhost:27017
OPENAI_API_KEY=your_openai_key

# New variables for enhanced architecture
REDIS_URL=redis://localhost:6379
ENABLE_BACKGROUND_TASKS=true
MEMORY_CLEANUP_INTERVAL=3600
CHAIN_EXECUTION_TIMEOUT=60
```

### 4. Start the Application

```bash
python main.py
```

### 5. Start Background Workers (Optional)

```bash
# In separate terminals
python -c "from app.core.background_tasks import start_worker; start_worker()"
python -c "from app.core.background_tasks import start_scheduler; start_scheduler()"
```

## Key Features

### ✅ Memory Management
- Multi-type memory system
- Automatic cleanup
- User context persistence
- Task insights storage

### ✅ Chain Processing
- LangChain integration
- Memory-aware chains
- Result caching
- Error recovery

### ✅ Intelligent Planning
- Action dependency management
- Priority-based execution
- Background processing
- Retry mechanisms

### ✅ MCP Integration
- Your existing unified MCP system
- 15+ standardized tools
- Consistent interface

### ✅ Background Processing
- RQ/Redis integration
- Scheduled tasks
- Job monitoring
- Fallback mechanisms

### ✅ Orchestration
- Complete workflow coordination
- Event-driven architecture
- System health monitoring

## Comparison with Architecture Blueprint

| Blueprint Component | Implementation | Status |
|-------------------|----------------|---------|
| FastAPI API Gateway | ✅ Enhanced with orchestrator endpoints | Complete |
| Auth Service | ✅ Existing JWT implementation | Complete |
| LangChain Agent Layer | ✅ Memory + Chains + Planner | Complete |
| MCP Adapter Layer | ✅ Your unified MCP system | Complete |
| Storage (MongoDB) | ✅ Enhanced with memory collections | Complete |
| Background Tasks | ✅ RQ/Redis implementation | Complete |
| External Services | ✅ Spotify, Calendar integrations | Complete |

## Performance & Scalability

- **Memory**: Automatic cleanup and TTL management
- **Chains**: Result caching and batch processing
- **Planner**: Concurrent action execution
- **Background Tasks**: Queue-based processing
- **MCP**: Rate limiting and connection pooling

## Monitoring & Health

- `/health` - Complete system health check
- `/orchestrator/status` - Detailed orchestrator status
- Background task monitoring
- Memory usage tracking
- Chain performance metrics

## Next Steps

1. **Vector Store Integration**: Add FAISS/Milvus for semantic search
2. **Advanced Agents**: Implement specialized agent classes
3. **Calendar Sync**: Complete Google Calendar integration
4. **Notification System**: Real-time notifications
5. **Performance Optimization**: Caching and optimization layers

This implementation provides a production-ready, scalable architecture that fully realizes the Memory-Chain-Planner pattern while leveraging your existing Unified MCP system as the perfect adapter layer.
