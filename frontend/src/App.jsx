import React, { useState, useEffect, useRef } from 'react';
import ControlPanel from './ControlPanel.jsx';
import VisualizerEngine from './VisualizerEngine.jsx';
import ExplanationPanel from './ExplanationPanel.jsx';
import Timeline from './Timeline.jsx';
import Logger from './Logger.js';
import './App.css';

const API_URL = 'http://localhost:8080';
const WS_URL = 'ws://localhost:8080';

function App() {
    const [runId, setRunId] = useState(null);
    const [currentArray, setCurrentArray] = useState([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [traceFrames, setTraceFrames] = useState([]);
    const [explanation, setExplanation] = useState(null);
    const [runStatus, setRunStatus] = useState('idle'); // idle, running, paused, completed, error
    const [speedMultiplier, setSpeedMultiplier] = useState(1.0);

    const wsRef = useRef(null);
    const pauseStartRef = useRef(null);

    // Handle run start
    const handleRun = async (array, algorithmId, speed) => {
        try {
            setRunStatus('running');
            setSpeedMultiplier(speed);
            Logger.clear();

            // Call /api/run
            const response = await fetch(`${API_URL}/api/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ algorithmId, array })
            });

            if (!response.ok) {
                throw new Error('Failed to create run');
            }

            const data = await response.json();
            const newRunId = data.runId;
            setRunId(newRunId);

            // Open WebSocket
            connectWebSocket(newRunId, speed);

        } catch (error) {
            console.error('Error starting run:', error);
            setRunStatus('error');
            alert('Error: ' + error.message);
        }
    };

    // Connect to WebSocket
    const connectWebSocket = (runId, speed) => {
        const ws = new WebSocket(`${WS_URL}/ws?runId=${runId}&speed=${speed}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('✅ WebSocket connected');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            console.log('📨 Received:', message.type);

            if (message.type === 'TRACE') {
                const frame = message.data;
                setCurrentArray(frame.array);
                setCurrentStep(frame.stepIndex);
                setTraceFrames(prev => [...prev, frame]);
            }

            if (message.type === 'EXPLANATION') {
                setExplanation(message.data);
            }

            if (message.type === 'END') {
                setRunStatus('completed');
                console.log('✅ Visualization complete');
            }

            if (message.type === 'ERROR') {
                setRunStatus('error');
                console.error('❌ Error:', message.data.message);
                alert('Error: ' + message.data.message);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setRunStatus('error');
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
        };
    };

    // Handle pause
    const handlePause = () => {
        if (runStatus === 'running') {
            pauseStartRef.current = Date.now();
            setRunStatus('paused');
            if (wsRef.current) {
                wsRef.current.close();
            }
        } else if (runStatus === 'paused') {
            // Calculate pause duration
            const pauseDuration = (Date.now() - pauseStartRef.current) / 1000;
            Logger.logPause(currentStep, pauseDuration);

            // Resume (for now, just log - full resume requires backend support)
            setRunStatus('running');
        }
    };

    // Handle speed change
    const handleSpeedChange = (newSpeed) => {
        setSpeedMultiplier(newSpeed);
        Logger.logSpeedChange(newSpeed);

        // For real-time speed change, would need to reconnect WebSocket
        // This is a simplified version
    };

    // Handle timeline seek
    const handleSeek = (stepIndex) => {
        if (traceFrames[stepIndex]) {
            const frame = traceFrames[stepIndex];
            setCurrentArray(frame.array);
            setCurrentStep(stepIndex);
        }
    };

    // Get current frame data for visualizer
    const currentFrame = traceFrames[currentStep] || {
        array: currentArray,
        pointers: {},
        swapOccurred: false,
        action: 'compare'
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1 className="app-title gradient-text">
                    Algorithm Visualizer
                </h1>
                <p className="app-subtitle">Adaptive AI-Powered Learning Platform</p>
            </header>

            <div className="app-layout">
                <div className="left-column">
                    <ControlPanel
                        onRun={handleRun}
                        onPause={handlePause}
                        onSpeedChange={handleSpeedChange}
                        isRunning={runStatus === 'running'}
                    />

                    <ExplanationPanel explanation={explanation} />
                </div>

                <div className="right-column">
                    <VisualizerEngine
                        array={currentFrame.array}
                        pointers={currentFrame.pointers}
                        swapOccurred={currentFrame.swapOccurred}
                        action={currentFrame.action}
                    />

                    <Timeline
                        currentStep={currentStep}
                        totalSteps={traceFrames.length}
                        onSeek={handleSeek}
                    />
                </div>
            </div>

            {runStatus === 'error' && (
                <div className="error-banner">
                    ⚠️ Unable to connect to backend. Make sure servers are running.
                </div>
            )}
        </div>
    );
}

export default App;
