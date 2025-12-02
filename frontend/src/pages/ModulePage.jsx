import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Visualizer from '../components/Visualizer';
import EditableCodePanel from '../components/EditableCodePanel';
import TerminalOutput from '../components/TerminalOutput';
import './ModulePage.css';

export default function ModulePage() {
    const { moduleName } = useParams();
    const navigate = useNavigate();

    const [moduleData, setModuleData] = useState(null);
    const [currentOperation, setCurrentOperation] = useState('');
    const [currentCode, setCurrentCode] = useState('');
    const [isPlaying, setIsPlaying] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [speed, setSpeed] = useState(1);
    const [trace, setTrace] = useState([]);
    const [currentStep, setCurrentStep] = useState(0);
    const [terminalOutput, setTerminalOutput] = useState([]);

    useEffect(() => {
        fetch(`http://localhost:8000/api/module/${moduleName}`)
            .then(res => res.json())
            .then(data => {
                setModuleData(data);
                if (data.operations && data.operations.length > 0) {
                    const firstOp = data.operations[0].id;
                    setCurrentOperation(firstOp);
                    setCurrentCode(data.code?.[firstOp] || '');
                }
            })
            .catch(err => {
                console.error('Failed to load module:', err);
            });
    }, [moduleName]);

    useEffect(() => {
        if (moduleData && currentOperation) {
            setCurrentCode(moduleData.code?.[currentOperation] || '');
        }
    }, [currentOperation, moduleData]);

    const addTerminalOutput = (line) => {
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        setTerminalOutput(prev => [...prev, { ...line, timestamp }]);
    };

    const handleExecute = async () => {
        if (!currentOperation || isRunning) return;

        setIsRunning(true);
        setTrace([]);
        setCurrentStep(0);
        setTerminalOutput([]);
        addTerminalOutput({ type: 'info', text: '▶️ Compiling and executing...' });

        try {
            const res = await fetch('http://localhost:8000/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    module: moduleName,
                    operation: currentOperation,
                    params: { code: currentCode }
                })
            });

            const data = await res.json();

            if (data.error) {
                addTerminalOutput({ type: 'error', text: `❌ ${data.error}` });
                setIsRunning(false);
                return;
            }

            setTrace(data.trace || []);
            addTerminalOutput({ type: 'success', text: `✓ Generated ${data.trace?.length || 0} steps` });

            if (data.trace && data.trace.length > 0) {
                setIsPlaying(true);
            }
        } catch (err) {
            addTerminalOutput({ type: 'error', text: `❌ ${err.message}` });
        } finally {
            setIsRunning(false);
        }
    };

    // Animation loop - FIXED to show last step
    useEffect(() => {
        if (!isPlaying || trace.length === 0) return;

        // Stop AFTER showing the last step (not before)
        if (currentStep >= trace.length) {
            setIsPlaying(false);
            setCurrentStep(trace.length - 1); // Stay on last frame
            return;
        }

        const timer = setTimeout(() => {
            setCurrentStep(prev => prev + 1);
        }, 1000 / speed);

        return () => clearTimeout(timer);
    }, [isPlaying, currentStep, trace.length, speed]);

    if (!moduleData) {
        return <div className="module-page"><div className="container"><p>Loading...</p></div></div>;
    }

    if (!moduleData.operations || moduleData.operations.length === 0) {
        return (
            <div className="module-page">
                <header className="module-header">
                    <div className="container">
                        <button onClick={() => navigate('/')} className="back-btn">← Back</button>
                        <h1>{moduleData.name}</h1>
                    </div>
                </header>
            </div>
        );
    }

    return (
        <div className="module-page">
            <header className="module-header">
                <div className="container">
                    <button onClick={() => navigate('/')} className="back-btn">← Back</button>
                    <h1 className="module-title">{moduleData.name}</h1>
                    {moduleData.operations && moduleData.operations.length > 1 && (
                        <select value={currentOperation} onChange={(e) => setCurrentOperation(e.target.value)} className="operation-select">
                            {moduleData.operations.map(op => (
                                <option key={op.id} value={op.id}>{op.name}</option>
                            ))}
                        </select>
                    )}
                </div>
            </header>

            <div className="module-content">
                <div className="container">
                    <div className="module-grid">
                        <div className="panel code-section">
                            <EditableCodePanel
                                initialCode={currentCode}
                                onCodeChange={setCurrentCode}
                                onRun={handleExecute}
                                isRunning={isRunning || isPlaying}
                            />
                        </div>

                        <div className="panel viz-section">
                            <Visualizer
                                module={moduleName}
                                data={trace[Math.min(currentStep, trace.length - 1)]?.data}
                                highlights={trace[Math.min(currentStep, trace.length - 1)]?.highlights || []}
                                controlsProps={{
                                    isPlaying,
                                    onPlayPause: () => setIsPlaying(!isPlaying),
                                    currentStep,
                                    totalSteps: trace.length,
                                    speed,
                                    onSpeedChange: setSpeed,
                                    onStepChange: setCurrentStep
                                }}
                            />
                        </div>

                        <div className="panel terminal-section">
                            <TerminalOutput
                                output={terminalOutput}
                                onClear={() => setTerminalOutput([])}
                                onAddOutput={addTerminalOutput}
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
