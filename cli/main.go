package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
	"strconv"
	"time"

	"github.com/fatih/color"
	"github.com/manifoldco/promptui"
)

type FocusForgeCLI struct {
	apiURL    string
	userID    string
	isRunning bool
	apiClient *APIClient
}

func main() {
	cli := &FocusForgeCLI{
		apiURL:    "http://localhost:8000",
		userID:    "",
		isRunning: true,
		apiClient: nil,
	}

	// Show welcome message
	cli.showWelcome()

	// Initialize API client
	cli.apiClient = NewAPIClient(cli.apiURL, cli.userID)

	// Check API health
	if err := cli.apiClient.HealthCheck(); err != nil {
		color.Yellow("⚠️  Warning: Could not connect to FocusForge backend")
		color.Yellow("   Make sure the backend is running at: %s", cli.apiURL)
		color.Yellow("   Some features may not work properly")
		fmt.Println()
	} else {
		color.Green("✅ Connected to FocusForge backend successfully!")
		fmt.Println()
	}

	// Main menu loop
	for cli.isRunning {
		cli.showMainMenu()
	}
}

func (c *FocusForgeCLI) showWelcome() {
	color.Cyan("╔══════════════════════════════════════════════════════════════╗")
	color.Cyan("║                    🚀 FocusForge CLI 🚀                    ║")
	color.Cyan("║              Your AI-Powered Productivity Assistant         ║")
	color.Cyan("╚══════════════════════════════════════════════════════════════╝")
	fmt.Println()
	
	color.Yellow("Welcome to FocusForge! Let's get you set up for maximum productivity.")
	fmt.Println()
	
	// Get user ID
	c.getUserID()
}

func (c *FocusForgeCLI) getUserID() {
	prompt := promptui.Prompt{
		Label: "Enter your User ID (or press Enter for 'default')",
		Default: "default",
	}
	
	userID, err := prompt.Run()
	if err != nil {
		color.Red("Error getting user ID: %v", err)
		c.userID = "default"
	} else {
		c.userID = userID
	}
	
	color.Green("✓ User ID set to: %s", c.userID)
	fmt.Println()
}

func (c *FocusForgeCLI) showMainMenu() {
	menuItems := []string{
		"📋 Task Management",
		"🎯 Focus Sessions",
		"😊 Mood Tracking",
		"🏆 Gamification & Rewards",
		"📊 Analytics & Insights",
		"🎵 Spotify Integration",
		"⚙️  Settings",
		"❌ Exit",
	}
	
	prompt := promptui.Select{
		Label: "What would you like to do?",
		Items: menuItems,
		Size:  10,
	}
	
	_, result, err := prompt.Run()
	if err != nil {
		color.Red("Error selecting menu item: %v", err)
		return
	}
	
	switch result {
	case "📋 Task Management":
		c.showTaskManagement()
	case "🎯 Focus Sessions":
		c.showFocusSessions()
	case "😊 Mood Tracking":
		c.showMoodTracking()
	case "🏆 Gamification & Rewards":
		c.showGamification()
	case "📊 Analytics & Insights":
		c.showAnalytics()
	case "🎵 Spotify Integration":
		c.showSpotifyIntegration()
	case "⚙️  Settings":
		c.showSettings()
	case "❌ Exit":
		c.exit()
	}
}

func (c *FocusForgeCLI) showTaskManagement() {
	for {
		menuItems := []string{
			"➕ Create New Task",
			"📝 List My Tasks",
			"🔍 View Task Details",
			"✏️  Edit Task",
			"🗑️  Delete Task",
			"📊 Task Dashboard",
			"🔙 Back to Main Menu",
		}
		
		prompt := promptui.Select{
			Label: "Task Management - What would you like to do?",
			Items: menuItems,
			Size:  10,
		}
		
		_, result, err := prompt.Run()
		if err != nil {
			color.Red("Error selecting menu item: %v", err)
			return
		}
		
		switch result {
		case "➕ Create New Task":
			c.createNewTask()
		case "📝 List My Tasks":
			c.listTasks()
		case "🔍 View Task Details":
			c.viewTaskDetails()
		case "✏️  Edit Task":
			c.editTask()
		case "🗑️  Delete Task":
			c.deleteTask()
		case "📊 Task Dashboard":
			c.showTaskDashboard()
		case "🔙 Back to Main Menu":
			return
		}
	}
}

func (c *FocusForgeCLI) createNewTask() {
	color.Cyan("🎯 Creating New Task")
	fmt.Println()
	
	// Get task title
	titlePrompt := promptui.Prompt{
		Label: "Task Title",
		Validate: func(input string) error {
			if len(strings.TrimSpace(input)) == 0 {
				return fmt.Errorf("title cannot be empty")
			}
			return nil
		},
	}
	title, err := titlePrompt.Run()
	if err != nil {
		color.Red("Error getting task title: %v", err)
		return
	}
	
	// Get task description
	descPrompt := promptui.Prompt{
		Label: "Task Description (optional)",
	}
	description, _ := descPrompt.Run()
	
	// Get duration
	durationPrompt := promptui.Prompt{
		Label: "Duration in minutes",
		Validate: func(input string) error {
			if len(strings.TrimSpace(input)) == 0 {
				return fmt.Errorf("duration cannot be empty")
			}
			return nil
		},
	}
	durationStr, err := durationPrompt.Run()
	if err != nil {
		color.Red("Error getting duration: %v", err)
		return
	}
	
	// Convert duration to int
	duration, err := strconv.Atoi(durationStr)
	if err != nil {
		color.Red("Error parsing duration: %v", err)
		return
	}
	
	// Get category
	categoryPrompt := promptui.Select{
		Label: "Task Category",
		Items: []string{"work", "personal", "learning", "health", "other"},
	}
	_, category, err := categoryPrompt.Run()
	if err != nil {
		color.Red("Error getting category: %v", err)
		return
	}
	
	// Get priority
	priorityPrompt := promptui.Select{
		Label: "Task Priority",
		Items: []string{"low", "medium", "high", "urgent"},
	}
	_, priority, err := priorityPrompt.Run()
	if err != nil {
		color.Red("Error getting priority: %v", err)
		return
	}
	
	// Auto-breakdown option
	breakdownPrompt := promptui.Select{
		Label: "Use AI to break down task into blocks?",
		Items: []string{"Yes", "No"},
	}
	_, breakdownChoice, err := breakdownPrompt.Run()
	if err != nil {
		color.Red("Error getting breakdown choice: %v", err)
		return
	}
	
	autoBreakdown := breakdownChoice == "Yes"
	
	color.Yellow("Creating task...")
	
	// Create task request
	taskReq := TaskCreateRequest{
		Title:           title,
		Description:     description,
		DurationMinutes: duration,
		Category:        category,
		Priority:        priority,
	}
	
	// Make API call to create task
	if c.apiClient != nil {
		resp, err := c.apiClient.CreateTask(taskReq)
		if err != nil {
			color.Red("❌ Failed to create task: %v", err)
			fmt.Println()
			fmt.Println("Press Enter to continue...")
			bufio.NewReader(os.Stdin).ReadString('\n')
			return
		}
		
		if resp.Success {
			color.Green("✓ Task created successfully!")
			fmt.Println()
			color.Cyan("Task Details:")
			if resp.Task != nil {
				fmt.Printf("  ID: %s\n", resp.Task.ID)
				fmt.Printf("  Title: %s\n", resp.Task.Title)
				fmt.Printf("  Description: %s\n", resp.Task.Description)
				fmt.Printf("  Duration: %d minutes\n", resp.Task.DurationMinutes)
				fmt.Printf("  Category: %s\n", resp.Task.Category)
				fmt.Printf("  Priority: %s\n", resp.Task.Priority)
				fmt.Printf("  Status: %s\n", resp.Task.Status)
			}
			fmt.Printf("  AI Breakdown: %t\n", autoBreakdown)
		} else {
			color.Red("❌ Failed to create task: %s", resp.Error)
		}
	} else {
		color.Yellow("⚠️  API client not available - using mock data")
		color.Green("✓ Task created successfully! (mock)")
		fmt.Println()
		color.Cyan("Task Details:")
		fmt.Printf("  Title: %s\n", title)
		fmt.Printf("  Description: %s\n", description)
		fmt.Printf("  Duration: %d minutes\n", duration)
		fmt.Printf("  Category: %s\n", category)
		fmt.Printf("  Priority: %s\n", priority)
		fmt.Printf("  AI Breakdown: %t\n", autoBreakdown)
	}
	
	fmt.Println()
	
	// Wait for user to continue
	fmt.Println("Press Enter to continue...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func (c *FocusForgeCLI) listTasks() {
	color.Cyan("📋 Your Tasks")
	fmt.Println()
	
	color.Yellow("Fetching your tasks...")
	
	if c.apiClient != nil {
		// Make API call to get tasks
		resp, err := c.apiClient.GetTasks("", "", 50)
		if err != nil {
			color.Red("❌ Failed to fetch tasks: %v", err)
			fmt.Println()
			fmt.Println("Press Enter to continue...")
			bufio.NewReader(os.Stdin).ReadString('\n')
			return
		}
		
		if resp.Success && resp.Tasks != nil {
			if len(resp.Tasks) == 0 {
				color.Yellow("No tasks found. Create your first task!")
			} else {
				for i, task := range resp.Tasks {
					statusColor := color.Green
					if task.Status == "pending" {
						statusColor = color.Yellow
					} else if task.Status == "in_progress" {
						statusColor = color.Cyan
					}
					
					fmt.Printf("%d. %s (%d min) - ", i+1, task.Title, task.DurationMinutes)
					statusColor(task.Status)
					fmt.Println()
				}
				
				if resp.Stats != nil {
					fmt.Println()
					color.Cyan("📊 Task Statistics:")
					fmt.Printf("  • Total Tasks: %d\n", resp.Stats.TotalTasks)
					fmt.Printf("  • Completed: %d\n", resp.Stats.CompletedTasks)
					fmt.Printf("  • In Progress: %d\n", resp.Stats.InProgressTasks)
					fmt.Printf("  • Pending: %d\n", resp.Stats.PendingTasks)
					fmt.Printf("  • Completion Rate: %.1f%%\n", resp.Stats.CompletionRate)
				}
			}
		} else {
			color.Red("❌ Failed to fetch tasks: %s", resp.Error)
		}
	} else {
		color.Yellow("⚠️  API client not available - showing mock data")
		
		// Mock data for now
		tasks := []map[string]string{
			{"id": "1", "title": "Complete project proposal", "status": "in_progress", "duration": "120"},
			{"id": "2", "title": "Review code changes", "status": "pending", "duration": "45"},
			{"id": "3", "title": "Team meeting", "status": "completed", "duration": "60"},
		}
		
		if len(tasks) == 0 {
			color.Yellow("No tasks found. Create your first task!")
		} else {
			for i, task := range tasks {
				statusColor := color.Green
				if task["status"] == "pending" {
					statusColor = color.Yellow
				} else if task["status"] == "in_progress" {
					statusColor = color.Cyan
				}
				
				fmt.Printf("%d. %s (%s min) - ", i+1, task["title"], task["duration"])
				statusColor(task["status"])
				fmt.Println()
			}
		}
	}
	
	fmt.Println()
	fmt.Println("Press Enter to continue...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func (c *FocusForgeCLI) viewTaskDetails() {
	color.Cyan("🔍 View Task Details")
	fmt.Println()
	
	// TODO: Implement task details view
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) editTask() {
	color.Cyan("✏️  Edit Task")
	fmt.Println()
	
	// TODO: Implement task editing
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) deleteTask() {
	color.Cyan("🗑️  Delete Task")
	fmt.Println()
	
	// TODO: Implement task deletion
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showTaskDashboard() {
	color.Cyan("📊 Task Dashboard")
	fmt.Println()
	
	color.Yellow("Loading your dashboard...")
	
	if c.apiClient != nil {
		// Make API call to get dashboard
		resp, err := c.apiClient.GetDashboard()
		if err != nil {
			color.Red("❌ Failed to load dashboard: %v", err)
			fmt.Println()
			fmt.Println("Press Enter to continue...")
			bufio.NewReader(os.Stdin).ReadString('\n')
			return
		}
		
		if resp.Success {
			if resp.Stats != nil {
				fmt.Println("📈 Task Statistics:")
				fmt.Printf("  • Total Tasks: %d\n", resp.Stats.TotalTasks)
				fmt.Printf("  • Completed: %d\n", resp.Stats.CompletedTasks)
				fmt.Printf("  • In Progress: %d\n", resp.Stats.InProgressTasks)
				fmt.Printf("  • Pending: %d\n", resp.Stats.PendingTasks)
				fmt.Printf("  • Completion Rate: %.1f%%\n", resp.Stats.CompletionRate)
				fmt.Printf("  • Total Minutes Planned: %d\n", resp.Stats.TotalMinutes)
				fmt.Printf("  • Total Tokens Earned: %d\n", resp.Stats.TotalTokens)
				fmt.Printf("  • Average Difficulty: %.1f\n", resp.Stats.AvgDifficulty)
			}
			
			// Show next block if available
			if resp.NextBlock != nil {
				fmt.Println()
				fmt.Println("🎯 Next Focus Block:")
				// TODO: Parse and display next block details
				fmt.Println("  • Ready to start next task block")
			}
			
			// Show active tasks if available
			if resp.ActiveTasks != nil {
				fmt.Println()
				fmt.Println("🔥 Active Tasks:")
				// TODO: Parse and display active tasks
				fmt.Println("  • You have active tasks in progress")
			}
		} else {
			color.Red("❌ Failed to load dashboard: %s", resp.Error)
		}
	} else {
		color.Yellow("⚠️  API client not available - showing mock data")
		
		// Mock dashboard data
		fmt.Println("📈 Task Statistics:")
		fmt.Println("  • Total Tasks: 15")
		fmt.Println("  • Completed: 8")
		fmt.Println("  • In Progress: 3")
		fmt.Println("  • Pending: 4")
		fmt.Println("  • Completion Rate: 53%")
		fmt.Println()
		
		fmt.Println("🎯 Current Focus:")
		fmt.Println("  • Active Task: Complete project proposal")
		fmt.Println("  • Time Remaining: 45 minutes")
		fmt.Println("  • Next Break: 15 minutes")
	}
	
	fmt.Println()
	fmt.Println("Press Enter to continue...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func (c *FocusForgeCLI) showFocusSessions() {
	for {
		menuItems := []string{
			"▶️  Start Focus Session",
			"⏸️  Current Session",
			"⏹️  End Session",
			"📊 Session History",
			"🔙 Back to Main Menu",
		}
		
		prompt := promptui.Select{
			Label: "Focus Sessions - What would you like to do?",
			Items: menuItems,
			Size:  10,
		}
		
		_, result, err := prompt.Run()
		if err != nil {
			color.Red("Error selecting menu item: %v", err)
			return
		}
		
		switch result {
		case "▶️  Start Focus Session":
			c.startFocusSession()
		case "⏸️  Current Session":
			c.showCurrentSession()
		case "⏹️  End Session":
			c.endSession()
		case "📊 Session History":
			c.showSessionHistory()
		case "🔙 Back to Main Menu":
			return
		}
	}
}

func (c *FocusForgeCLI) startFocusSession() {
	color.Cyan("🎯 Starting Focus Session")
	fmt.Println()
	
	// TODO: Implement focus session start
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showCurrentSession() {
	color.Cyan("⏸️  Current Session")
	fmt.Println()
	
	// TODO: Show current session status
	color.Yellow("No active session")
	fmt.Println()
}

func (c *FocusForgeCLI) endSession() {
	color.Cyan("⏹️  End Session")
	fmt.Println()
	
	// TODO: Implement session end
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showSessionHistory() {
	color.Cyan("📊 Session History")
	fmt.Println()
	
	// TODO: Show session history
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showMoodTracking() {
	for {
		menuItems := []string{
			"😊 Log Mood",
			"📊 Mood Trends",
			"🔍 Mood Analysis",
			"🔙 Back to Main Menu",
		}
		
		prompt := promptui.Select{
			Label: "Mood Tracking - What would you like to do?",
			Items: menuItems,
			Size:  10,
		}
		
		_, result, err := prompt.Run()
		if err != nil {
			color.Red("Error selecting menu item: %v", err)
			return
		}
		
		switch result {
		case "😊 Log Mood":
			c.logMood()
		case "📊 Mood Trends":
			c.showMoodTrends()
		case "🔍 Mood Analysis":
			c.showMoodAnalysis()
		case "🔙 Back to Main Menu":
			return
		}
	}
}

func (c *FocusForgeCLI) logMood() {
	color.Cyan("😊 Log Your Mood")
	fmt.Println()
	
	moodPrompt := promptui.Select{
		Label: "How are you feeling right now?",
		Items: []string{
			"😊 Happy", "😌 Content", "😤 Stressed", "😴 Tired",
			"😡 Angry", "😰 Anxious", "😔 Sad", "🤔 Confused",
			"😤 Frustrated", "😃 Excited", "😌 Relaxed", "😤 Overwhelmed",
		},
		Size: 12,
	}
	
	_, mood, err := moodPrompt.Run()
	if err != nil {
		color.Red("Error selecting mood: %v", err)
		return
	}
	
	// Extract feeling from emoji + text
	feeling := strings.TrimSpace(strings.Split(mood, " ")[1])
	
	intensityPrompt := promptui.Select{
		Label: "How intense is this feeling? (1-10)",
		Items: []string{"1", "2", "3", "4", "5", "6", "7", "8", "9", "10"},
	}
	
	_, intensityStr, err := intensityPrompt.Run()
	if err != nil {
		color.Red("Error selecting intensity: %v", err)
		return
	}
	
	intensity, _ := strconv.Atoi(intensityStr)
	
	notePrompt := promptui.Prompt{
		Label: "Any notes about your mood? (optional)",
	}
	note, _ := notePrompt.Run()
	
	color.Yellow("Logging your mood...")
	
	if c.apiClient != nil {
		// Create mood request
		moodReq := MoodLogRequest{
			Feeling:   feeling,
			Intensity: intensity,
			Note:      note,
		}
		
		// Make API call to log mood
		resp, err := c.apiClient.LogMood(moodReq)
		if err != nil {
			color.Red("❌ Failed to log mood: %v", err)
			fmt.Println()
			fmt.Println("Press Enter to continue...")
			bufio.NewReader(os.Stdin).ReadString('\n')
			return
		}
		
		if resp.Success {
			color.Green("✓ Mood logged successfully!")
			fmt.Println()
			color.Cyan("Mood Details:")
			if resp.MoodLog != nil {
				fmt.Printf("  ID: %s\n", resp.MoodLog.ID)
				fmt.Printf("  Feeling: %s\n", resp.MoodLog.Feeling)
				fmt.Printf("  Intensity: %d/10\n", resp.MoodLog.Intensity)
				if resp.MoodLog.Note != "" {
					fmt.Printf("  Notes: %s\n", resp.MoodLog.Note)
				}
				if resp.MoodLog.Timestamp != "" {
					fmt.Printf("  Timestamp: %s\n", resp.MoodLog.Timestamp)
				}
			}
			
			// Show patterns if available
			if resp.Patterns != nil {
				fmt.Println()
				color.Cyan("📊 Mood Patterns:")
				// TODO: Parse and display mood patterns
				fmt.Println("  • Your mood has been tracked")
			}
		} else {
			color.Red("❌ Failed to log mood: %s", resp.Error)
		}
	} else {
		color.Yellow("⚠️  API client not available - using mock data")
		color.Green("✓ Mood logged successfully! (mock)")
		fmt.Println()
		color.Cyan("Mood Details:")
		fmt.Printf("  Feeling: %s\n", feeling)
		fmt.Printf("  Intensity: %d/10\n", intensity)
		if note != "" {
			fmt.Printf("  Notes: %s\n", note)
		}
	}
	
	fmt.Println()
	
	// Wait for user to continue
	fmt.Println("Press Enter to continue...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func (c *FocusForgeCLI) showMoodTrends() {
	color.Cyan("📊 Mood Trends")
	fmt.Println()
	
	// TODO: Show mood trends
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showMoodAnalysis() {
	color.Cyan("🔍 Mood Analysis")
	fmt.Println()
	
	// TODO: Show mood analysis
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showGamification() {
	for {
		menuItems := []string{
			"💰 View Points & Level",
			"🏆 Achievements",
			"🛒 Store & Rewards",
			"📊 Progress Stats",
			"🔙 Back to Main Menu",
		}
		
		prompt := promptui.Select{
			Label: "Gamification - What would you like to do?",
			Items: menuItems,
			Size:  10,
		}
		
		_, result, err := prompt.Run()
		if err != nil {
			color.Red("Error selecting menu item: %v", err)
			return
		}
		
		switch result {
		case "💰 View Points & Level":
			c.showPointsAndLevel()
		case "🏆 Achievements":
			c.showAchievements()
		case "🛒 Store & Rewards":
			c.showStore()
		case "📊 Progress Stats":
			c.showProgressStats()
		case "🔙 Back to Main Menu":
			return
		}
	}
}

func (c *FocusForgeCLI) showPointsAndLevel() {
	color.Cyan("💰 Points & Level")
	fmt.Println()
	
	// TODO: Show points and level
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showAchievements() {
	color.Cyan("🏆 Achievements")
	fmt.Println()
	
	// TODO: Show achievements
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showStore() {
	color.Cyan("🛒 Store & Rewards")
	fmt.Println()
	
	// TODO: Show store
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showProgressStats() {
	color.Cyan("📊 Progress Stats")
	fmt.Println()
	
	// TODO: Show progress stats
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showAnalytics() {
	color.Cyan("📊 Analytics & Insights")
	fmt.Println()
	
	// TODO: Show analytics
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showSpotifyIntegration() {
	color.Cyan("🎵 Spotify Integration")
	fmt.Println()
	
	// TODO: Show Spotify integration
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showSettings() {
	for {
		menuItems := []string{
			"🔧 API Configuration",
			"👤 User Settings",
			"🎨 Display Options",
			"🔙 Back to Main Menu",
		}
		
		prompt := promptui.Select{
			Label: "Settings - What would you like to do?",
			Items: menuItems,
			Size:  10,
		}
		
		_, result, err := prompt.Run()
		if err != nil {
			color.Red("Error selecting menu item: %v", err)
			return
		}
		
		switch result {
		case "🔧 API Configuration":
			c.showAPIConfig()
		case "👤 User Settings":
			c.showUserSettings()
		case "🎨 Display Options":
			c.showDisplayOptions()
		case "🔙 Back to Main Menu":
			return
		}
	}
}

func (c *FocusForgeCLI) showAPIConfig() {
	color.Cyan("🔧 API Configuration")
	fmt.Println()
	
	fmt.Printf("Current API URL: %s\n", c.apiURL)
	fmt.Printf("Current User ID: %s\n", c.userID)
	fmt.Println()
	
	// TODO: Allow changing API URL
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showUserSettings() {
	color.Cyan("👤 User Settings")
	fmt.Println()
	
	// TODO: Show user settings
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) showDisplayOptions() {
	color.Cyan("🎨 Display Options")
	fmt.Println()
	
	// TODO: Show display options
	color.Yellow("Feature coming soon!")
	fmt.Println()
}

func (c *FocusForgeCLI) exit() {
	color.Yellow("👋 Thanks for using FocusForge CLI!")
	color.Yellow("Keep up the great work on your productivity journey!")
	fmt.Println()
	
	// Show a little animation
	for i := 0; i < 3; i++ {
		fmt.Print(".")
		time.Sleep(500 * time.Millisecond)
	}
	fmt.Println()
	
	c.isRunning = false
}
