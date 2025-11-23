# FocusForge Backend Architecture

## Overview

FocusForge implements a complete **Memory-Chain-Planner** architecture with **Model Context Protocol (MCP)** integration, built on FastAPI, LangChain, and MongoDB. This architecture provides intelligent task management, AI-powered productivity insights, and seamless integration with external services.

## Architecture Components

### 1. FastAPI Gateway Layer
- **Purpose**: Main API gateway and request orchestrator
- **Features**: 
  - RESTful API endpoints
  - WebSocket support for real-time updates
  - CORS middleware
  - Request validation and error handling
  - Health checks and system monitoring

### 2. Memory Layer
- **Components**:
  - **Short-term Memory**: Temporary data (1 hour TTL)
  - **Working Memory**: Active session data (24 hour TTL)
  - **Long-term Memory**: Persistent user data (no expiry)
  - **Semantic Memory**: Vector-based similarity search using FAISS
- **Storage**: MongoDB with automatic cleanup and TTL management
- **Features**: 
  - User context persistence
  - Task insights storage
  - Semantic search capabilities
  - Memory type-specific configurations

### 3. Chain Layer (LangChain Integration)
- **Purpose**: AI-powered task processing and analysis
- **Chains**:
  - **Task Breakdown**: Decompose complex tasks into manageable blocks
  - **Task Analysis**: Analyze task complexity and requirements
  - **Motivation**: Generate personalized motivational content
  - **Proof Validation**: Validate task completion proofs using AI
- **Features**:
  - OpenAI GPT-4 integration
  - Memory-aware context processing
  - Fallback mechanisms for reliability
  - Result caching and optimization

### 4. Planner Layer
- **Purpose**: Intelligent action planning and coordination
- **Features**:
  - **Action Types**: Task management, mood tracking, gamification, integrations
  - **Priority Levels**: Critical, High, Medium, Low, Background
  - **Dependency Management**: Action execution order and prerequisites
  - **Retry Logic**: Automatic retry with exponential backoff
  - **Resource Management**: Concurrent execution limits and scheduling

### 5. MCP Adapter Layer
- **Purpose**: Unified tool interface for external service integration
- **Tool Categories**:
  - **AI Agents**: Task breakdown, analysis, motivation, proof validation
  - **Task Management**: Create, retrieve, start, complete tasks
  - **Mood Tracking**: Log mood, analyze patterns
  - **Gamification**: Points, rewards, user profiles
  - **Integrations**: Spotify, Calendar, external APIs
- **Features**:
  - Standardized tool interface
  - Parameter validation
  - Error handling and fallbacks
  - Service discovery and status monitoring

### 6. Background Task System
- **Purpose**: Asynchronous processing and scheduled operations
- **Technology**: Redis Queue (RQ) with fallback mechanisms
- **Features**:
  - Task scheduling and queuing
  - Recurring task management
  - Background workflow processing
  - Job monitoring and cancellation
  - Graceful degradation when Redis unavailable

## Data Flow

### Task Creation Workflow
1. **Request**: User creates task via API
2. **Memory**: Retrieve user context and similar tasks
3. **Chain**: Execute task analysis and breakdown chains
4. **Planner**: Create execution plan with dependencies
5. **MCP**: Execute task creation using unified tools
6. **Storage**: Store workflow results in memory
7. **Response**: Return task with AI insights and breakdown

### Task Completion Workflow
1. **Request**: User completes task with optional proof
2. **Memory**: Retrieve task context and user history
3. **Chain**: Validate proof using AI (if provided)
4. **MCP**: Complete task and award points
5. **Planner**: Plan follow-up actions
6. **Storage**: Update completion insights
7. **Response**: Return validation results and motivation

## API Endpoints

### Core Endpoints
- `/api/v1/orchestrator/*` - Memory-Chain-Planner orchestration
- `/api/v1/mcp/*` - MCP tool access and management
- `/api/v1/tasks/*` - Task management
- `/api/v1/users/*` - User management
- `/api/v1/mood/*` - Mood tracking
- `/api/v1/analytics/*` - Analytics and insights
- `/api/v1/spotify/*` - Spotify integration
- `/api/v1/store/*` - Gamification store
- `/api/v1/calendar/*` - Calendar management
- `/api/v1/pomodoro/*` - Focus session management

### Orchestrator Endpoints
- `POST /orchestrator/tasks/create-enhanced` - Enhanced task creation
- `POST /orchestrator/tasks/complete-enhanced` - Enhanced task completion
- `POST /orchestrator/daily-optimization` - Daily optimization
- `POST /orchestrator/focus-session` - Focus session management
- `GET /orchestrator/planner/actions/{user_id}` - Get planned actions
- `POST /orchestrator/planner/execute/{user_id}` - Execute ready actions

### MCP Tool Endpoints
- `GET /mcp/tools` - List available tools
- `POST /mcp/tools/{tool_name}` - Execute specific tool
- `GET /mcp/status` - MCP system status
- `POST /mcp/ai/task-breakdown` - AI task breakdown
- `POST /mcp/ai/motivation` - AI motivation coach
- `POST /mcp/ai/ritual-suggestion` - AI ritual suggestions

## Database Schema

### Collections
- **users**: User profiles and preferences
- **tasks**: Task definitions and metadata
- **task_blocks**: Individual work blocks
- **mood_logs**: User mood tracking data
- **store_items**: Gamification store items
- **user_profiles**: User points and achievements
- **memory_short_term**: Short-term memory storage
- **memory_working**: Working memory storage
- **memory_long_term**: Long-term memory storage
- **memory_semantic**: Semantic memory storage
- **vector_store**: FAISS vector embeddings
- **calendar_events**: Calendar event storage
- **background_jobs**: Background task tracking

### Indexes
- User ID on all user-related collections
- Timestamp indexes for temporal queries
- Text indexes for search functionality
- Vector indexes for semantic similarity

## Security Features

### Authentication & Authorization
- JWT-based authentication
- User ID validation on all endpoints
- Role-based access control (future enhancement)
- API key management for external services

### Data Protection
- User data isolation
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure environment variable handling

## Performance Optimizations

### Caching Strategy
- Chain execution results (30-minute TTL)
- User context data (session-based)
- Vector search results (configurable TTL)
- Background task results (job-based)

### Database Optimization
- Connection pooling with Motor
- Indexed queries for common operations
- Aggregation pipelines for analytics
- TTL-based automatic cleanup

### Background Processing
- Asynchronous task execution
- Queue-based workload distribution
- Graceful degradation when Redis unavailable
- Configurable concurrency limits

## Monitoring & Health Checks

### Health Endpoints
- `/health` - Comprehensive system health
- `/orchestrator/status` - Orchestrator status
- `/mcp/status` - MCP system status

### Metrics
- System component status
- Memory usage and cleanup
- Background task statistics
- Vector store performance
- API response times

### Logging
- Structured logging with correlation IDs
- Error tracking and alerting
- Performance monitoring
- Debug information for development

## Deployment & Scaling

### Containerization
- Docker-based deployment
- Multi-stage builds for optimization
- Health check integration
- Environment-specific configurations

### Infrastructure
- MongoDB for persistent storage
- Redis for caching and queuing
- Horizontal scaling support
- Load balancing ready

### Environment Configuration
- Development: Mock external services, debug logging
- Testing: In-memory databases, test fixtures
- Production: Real external services, performance monitoring

## External Integrations

### AI Services
- OpenAI GPT-4 for natural language processing
- OpenAI embeddings for semantic search
- Configurable model parameters and fallbacks

### Productivity Tools
- Spotify for focus music and playlists
- Calendar systems for scheduling (Google Calendar ready)
- Email and notification services (future)

### Analytics & Monitoring
- Performance metrics collection
- User behavior analytics
- System health monitoring
- Error tracking and reporting

## Development Workflow

### Code Organization
- **app/core/**: Core architecture components
- **app/services/**: Business logic services
- **app/api/**: API endpoint definitions
- **app/models/**: Data models and schemas
- **app/utils/**: Utility functions and helpers

### Testing Strategy
- Unit tests for core components
- Integration tests for API endpoints
- Mock external services for testing
- Performance testing for critical paths

### Code Quality
- Type hints throughout codebase
- Comprehensive error handling
- Logging and monitoring
- Documentation and examples

## Future Enhancements

### Planned Features
- Advanced semantic search with multiple embedding models
- Machine learning-based user behavior prediction
- Real-time collaboration features
- Advanced calendar integration (Google, Outlook)
- Mobile app backend support
- Advanced analytics and reporting

### Scalability Improvements
- Microservices architecture
- Event-driven communication
- Advanced caching strategies
- Database sharding and replication
- Kubernetes deployment support

## Getting Started

### Prerequisites
- Python 3.11+
- MongoDB 6.0+
- Redis 7.0+
- OpenAI API key

### Installation
```bash
cd backend
pip install -e .
```

### Configuration
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running
```bash
# Development
python main.py

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker-compose -f docker-compose.backend.yml up -d
```

## Architecture Benefits

### 1. **Intelligence**: AI-powered task management and insights
### 2. **Scalability**: Modular design with clear separation of concerns
### 3. **Reliability**: Comprehensive error handling and fallback mechanisms
### 4. **Maintainability**: Clean architecture with well-defined interfaces
### 5. **Extensibility**: Easy to add new tools and integrations
### 6. **Performance**: Optimized for speed with intelligent caching
### 7. **Monitoring**: Comprehensive health checks and metrics
### 8. **Security**: Secure by design with proper validation

This architecture provides a solid foundation for building intelligent, scalable productivity applications while maintaining code quality and operational excellence.
