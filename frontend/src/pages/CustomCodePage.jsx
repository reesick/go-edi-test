// Custom Code Page
// Main page for the LineSync AI feature where users can write custom C++ algorithms
// and visualize them with AI-powered line synchronization

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CustomCodeEditor, { DEFAULT_CODE } from '../components/custom/CustomCodeEditor';
import CustomTerminal from '../components/custom/CustomTerminal';
import CustomVisualizer from '../components/custom/CustomVisualizer';
import './CustomCodePage.css';

const API_BASE = 'http://localhost:8000';

const CustomCodePage = () => {
    // State management
    const [code, setCode] = useState(localStorage.getItem('customCode') || DEFAULT_CODE);
    const [inputData, setInputData] = useState('');
    const [logs, setLogs] = useState([]);
    const [isRunning, setIsRunning] = useState(false);
    const [executablePath, setExecutablePath] = useState(null);

    // Visualization state
    const [visualizationData, setVisualizationData] = useState(null);
    const [lineSyncData, setLineSyncData] = useState(null);
    const [currentFrame, setCurrentFrame] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(1000); // ms per frame

    // Line highlighting state
    const [highlightedLines, setHighlightedLines] = useState([]);
    const [setupLines, setSetupLines] = useState([]);
    const [dimmedLines, setDimmedLines] = useState([]);

    // Auto-save code to localStorage
    useEffect(() => {
        localStorage.setItem('customCode', code);
    }, [code]);

    // Auto-play frames
    useEffect(() => {
        if (isPlaying && visualizationData) {
            const interval = setInterval(() => {
                setCurrentFrame(prev => {
                    const next = prev + 1;
                    if (next >= visualizationData.frames.length) {
                        setIsPlaying(false);
                        return prev;
                    }
                    return next;
                });
            }, playbackSpeed);

            return () => clearInterval(interval);
        }
    }, [isPlaying, visualizationData, playbackSpeed]);

    // Update line highlights when frame changes
    useEffect(() => {
        if (!lineSyncData || !visualizationData) return;

        const mapping = lineSyncData.frame_mappings.find(
            m => m.frame_id === currentFrame
        );

        if (mapping) {
            setHighlightedLines(mapping.line_numbers);
        } else {
            setHighlightedLines([]);
        }

        // Set dimmed lines (non-visualized)
        setDimmedLines(lineSyncData.non_visualized_lines || []);
    }, [currentFrame, lineSyncData, visualizationData]);

    const addLog = (type, message) => {
        setLogs(prev => [...prev, { type, message, timestamp: Date.now() }]);
    };

    const handleRun = async () => {
        setIsRunning(true);
        setLogs([]);
        setVisualizationData(null);
        setLineSyncData(null);
        setCurrentFrame(0);
        setHighlightedLines([]);
        setSetupLines([]);

        try {
            // Step 1: Compile
            addLog('info', 'Compiling C++ code...');
            const compileResponse = await axios.post(`${API_BASE}/api/custom/compile`, {
                code
            });

            if (!compileResponse.data.success) {
                addLog('error', 'Compilation failed:');
                addLog('error', compileResponse.data.errors);
                setIsRunning(false);
                return;
            }

            addLog('success', `Compiled successfully (${compileResponse.data.compile_time_ms}ms)`);

            if (compileResponse.data.warnings) {
                addLog('warning', compileResponse.data.warnings);
            }

            setExecutablePath(compileResponse.data.executable_path);

            // Step 2: Generate visualization and linesync
            addLog('info', 'Generating visualization with AI...');
            const vizResponse = await axios.post(`${API_BASE}/api/custom/visualize-with-linesync`, {
                code,
                input_data: inputData,
                executable_path: compileResponse.data.executable_path
            });

            if (vizResponse.data.is_fallback) {
                addLog('warning', 'AI visualization failed, using fallback');
                addLog('warning', vizResponse.data.metadata.error);
            } else {
                addLog('success', `Visualization ready (${vizResponse.data.metadata.total_frames} frames)`);
            }

            // Set visualization data
            setVisualizationData(vizResponse.data.visualization);
            setLineSyncData(vizResponse.data.linesync);

            // Flash setup lines briefly
            if (vizResponse.data.linesync.setup_lines) {
                setSetupLines(vizResponse.data.linesync.setup_lines);
                setTimeout(() => setSetupLines([]), 500);
            }

            // Start playback
            setTimeout(() => setIsPlaying(true), 600);

        } catch (error) {
            console.error('Error:', error);

            if (error.response) {
                const status = error.response.status;
                if (status === 429) {
                    addLog('error', 'Rate limit exceeded. Please wait before trying again.');
                } else if (status === 408) {
                    addLog('error', 'Execution timeout. Please optimize your code.');
                } else {
                    addLog('error', `Error: ${error.response.data.detail || error.message}`);
                }
            } else {
                addLog('error', `Network error: ${error.message}`);
            }
        } finally {
            setIsRunning(false);
        }
    };

    const handlePlayPause = () => {
        setIsPlaying(!isPlaying);
    };

    const handleStepForward = () => {
        if (visualizationData && currentFrame < visualizationData.frames.length - 1) {
            setCurrentFrame(prev => prev + 1);
        }
    };

    const handleStepBackward = () => {
        if (currentFrame > 0) {
            setCurrentFrame(prev => prev - 1);
        }
    };

    const handleReset = () => {
        setCurrentFrame(0);
        setIsPlaying(false);
    };

    return (
        <div className="custom-code-page">
            <header className="page-header">
                <div className="header-left">
                    <h1>Custom Code</h1>
                    <span className="beta-badge">BETA</span>
                    <p className="subtitle">Write your own algorithms with AI-powered visualization</p>
                </div>
                <div className="header-controls">
                    <button
                        className="run-button"
                        onClick={handleRun}
                        disabled={isRunning}
                    >
                        {isRunning ? 'Running...' : '⚡ Run'}
                    </button>
                </div>
            </header>

            <div className="page-content">
                <div className="left-panel">
                    <div className="editor-section">
                        <CustomCodeEditor
                            code={code}
                            onChange={setCode}
                            highlightedLines={highlightedLines}
                            setupLines={setupLines}
                            dimmedLines={dimmedLines}
                            readOnly={isRunning}
                        />
                    </div>
                    <div className="terminal-section">
                        <CustomTerminal logs={logs} isRunning={isRunning} />
                    </div>
                </div>

                <div className="right-panel">
                    <CustomVisualizer
                        frame={visualizationData?.frames[currentFrame]}
                        currentFrameIndex={currentFrame}
                        totalFrames={visualizationData?.frames.length || 0}
                    />

                    {visualizationData && (
                        <div className="playback-controls">
                            <button onClick={handleReset} disabled={currentFrame === 0}>
                                ⏮ Reset
                            </button>
                            <button onClick={handleStepBackward} disabled={currentFrame === 0}>
                                ⏪ Step Back
                            </button>
                            <button onClick={handlePlayPause}>
                                {isPlaying ? '⏸ Pause' : '▶ Play'}
                            </button>
                            <button
                                onClick={handleStepForward}
                                disabled={currentFrame >= visualizationData.frames.length - 1}
                            >
                                ⏩ Step Forward
                            </button>
                            <div className="speed-control">
                                <label>Speed:</label>
                                <select
                                    value={playbackSpeed}
                                    onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                                >
                                    <option value={2000}>0.5x</option>
                                    <option value={1000}>1x</option>
                                    <option value={500}>2x</option>
                                    <option value={250}>4x</option>
                                </select>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CustomCodePage;
