package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for development
	},
}

type websocketConnection struct {
	*websocket.Conn
}

func (c *websocketConnection) WriteJSON(v interface{}) error {
	return c.Conn.WriteJSON(v)
}

// Enable CORS
func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

// POST /api/run - Create a new run
func handleRunCreate(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusOK)
		return
	}

	if r.Method != "POST" {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var request struct {
		AlgorithmID string `json:"algorithmId"`
		Array       []int  `json:"array"`
	}

	if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Validate input
	if len(request.Array) == 0 {
		http.Error(w, "Array cannot be empty", http.StatusBadRequest)
		return
	}

	// Create run
	run, err := createRun(request.AlgorithmID, request.Array)
	if err != nil {
		http.Error(w, fmt.Sprintf("Failed to create run: %v", err), http.StatusInternalServerError)
		return
	}

	// Return runId
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"runId": run.RunID,
	})
}

// GET /ws?runId=<id> - WebSocket handler
func handleWebSocket(w http.ResponseWriter, r *http.Request) {
	runID := r.URL.Query().Get("runId")
	if runID == "" {
		http.Error(w, "Missing runId parameter", http.StatusBadRequest)
		return
	}

	speedStr := r.URL.Query().Get("speed")
	speedMultiplier := 1.0
	if speedStr != "" {
		fmt.Sscanf(speedStr, "%f", &speedMultiplier)
	}

	// Upgrade connection
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade failed: %v", err)
		return
	}
	defer conn.Close()

	wsConn := &websocketConnection{Conn: conn}

	// Stream the run
	if err := streamRun(runID, wsConn, speedMultiplier); err != nil {
		log.Printf("Error streaming run: %v", err)
		// Try to send error message
		wsConn.WriteJSON(map[string]interface{}{
			"type": "ERROR",
			"data": map[string]string{
				"message": err.Error(),
			},
		})
	}
}

// GET /health - Health check
func handleHealth(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status":  "healthy",
		"service": "go-backend",
	})
}

func main() {
	http.HandleFunc("/api/run", handleRunCreate)
	http.HandleFunc("/ws", handleWebSocket)
	http.HandleFunc("/health", handleHealth)

	port := ":8080"
	fmt.Printf("🚀 Go backend starting on port %s\n", port)
	fmt.Println("📡 WebSocket endpoint: ws://localhost:8080/ws?runId=<id>")
	fmt.Println("🔗 API endpoint: http://localhost:8080/api/run")

	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal(err)
	}
}
