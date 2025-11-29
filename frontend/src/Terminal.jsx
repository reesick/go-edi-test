/**
 * Terminal.jsx - Premium Terminal/Console Component
 * Features: Syntax highlighting, auto-scroll, copy output, clear
 */
import { useState, useRef, useEffect } from 'react';
import './Terminal.css';

export default function Terminal({ output = [], title = "Terminal Output" }) {
    const [filter, setFilter] = useState('all'); // all, info, error, success
    const terminalRef = useRef(null);
    const [autoScroll, setAutoScroll] = useState(true);

    // Auto-scroll to bottom when new output arrives
    useEffect(() => {
        if (autoScroll && terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [output, autoScroll]);

    const handleCopyAll = () => {
        const text = output.map(line => line.text || line).join('\n');
        navigator.clipboard.writeText(text);
    };

    const handleClear = () => {
        // Trigger parent to clear output
        window.dispatchEvent(new CustomEvent('terminal-clear'));
    };

    const getLineClass = (line) => {
        if (typeof line === 'string') return 'terminal-line-default';

        const type = line.type || 'default';
        return `terminal-line-${type}`;
    };

    const getLineIcon = (line) => {
        if (typeof line === 'string') return '›';

        const icons = {
            info: 'ℹ️',
            success: '✓',
            error: '✗',
            warning: '⚠️',
            step: '▶',
            default: '›'
        };
        return icons[line.type] || icons.default;
    };

    const filteredOutput = output.filter(line => {
        if (filter === 'all') return true;
        const type = typeof line === 'string' ? 'default' : line.type;
        return type === filter;
    });

    return (
        <div className="terminal-container">
            {/* Header */}
            <div className="terminal-header">
                <div className="terminal-title">
                    <span className="terminal-icon">💻</span>
                    <span>{title}</span>
                    <span className="terminal-badge">{output.length} lines</span>
                </div>

                <div className="terminal-controls">
                    {/* Filter */}
                    <select
                        className="terminal-filter"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    >
                        <option value="all">All</option>
                        <option value="info">Info</option>
                        <option value="success">Success</option>
                        <option value="error">Errors</option>
                        <option value="warning">Warnings</option>
                    </select>

                    {/* Auto-scroll toggle */}
                    <button
                        className={`terminal-btn ${autoScroll ? 'active' : ''}`}
                        onClick={() => setAutoScroll(!autoScroll)}
                        title="Toggle auto-scroll"
                    >
                        {autoScroll ? '📌 Auto' : '📌 Off'}
                    </button>

                    {/* Actions */}
                    <button className="terminal-btn" onClick={handleCopyAll} title="Copy all output">
                        📋 Copy
                    </button>
                    <button className="terminal-btn" onClick={handleClear} title="Clear terminal">
                        🗑️ Clear
                    </button>
                </div>
            </div>

            {/* Output Area */}
            <div className="terminal-output" ref={terminalRef}>
                {filteredOutput.length === 0 ? (
                    <div className="terminal-empty">
                        <span className="terminal-empty-icon">📭</span>
                        <p>No output yet. Run your code to see results here.</p>
                    </div>
                ) : (
                    filteredOutput.map((line, index) => {
                        const text = typeof line === 'string' ? line : line.text;
                        const timestamp = typeof line === 'object' ? line.timestamp : null;

                        return (
                            <div key={index} className={getLineClass(line)}>
                                <span className="terminal-line-icon">{getLineIcon(line)}</span>
                                {timestamp && (
                                    <span className="terminal-timestamp">{timestamp}</span>
                                )}
                                <span className="terminal-line-text">{text}</span>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Status Bar */}
            <div className="terminal-status">
                <span>Lines: {output.length}</span>
                <span>Filtered: {filteredOutput.length}</span>
                <span>{autoScroll ? '🔄 Auto-scroll ON' : '⏸️ Auto-scroll OFF'}</span>
            </div>
        </div>
    );
}


// Example usage:
// <Terminal output={[
//   "Starting execution...",
//   { type: 'info', text: 'Processing array [5, 2, 8, 1]', timestamp: '00:01' },
//   { type: 'success', text: 'Step 1 complete', timestamp: '00:02' },
//   { type: 'error', text: 'Index out of bounds', timestamp: '00:03' },
// ]} />
