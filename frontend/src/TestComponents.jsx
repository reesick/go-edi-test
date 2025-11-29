/**
 * Test page for CodeEditor and Terminal components
 */
import { useState } from 'react';
import CodeEditor from './CodeEditor';
import Terminal from './Terminal';
import './TestComponents.css';

const sampleCode = `def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Test
result = bubble_sort([5, 2, 8, 1, 9])
print(f"Sorted: {result}")`;

const sampleOutput = [
    { type: 'info', text: 'Starting bubble sort execution...', timestamp: '00:00' },
    { type: 'step', text: 'Pass 1: Comparing arr[0]=5 and arr[1]=2', timestamp: '00:01' },
    { type: 'step', text: 'Swapping 5 and 2', timestamp: '00:01' },
    { type: 'success', text: 'Pass 1 complete', timestamp: '00:02' },
    { type: 'step', text: 'Pass 2: Comparing arr[1]=5 and arr[2]=8', timestamp: '00:02' },
    { type: 'info', text: 'No swap needed', timestamp: '00:02' },
    { type: 'step', text: 'Pass 3: Comparing arr[2]=8 and arr[3]=1', timestamp: '00:03' },
    { type: 'step', text: 'Swapping 8 and 1', timestamp: '00:03' },
    { type: 'warning', text: 'Large swap detected', timestamp: '00:03' },
    { type: 'success', text: '✓ Sorting complete!', timestamp: '00:05' },
    { type: 'success', text: 'Result: [1, 2, 5, 8, 9]', timestamp: '00:05' },
];

export default function TestComponents() {
    const [code, setCode] = useState(sampleCode);
    const [output, setOutput] = useState(sampleOutput);

    const handleRun = () => {
        setOutput([
            ...output,
            { type: 'info', text: '▶️ Running code...', timestamp: new Date().toLocaleTimeString() }
        ]);
    };

    return (
        <div className="test-container">
            <h1>🧪 Component Test Page</h1>
            <p>Testing CodeEditor and Terminal components</p>

            <div className="test-grid">
                {/* Code Editor */}
                <div className="test-section">
                    <h2>💻 Code Editor</h2>
                    <CodeEditor
                        code={code}
                        onChange={setCode}
                        language="python"
                        onRun={handleRun}
                    />
                </div>

                {/* Terminal */}
                <div className="test-section">
                    <h2>📟 Terminal Output</h2>
                    <Terminal
                        output={output}
                        title="Execution Console"
                    />
                </div>
            </div>

            <div className="test-info">
                <h3>✅ Features to Test:</h3>
                <ul>
                    <li>✏️ Edit code in Monaco editor</li>
                    <li>🎨 Change themes (Dark/Light/High Contrast)</li>
                    <li>📏 Adjust font size</li>
                    <li>⚡ Click Format button</li>
                    <li>📋 Copy code</li>
                    <li>▶️ Click Run Code button</li>
                    <li>🔍 Filter terminal output by type</li>
                    <li>📌 Toggle auto-scroll</li>
                    <li>📋 Copy terminal output</li>
                    <li>🗑️ Clear terminal</li>
                </ul>
            </div>
        </div>
    );
}
