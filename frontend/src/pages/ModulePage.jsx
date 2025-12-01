import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Visualizer from '../components/Visualizer';
import EditableCodePanel from '../components/EditableCodePanel';
import TerminalOutput from '../components/TerminalOutput';
import ControlBar from '../components/ControlBar';
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

    // Load module data from backend
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
                addTerminalOutput({ type: 'error', text: `Failed to load module: ${err.message}` });
            });
    }, [moduleName]);

    // Update code when operation changes
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

    // Handle operation execution
    const handleExecute = async () => {
        if (!currentOperation || isRunning) return;

        setIsRunning(true);
        setTrace([]);
        setCurrentStep(0);
        setTerminalOutput([]);
        addTerminalOutput({ type: 'info', text: '▶️ Validating code syntax...' });

        // Step 1: Validate syntax first
        try {
            const validateRes = await fetch('http://localhost:8000/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: currentCode })
            });

            const validateData = await validateRes.json();

            if (!validateData.valid) {
                addTerminalOutput({
                    type: 'error',
                    text: `❌ Syntax Error: ${validateData.error}`
                });
                if (validateData.line) {
                    addTerminalOutput({
                        type: 'error',
                        text: `   at line ${validateData.line}`
                    });
                }
                setIsRunning(false);
                return;
            }

            addTerminalOutput({ type: 'success', text: '✓ Syntax validation passed' });
        } catch (err) {
            addTerminalOutput({ type: 'error', text: `❌ Validation failed: ${err.message}` });
            setIsRunning(false);
            return;
        }

        addTerminalOutput({ type: 'info', text: '▶️ Executing your code...' });

        // Step 2: Execute the code
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
                addTerminalOutput({ type: 'error', text: `❌ Error: ${data.error}` });
                setIsRunning(false);
                return;
            }

            // Show output if any
            if (data.output) {
                if (data.output.stdout) {
                    addTerminalOutput({ type: 'success', text: data.output.stdout });
                }
                if (data.output.stderr) {
                    addTerminalOutput({ type: 'error', text: data.output.stderr });
                }
                if (data.output.execution_time) {
                    addTerminalOutput({
                        type: 'info',
                        text: `⏱️ Execution time: ${data.output.execution_time.toFixed(3)}s`
                    });
                }
            }

            setTrace(data.trace || []);
            addTerminalOutput({
                type: 'success',
                text: `✓ Generated ${data.trace?.length || 0} animation steps from YOUR code`
            });

            if (data.trace && data.trace.length > 0) {
                setIsPlaying(true);
                addTerminalOutput({ type: 'info', text: 'Starting visualization...' });
            }
        } catch (err) {
            addTerminalOutput({ type: 'error', text: `❌ ${err.message}` });
        } finally {
            setIsRunning(false);
        }
    };

    // Animation loop
    useEffect(() => {
        if (!isPlaying || currentStep >= trace.length) {
            if (isPlaying && currentStep >= trace.length) {
                addTerminalOutput({ type: 'success', text: '✓ Visualization complete!' });
            }
            setIsPlaying(false);
            return;
        }

        const timer = setTimeout(() => {
            setCurrentStep(currentStep + 1);
        }, 1000 / speed);

        return () => clearTimeout(timer);
    }, [isPlaying, currentStep, trace.length, speed]);

    if (!moduleData) {
        return (
            <div className="module-page">
                <div className="container">
                    <p className="text-center text-muted">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="module-page">
            {/* Header */}
            <header className="module-header">
                <div className="container">
                    <button onClick={() => navigate('/')} className="back-btn">
                        ← Back to Home
                    </button>
                    <h1 className="module-title">{moduleData.name}</h1>
                </div>
            </header>

            {/* Main Content */}
            <div className="module-content">
                <div className="container">
                    <div className="module-grid">
                        {/* Left: Code Panel */}
                        <div className="panel code-section">
                            <EditableCodePanel
                                initialCode={currentCode}
                                onCodeChange={setCurrentCode}
                                onRun={handleExecute}
                                isRunning={isRunning || isPlaying}
                            />
                        </div>

                        {/* Right Top: Visualizer */}
                        <div className="panel viz-section">
                            <Visualizer
                                module={moduleName}
                                data={trace[currentStep]?.data}
                                highlights={trace[currentStep]?.highlights || []}
                            />
                        </div>

                        {/* Right Bottom: Terminal */}
                        <div className="panel terminal-section">
                            <TerminalOutput
                                output={terminalOutput}
                                onClear={() => setTerminalOutput([])}
                            />
                        </div>
                    </div>

                    {/* Controls */}
                    <ControlBar
                        operations={moduleData.operations || []}
                        currentOperation={currentOperation}
                        onOperationChange={setCurrentOperation}
                        isPlaying={isPlaying}
                        onPlayPause={() => setIsPlaying(!isPlaying)}
                        onExecute={handleExecute}
                        speed={speed}
                        onSpeedChange={setSpeed}
                        currentStep={currentStep}
                        totalSteps={trace.length}
                    />
                </div>
            </div>
        </div>
    );
}
