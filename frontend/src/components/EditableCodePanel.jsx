import { useState } from 'react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-tomorrow.css';
import './EditableCodePanel.css';

export default function EditableCodePanel({
    initialCode,
    onCodeChange,
    onRun,
    isRunning
}) {
    const [code, setCode] = useState(initialCode);
    const [isDirty, setIsDirty] = useState(false);

    const handleCodeChange = (newCode) => {
        setCode(newCode);
        setIsDirty(true);
        if (onCodeChange) {
            onCodeChange(newCode);
        }
    };

    const handleReset = () => {
        setCode(initialCode);
        setIsDirty(false);
        if (onCodeChange) {
            onCodeChange(initialCode);
        }
    };

    const handleKeyDown = (e) => {
        // Ctrl+Enter to run
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            if (onRun) onRun();
        }
    };

    return (
        <div className="editable-code-panel">
            <div className="code-header">
                <h3>Code</h3>
                <div className="code-actions">
                    {isDirty && (
                        <button
                            onClick={handleReset}
                            className="btn-secondary btn-sm"
                            disabled={isRunning}
                        >
                            ↺ Reset
                        </button>
                    )}
                    <button
                        onClick={onRun}
                        className="btn btn-sm"
                        disabled={isRunning}
                    >
                        {isRunning ? '⏳ Running...' : '▶ Run (Ctrl+Enter)'}
                    </button>
                </div>
            </div>

            <div className="code-editor-wrapper">
                <Editor
                    value={code}
                    onValueChange={handleCodeChange}
                    highlight={code => highlight(code, languages.python, 'python')}
                    padding={16}
                    onKeyDown={handleKeyDown}
                    className="code-editor"
                    style={{
                        fontFamily: '"Monaco", "Menlo", "Consolas", monospace',
                        fontSize: 14,
                        lineHeight: 1.6,
                        minHeight: '400px',
                    }}
                    textareaClassName="code-textarea"
                />
            </div>

            <div className="code-hint text-muted">
                Press <kbd>Ctrl+Enter</kbd> to run code
            </div>
        </div>
    );
}
