import { useState, useEffect } from 'react';
import './EditableCodePanel.css';

export default function EditableCodePanel({
    initialCode,
    onCodeChange,
    onRun,
    isRunning
}) {
    const [code, setCode] = useState(initialCode);
    const [isDirty, setIsDirty] = useState(false);

    useEffect(() => {
        setCode(initialCode);
        setIsDirty(false);
    }, [initialCode]);

    const handleCodeChange = (e) => {
        const newCode = e.target.value;
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

        // Tab support
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const newCode = code.substring(0, start) + '    ' + code.substring(end);
            setCode(newCode);
            if (onCodeChange) onCodeChange(newCode);

            setTimeout(() => {
                e.target.selectionStart = e.target.selectionEnd = start + 4;
            }, 0);
        }
    };

    return (
        <div className="editable-code-panel">
            <div className="code-header">
                <h3>Code (C++)</h3>
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
                <textarea
                    value={code}
                    onChange={handleCodeChange}
                    onKeyDown={handleKeyDown}
                    className="code-editor-plain"
                    spellCheck="false"
                    autoComplete="off"
                    autoCorrect="off"
                    autoCapitalize="off"
                />
            </div>

            <div className="code-hint text-muted">
                Press <kbd>Ctrl+Enter</kbd> to compile and run • <kbd>Tab</kbd> to indent
            </div>
        </div>
    );
}
