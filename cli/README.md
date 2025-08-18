# FocusForge CLI

A beautiful, interactive command-line interface for FocusForge - your AI-powered productivity assistant.

## Features

🚀 **Interactive UI** - Beautiful, intuitive command-line interface with emojis and colors
📋 **Task Management** - Create, view, edit, and delete tasks with AI-powered breakdown
🎯 **Focus Sessions** - Start and manage focused work sessions
😊 **Mood Tracking** - Log and analyze your mood patterns
🏆 **Gamification** - View points, achievements, and rewards
📊 **Analytics** - Get insights into your productivity patterns
🎵 **Spotify Integration** - Control your focus music
⚙️ **Settings** - Configure API endpoints and preferences

## Installation

### Prerequisites
- Go 1.21 or later
- FocusForge backend running (default: http://localhost:8000)

### Build and Run

1. **Clone and navigate to the CLI directory:**
   ```bash
   cd cli
   ```

2. **Install dependencies:**
   ```bash
   go mod tidy
   ```

3. **Build the CLI:**
   ```bash
   go build -o focusforge-cli
   ```

4. **Run the CLI:**
   ```bash
   ./focusforge-cli
   ```

### Development Mode

For development with auto-reload:
```bash
go install github.com/cosmtrek/air@latest
air
```

## Usage

### Getting Started

1. **Launch the CLI:**
   ```bash
   ./focusforge-cli
   ```

2. **Enter your User ID:**
   - Use your actual user ID from the backend
   - Or press Enter to use 'default'

3. **Navigate the Menu:**
   - Use arrow keys to navigate
   - Press Enter to select
   - Use 'q' to go back

### Main Menu Options

- **📋 Task Management** - Create, view, and manage tasks
- **🎯 Focus Sessions** - Start and manage work sessions
- **😊 Mood Tracking** - Log and track your mood
- **🏆 Gamification & Rewards** - View points and achievements
- **📊 Analytics & Insights** - Productivity analytics
- **🎵 Spotify Integration** - Control focus music
- **⚙️ Settings** - Configure the CLI
- **❌ Exit** - Close the application

### Task Management

#### Creating a Task
1. Select "📋 Task Management" → "➕ Create New Task"
2. Enter task details:
   - Title (required)
   - Description (optional)
   - Duration in minutes
   - Category (work, personal, learning, health, other)
   - Priority (low, medium, high, urgent)
   - AI breakdown option

#### Viewing Tasks
- Select "📋 Task Management" → "📝 List My Tasks"
- Tasks are displayed with status indicators:
  - 🟡 Pending
  - 🔵 In Progress
  - 🟢 Completed

### Mood Tracking

#### Logging Mood
1. Select "😊 Mood Tracking" → "😊 Log Mood"
2. Choose your current feeling from 12 options
3. Rate intensity (1-10)
4. Add optional notes

### Focus Sessions

#### Starting a Session
1. Select "🎯 Focus Sessions" → "▶️ Start Focus Session"
2. Choose task and duration
3. Start your focused work period

## Configuration

### API Settings

The CLI connects to the FocusForge backend API. Default settings:
- **API URL:** http://localhost:8000
- **User ID:** Set on first run

To change settings:
1. Go to "⚙️ Settings" → "🔧 API Configuration"
2. Update API URL if needed

### Environment Variables

You can set these environment variables:
```bash
export FOCUSFORGE_API_URL="http://your-backend:8000"
export FOCUSFORGE_USER_ID="your-user-id"
```

## Development

### Project Structure

```
cli/
├── main.go          # Main CLI application
├── go.mod           # Go module file
├── go.sum           # Dependency checksums
└── README.md        # This file
```

### Adding New Features

1. **New Menu Items:**
   - Add to the appropriate menu array
   - Implement the corresponding method
   - Add case handling in the switch statement

2. **API Integration:**
   - Create HTTP client functions
   - Handle API responses and errors
   - Update mock data with real API calls

3. **UI Enhancements:**
   - Use color package for styling
   - Add emojis for visual appeal
   - Implement progress indicators

### Dependencies

- **github.com/fatih/color** - Terminal colors and styling
- **github.com/manifoldco/promptui** - Interactive prompts and menus

## Troubleshooting

### Common Issues

1. **"Connection refused" errors:**
   - Ensure FocusForge backend is running
   - Check API URL in settings
   - Verify network connectivity

2. **"User not found" errors:**
   - Verify user ID exists in backend
   - Check user authentication

3. **Build errors:**
   - Ensure Go version is 1.21+
   - Run `go mod tidy` to fix dependencies

### Debug Mode

For debugging, you can add logging:
```go
import "log"

log.Printf("Debug: %s", "message")
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the main repository for details.

## Support

For support and questions:
- Check the main FocusForge documentation
- Open an issue on GitHub
- Join the community discussions

---

Made with ❤️ by the FocusForge team
