// Custom Terminal Component
// Displays compilation output, execution output, and status messages

import React, { useEffect, useRef } from 'react';
import './CustomTerminal.css';

const CustomTerminal = ({ logs, isRunning }) => {
    const terminalRef = useRef(null);

    // Auto-scroll to bottom when new logs appear
    useEffect(() => {
        if (terminalRef.current) {
            terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
        }
    }, [logs]);

    const formatLog = (log) => {
        const { type, message, timestamp } = log;
        const time = new Date(timestamp).toLocaleTimeString();

        switch (type) {
            case 'success':
                return `[${time}] ✓ ${message}`;
            case 'error':
                return `[${time}] ✗ ${message}`;
            case 'warning':
                return `[${time}] ⚠ ${message}`;
            case 'info':
                return `[${time}] ℹ ${message}`;
            default:
                return `[${time}] ${message}`;
        }
    };

    return (
        <div className="custom-terminal">
            <div className="terminal-header">
                <span className="terminal-title">Terminal</span>
                <span className={`status-indicator ${isRunning ? 'running' : 'idle'}`}>
                    {isRunning ? '● Running' : '○ Idle'}
                </span>
            </div>
            <div className="terminal-content" ref={terminalRef}>
                {logs.length === 0 ? (
                    <div className="terminal-placeholder">
                        Ready. Write your algorithm and click Run...
                    </div>
                ) : (
                    logs.map((log, index) => (
                        <div key={index} className={`terminal-line terminal-${log.type}`}>
                            {formatLog(log)}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default CustomTerminal;
