import { useEffect, useRef, useState } from 'react';
import './TerminalOutput.css';

export default function TerminalOutput({ output = [], onClear, onAddOutput }) {
    const contentRef = useRef(null);
    const inputRef = useRef(null);
    const [input, setInput] = useState('');
    const [history, setHistory] = useState([]);
    const [historyIndex, setHistoryIndex] = useState(-1);

    // Auto-scroll to bottom when output changes
    useEffect(() => {
        if (contentRef.current) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight;
        }
    }, [output]);

    const handleCommand = async (cmd) => {
        if (!cmd.trim()) return;

        // Add to history
        setHistory(prev => [...prev, cmd]);
        setHistoryIndex(-1);

        // Add command to output
        if (onAddOutput) {
            onAddOutput({ type: 'command', text: `$ ${cmd}` });

            // Execute command via backend
            try {
                const res = await fetch('http://localhost:8000/api/terminal/exec', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: cmd })
                });
                const data = await res.json();

                if (data.error) {
                    onAddOutput({ type: 'error', text: data.error });
                } else if (data.output) {
                    onAddOutput({ type: 'info', text: data.output });
                }
            } catch (err) {
                onAddOutput({ type: 'error', text: `Error: ${err.message}` });
            }
        }

        setInput('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleCommand(input);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (history.length > 0) {
                const newIndex = historyIndex === -1 ? history.length - 1 : Math.max(0, historyIndex - 1);
                setHistoryIndex(newIndex);
                setInput(history[newIndex]);
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex !== -1) {
                const newIndex = historyIndex + 1;
                if (newIndex >= history.length) {
                    setHistoryIndex(-1);
                    setInput('');
                } else {
                    setHistoryIndex(newIndex);
                    setInput(history[newIndex]);
                }
            }
        } else if (e.key === 'l' && e.ctrlKey) {
            // Ctrl+L to clear (like real terminal)
            e.preventDefault();
            if (onClear) onClear();
        }
    };

    const getLineClass = (line) => {
        if (typeof line === 'string') return 'terminal-line';
        const type = line.type || 'info';
        return `terminal-line terminal-${type}`;
    };

    const getLineText = (line) => {
        if (typeof line === 'string') return line;
        return line.text || '';
    };

    const getTimestamp = (line) => {
        if (typeof line === 'string') return '';
        return line.timestamp || '';
    };

    return (
        <div className="terminal-output">
            <div className="terminal-header">
                <h3>Terminal (Interactive)</h3>
                {output.length > 0 && (
                    <button onClick={onClear} className="btn-clear" title="Clear terminal (Ctrl+L)">
                        Clear
                    </button>
                )}
            </div>

            <div className="terminal-content" ref={contentRef}>
                {output.length === 0 ? (
                    <div className="terminal-empty">
                        Interactive terminal - Type commands below
                        <br />
                        <span className="text-muted">Try: g++ --version, ls, pwd, cat filename.cpp</span>
                    </div>
                ) : (
                    output.map((line, index) => (
                        <div key={index} className={getLineClass(line)}>
                            {getTimestamp(line) && (
                                <span className="terminal-timestamp">{getTimestamp(line)}</span>
                            )}
                            <span className="terminal-text">{getLineText(line)}</span>
                        </div>
                    ))
                )}
            </div>

            {/* Interactive Input */}
            <div className="terminal-input-container">
                <span className="terminal-prompt">$</span>
                <input
                    ref={inputRef}
                    type="text"
                    className="terminal-input"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Type command and press Enter (↑↓ for history, Ctrl+L to clear)..."
                    autoComplete="off"
                    spellCheck="false"
                />
            </div>
        </div>
    );
}
