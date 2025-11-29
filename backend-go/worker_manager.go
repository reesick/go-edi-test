package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"

	"github.com/google/uuid"
)

const pythonBaseURL = "http://localhost:8000"

// Data structures
type RunState struct {
	RunID           string                   `json:"runId"`
	Trace           []map[string]interface{} `json:"trace"`
	CurrentStep     int                      `json:"currentStep"`
	BehaviorSignals map[int]*BehaviorSignal  `json:"behaviorSignals"`
}

type BehaviorSignal struct {
	PauseDuration    float64 `json:"pauseDuration"`
	ReplayCount      int     `json:"replayCount"`
	SpeedMultiplier  float64 `json:"speedMultiplier"`
	HoverIndex       *int    `json:"hoverIndex,omitempty"`
	ScrollDepth      *int    `json:"scrollDepth,omitempty"`
}

// In-memory storage
var (
	runs   = make(map[string]*RunState)
	runsMu sync.RWMutex
)

// Call Python /execute endpoint
func callPythonExecute(algorithmID string, array []int) ([]map[string]interface{}, error) {
	requestBody := map[string]interface{}{
		"algorithmId": algorithmID,
		"array":       array,
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(pythonBaseURL+"/execute", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to call Python backend: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Python backend returned error: %s", string(body))
	}

	var result struct {
		Trace []map[string]interface{} `json:"trace"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result.Trace, nil
}

// Call Python /explain-step endpoint
func callPythonExplain(frame map[string]interface{}, userBehavior map[string]interface{}) (map[string]interface{}, error) {
	requestBody := map[string]interface{}{
		"frame":        frame,
		"userBehavior": userBehavior,
	}

	jsonData, err := json.Marshal(requestBody)
	if err != nil {
		return nil, err
	}

	resp, err := http.Post(pythonBaseURL+"/explain-step", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to call Python backend: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("Python backend returned error: %s", string(body))
	}

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result, nil
}

// Get or create behavior signal for a step
func getBehaviorSignal(runID string, stepIndex int) map[string]interface{} {
	runsMu.RLock()
	run, exists := runs[runID]
	runsMu.RUnlock()

	if !exists {
		return map[string]interface{}{
			"pauseDuration":   0.0,
			"replayCount":     0,
			"speedMultiplier": 1.0,
		}
	}

	if signal, ok := run.BehaviorSignals[stepIndex]; ok {
		return map[string]interface{}{
			"pauseDuration":   signal.PauseDuration,
			"replayCount":     signal.ReplayCount,
			"speedMultiplier": signal.SpeedMultiplier,
			"hoverIndex":      signal.HoverIndex,
			"scrollDepth":     signal.ScrollDepth,
		}
	}

	return map[string]interface{}{
		"pauseDuration":   0.0,
		"replayCount":     0,
		"speedMultiplier": 1.0,
	}
}

// Stream trace frames via WebSocket
func streamRun(runID string, conn *websocketConnection, speedMultiplier float64) error {
	runsMu.RLock()
	run, exists := runs[runID]
	runsMu.RUnlock()

	if !exists {
		return fmt.Errorf("run not found: %s", runID)
	}

	// Calculate frame delay based on speed multiplier
	baseDelay := 1000.0 // milliseconds
	frameDelay := time.Duration(baseDelay/speedMultiplier) * time.Millisecond

	for i, frame := range run.Trace {
		// Send TRACE message
		traceMsg := map[string]interface{}{
			"type": "TRACE",
			"data": frame,
		}
		if err := conn.WriteJSON(traceMsg); err != nil {
			return fmt.Errorf("failed to send trace: %w", err)
		}

		// Get behavior signal
		userBehavior := getBehaviorSignal(runID, i)
		userBehavior["speedMultiplier"] = speedMultiplier

		// Call AI explainer
		explanation, err := callPythonExplain(frame, userBehavior)
		if err != nil {
			fmt.Printf("Error getting explanation: %v\n", err)
			// Send fallback explanation
			explanation = map[string]interface{}{
				"mode":                "conceptual",
				"explanation":         "Processing this step...",
				"short_hint":          "Watch the visualization",
				"confidence_estimate": "medium",
				"followup_question":   "",
			}
		}

		// Send EXPLANATION message
		explainMsg := map[string]interface{}{
			"type": "EXPLANATION",
			"data": explanation,
		}
		if err := conn.WriteJSON(explainMsg); err != nil {
			return fmt.Errorf("failed to send explanation: %w", err)
		}

		// Wait before next frame
		time.Sleep(frameDelay)
	}

	// Send END message
	endMsg := map[string]interface{}{
		"type": "END",
		"data": map[string]interface{}{
			"message": "Visualization complete",
		},
	}
	return conn.WriteJSON(endMsg)
}

// Create new run
func createRun(algorithmID string, array []int) (*RunState, error) {
	// Call Python to get trace
	trace, err := callPythonExecute(algorithmID, array)
	if err != nil {
		return nil, err
	}

	// Create run state
	runID := uuid.New().String()
	run := &RunState{
		RunID:           runID,
		Trace:           trace,
		CurrentStep:     0,
		BehaviorSignals: make(map[int]*BehaviorSignal),
	}

	// Store run
	runsMu.Lock()
	runs[runID] = run
	runsMu.Unlock()

	return run, nil
}
