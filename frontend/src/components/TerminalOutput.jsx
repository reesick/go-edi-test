import { useRef, useEffect } from 'react';
import './TerminalOutput.css';

export default function TerminalOutput({ output = [], onClear }) {
    const terminalRef = useRef(null);

    // Auto-scroll to bottom when new output arrives
    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [output]);

    const getLineClass = (line) => {
        if (typeof line === 'string') return 'terminal-line';

        const type = line.type || 'info';
        return `terminal-line terminal-${type}`;
    };

    return (
        <div className="terminal-output">
            <div className="terminal-header">
                <h3>Terminal</h3>
                {output.length > 0 && (
                    <button onClick={onClear} className="btn-secondary btn-sm">
                        🗑️ Clear
                    </button>
                )}
            </div>

            <div className="terminal-content" ref={terminalRef}>
                {output.length === 0 ? (
                    <div className="terminal-empty">
                        <p className="text-muted">Run code to see output...</p>
                    </div>
                ) : (
                    output.map((line, index) => {
                        const text = typeof line === 'string' ? line : line.text;
                        const timestamp = typeof line === 'object' ? line.timestamp : null;

                        return (
                            <div key={index} className={getLineClass(line)}>
                                {timestamp && (
                                    <span className="terminal-timestamp">{timestamp}</span>
                                )}
                                <span className="terminal-text">{text}</span>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
}
