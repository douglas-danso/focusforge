package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// APIClient handles communication with the FocusForge backend
type APIClient struct {
	baseURL    string
	httpClient *http.Client
	userID     string
}

// NewAPIClient creates a new API client
func NewAPIClient(baseURL, userID string) *APIClient {
	return &APIClient{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
		userID: userID,
	}
}

// Task represents a task in the system
type Task struct {
	ID              string    `json:"id,omitempty"`
	Title           string    `json:"title"`
	Description     string    `json:"description,omitempty"`
	DurationMinutes int       `json:"duration_minutes"`
	Category        string    `json:"category,omitempty"`
	Priority        string    `json:"priority,omitempty"`
	Status          string    `json:"status,omitempty"`
	CreatedAt       string    `json:"created_at,omitempty"`
	UpdatedAt       string    `json:"updated_at,omitempty"`
}

// TaskCreateRequest represents a task creation request
type TaskCreateRequest struct {
	Title           string `json:"title"`
	Description     string `json:"description,omitempty"`
	DurationMinutes int    `json:"duration_minutes"`
	Category        string `json:"category,omitempty"`
	Priority        string `json:"priority,omitempty"`
}

// TaskResponse represents the response from task operations
type TaskResponse struct {
	Success bool        `json:"success"`
	Task    *Task      `json:"task,omitempty"`
	Tasks   []*Task    `json:"tasks,omitempty"`
	Error   string     `json:"error,omitempty"`
	Message string     `json:"message,omitempty"`
	Count   int        `json:"count,omitempty"`
	Stats   *TaskStats `json:"stats,omitempty"`
}

// TaskStats represents task statistics
type TaskStats struct {
	TotalTasks       int     `json:"total_tasks"`
	CompletedTasks   int     `json:"completed_tasks"`
	PendingTasks     int     `json:"pending_tasks"`
	InProgressTasks  int     `json:"in_progress_tasks"`
	CompletionRate   float64 `json:"completion_rate"`
	TotalMinutes     int     `json:"total_minutes_planned"`
	TotalTokens      int     `json:"total_tokens_earned"`
	AvgDifficulty    float64 `json:"avg_difficulty"`
}

// MoodLog represents a mood entry
type MoodLog struct {
	ID        string `json:"id,omitempty"`
	Feeling   string `json:"feeling"`
	Intensity int    `json:"intensity,omitempty"`
	Note      string `json:"note,omitempty"`
	Timestamp string `json:"timestamp,omitempty"`
}

// MoodLogRequest represents a mood logging request
type MoodLogRequest struct {
	Feeling   string `json:"feeling"`
	Intensity int    `json:"intensity,omitempty"`
	Note      string `json:"note,omitempty"`
}

// MoodResponse represents the response from mood operations
type MoodResponse struct {
	Success   bool      `json:"success"`
	MoodLog   *MoodLog `json:"mood_log,omitempty"`
	MoodLogs  []*MoodLog `json:"mood_logs,omitempty"`
	Error     string    `json:"error,omitempty"`
	Message   string    `json:"message,omitempty"`
	Patterns  map[string]interface{} `json:"patterns,omitempty"`
}

// DashboardResponse represents the dashboard data
type DashboardResponse struct {
	Success        bool        `json:"success"`
	ActiveTasks    interface{} `json:"active_tasks,omitempty"`
	UpcomingTasks  interface{} `json:"upcoming_tasks,omitempty"`
	NextBlock      interface{} `json:"next_block,omitempty"`
	Stats          *TaskStats  `json:"stats,omitempty"`
	Error          string      `json:"error,omitempty"`
}

// CreateTask creates a new task
func (c *APIClient) CreateTask(taskReq TaskCreateRequest) (*TaskResponse, error) {
	url := fmt.Sprintf("%s/api/v1/tasks/", c.baseURL)
	
	// Add user_id to request
	requestData := map[string]interface{}{
		"title":            taskReq.Title,
		"description":      taskReq.Description,
		"duration_minutes": taskReq.DurationMinutes,
		"category":         taskReq.Category,
		"priority":         taskReq.Priority,
	}
	
	jsonData, err := json.Marshal(requestData)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}
	
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	
	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", c.userID)
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()
	
	var taskResp TaskResponse
	if err := json.NewDecoder(resp.Body).Decode(&taskResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}
	
	return &taskResp, nil
}

// GetTasks retrieves tasks for the user
func (c *APIClient) GetTasks(status, category string, limit int) (*TaskResponse, error) {
	url := fmt.Sprintf("%s/api/v1/tasks/", c.baseURL)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	
	// Set headers
	req.Header.Set("Authorization", c.userID)
	
	// Add query parameters
	q := req.URL.Query()
	if status != "" {
		q.Add("status", status)
	}
	if category != "" {
		q.Add("category", category)
	}
	if limit > 0 {
		q.Add("limit", fmt.Sprintf("%d", limit))
	}
	req.URL.RawQuery = q.Encode()
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()
	
	var taskResp TaskResponse
	if err := json.NewDecoder(resp.Body).Decode(&taskResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}
	
	return &taskResp, nil
}

// GetDashboard retrieves the user dashboard
func (c *APIClient) GetDashboard() (*DashboardResponse, error) {
	url := fmt.Sprintf("%s/api/v1/tasks/dashboard", c.baseURL)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	
	// Set headers
	req.Header.Set("Authorization", c.userID)
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()
	
	var dashboardResp DashboardResponse
	if err := json.NewDecoder(resp.Body).Decode(&dashboardResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}
	
	return &dashboardResp, nil
}

// LogMood logs a mood entry
func (c *APIClient) LogMood(moodReq MoodLogRequest) (*MoodResponse, error) {
	url := fmt.Sprintf("%s/api/v1/mood/", c.baseURL)
	
	jsonData, err := json.Marshal(moodReq)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %v", err)
	}
	
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	
	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", c.userID)
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()
	
	var moodResp MoodResponse
	if err := json.NewDecoder(resp.Body).Decode(&moodResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}
	
	return &moodResp, nil
}

// GetMoodLogs retrieves mood logs for the user
func (c *APIClient) GetMoodLogs(limit int) (*MoodResponse, error) {
	url := fmt.Sprintf("%s/api/v1/mood/", c.baseURL)
	
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	
	// Set headers
	req.Header.Set("Authorization", c.userID)
	
	// Add query parameters
	q := req.URL.Query()
	if limit > 0 {
		q.Add("limit", fmt.Sprintf("%d", limit))
	}
	req.URL.RawQuery = q.Encode()
	
	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()
	
	var moodResp MoodResponse
	if err := json.NewDecoder(resp.Body).Decode(&moodResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %v", err)
	}
	
	return &moodResp, nil
}

// HealthCheck checks if the API is accessible
func (c *APIClient) HealthCheck() error {
	url := fmt.Sprintf("%s/health", c.baseURL)
	
	resp, err := c.httpClient.Get(url)
	if err != nil {
		return fmt.Errorf("health check failed: %v", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("health check failed with status: %d", resp.StatusCode)
	}
	
	return nil
}
