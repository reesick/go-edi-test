/**
 * WorkspacePage.jsx - Main workspace integrating visualization + code + terminal
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import CodeEditor from './CodeEditor';
import VisualizerEngine from './VisualizerEngine';
import Terminal from './Terminal';
import './WorkspacePage.css';

export default function WorkspacePage() {
    const { mode } = useParams();
    const navigate = useNavigate();

    const [code, setCode] = useState('');
    const [isRunning, setIsRunning] = useState(false);
    const [currentFrame, setCurrentFrame] = useState(null);
    const [output, setOutput] = useState([]);
    const [presets, setPresets] = useState([]);

    // Load presets on mount
    useEffect(() => {
        fetch('http://localhost:8000/presets')
            .then(res => res.json())
            .then(data => {
                setPresets(data.presets || []);
                // Load first preset by default
                if (data.presets && data.presets.length > 0) {
                    loadPreset(data.presets[0].id);
                }
            })
            .catch(err => console.error('Failed to load presets:', err));
    }, []);

    const loadPreset = async (presetId) => {
        try {
            const res = await fetch(`http://localhost:8000/preset/${presetId}`);
            const data = await res.json();
            setCode(data.code);
            addOutput({ type: 'info', text: `Loaded preset: ${data.name}`, timestamp: getTimestamp() });
        } catch (err) {
            addOutput({ type: 'error', text: `Failed to load preset: ${err.message}`, timestamp: getTimestamp() });
        }
    };

    const handleRun = async () => {
        setIsRunning(true);
        setOutput([{ type: 'info', text: '▶️ Executing algorithm...', timestamp: getTimestamp() }]);

        try {
            // Use the /execute endpoint to generate trace
            const res = await fetch('http://localhost:8000/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    algorithmId: 'bubble_sort',
                    array: [5, 2, 8, 1, 9]
                })
            });

            const result = await res.json();

            if (result.trace && result.trace.length > 0) {
                addOutput({ type: 'success', text: `✓ Generated ${result.trace.length} steps`, timestamp: getTimestamp() });
                addOutput({ type: 'info', text: 'Starting visualization...', timestamp: getTimestamp() });

                // Start visualization
                visualizeTrace(result.trace);
            } else {
                addOutput({ type: 'error', text: 'No trace generated', timestamp: getTimestamp() });
            }
        } catch (err) {
            addOutput({ type: 'error', text: `Error: ${err.message}`, timestamp: getTimestamp() });
        } finally {
            setIsRunning(false);
        }
    };

    const visualizeTrace = (trace) => {
        let index = 0;
        const interval = setInterval(() => {
            if (index >= trace.length) {
                clearInterval(interval);
                addOutput({ type: 'success', text: '✓ Visualization complete!', timestamp: getTimestamp() });
                return;
            }

            setCurrentFrame(trace[index]);
            addOutput({
                type: 'step',
                text: `Step ${index + 1}/${trace.length}: ${trace[index].action}`,
                timestamp: getTimestamp()
            });

            index++;
        }, 1000); // 1 second per step
    };

    const addOutput = (line) => {
        setOutput(prev => [...prev, line]);
    };

    const getTimestamp = () => {
        return new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    };

    return (
        <div className="workspace-page">
            {/* Top Bar */}
            <header className="workspace-header">
                <div className="workspace-title">
                    <button className="back-button" onClick={() => navigate('/')}>
                        ← Home
                    </button>
                    <h1>{getModeTitle(mode)}</h1>
                </div>

                <div className="workspace-controls">
                    <select
                        className="preset-selector"
                        onChange={(e) => loadPreset(e.target.value)}
                    >
                        <option value="">Load Preset...</option>
                        {presets.map(p => (
                            <option key={p.id} value={p.id}>{p.name}</option>
                        ))}
                    </select>
                </div>
            </header>

            {/* Main Workspace - 3 Panel Layout */}
            <div className="workspace-grid">
                {/* Left: Code Editor */}
                <div className="workspace-panel panel-code">
                    <CodeEditor
                        code={code}
                        onChange={setCode}
                        language="python"
                        onRun={handleRun}
                    />
                </div>

                {/* Center: Visualization */}
                <div className="workspace-panel panel-viz">
                    <div className="panel-header">
                        <h3>📊 Visualization</h3>
                    </div>
                    <VisualizerEngine
                        array={currentFrame?.array || [5, 2, 8, 1, 9]}
                        pointers={currentFrame?.pointers || {}}
                        action={currentFrame?.action || 'idle'}
                        swapOccurred={currentFrame?.swapOccurred || false}
                    />
                </div>

                {/* Right: Terminal */}
                <div className="workspace-panel panel-terminal">
                    <Terminal
                        output={output}
                        title="Execution Console"
                    />
                </div>
            </div>
        </div>
    );
}

function getModeTitle(mode) {
    const titles = {
        learn: '🎓 Learn Mode',
        practice: '💪 Practice Mode',
        challenge: '🏆 Challenge Mode',
        explore: '🔬 Explore Mode',
        custom: '💻 Custom Code'
    };
    return titles[mode] || 'Workspace';
}
