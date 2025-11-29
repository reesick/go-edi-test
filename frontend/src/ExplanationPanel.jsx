import React from 'react';
import './ExplanationPanel.css';
import Logger from './Logger';

function ExplanationPanel({ explanation }) {
    const panelRef = React.useRef(null);

    React.useEffect(() => {
        const handleScroll = () => {
            if (panelRef.current) {
                const { scrollTop, scrollHeight, clientHeight } = panelRef.current;
                const scrollDepth = ((scrollTop + clientHeight) / scrollHeight) * 100;
                Logger.logScroll(Math.round(scrollDepth));
            }
        };

        const panel = panelRef.current;
        if (panel) {
            panel.addEventListener('scroll', handleScroll);
            return () => panel.removeEventListener('scroll', handleScroll);
        }
    }, []);

    if (!explanation) {
        return (
            <div className="explanation-panel glass">
                <div className="explanation-header">
                    <h3>💡 AI Tutor</h3>
                </div>
                <div className="explanation-empty">
                    <p>Waiting for visualization to start...</p>
                </div>
            </div>
        );
    }

    const { mode, explanation: text, short_hint, confidence_estimate, followup_question } = explanation;

    const modeColors = {
        conceptual: 'var(--accent-blue)',
        operational: 'var(--accent-purple)',
        technical: 'var(--accent-orange)'
    };

    const modeIcons = {
        conceptual: '🎯',
        operational: '⚙️',
        technical: '🔬'
    };

    return (
        <div className="explanation-panel glass" ref={panelRef}>
            <div className="explanation-header">
                <h3>💡 AI Tutor</h3>
                <div className="mode-badge" style={{ background: modeColors[mode] }}>
                    {modeIcons[mode]} {mode}
                </div>
            </div>

            <div className="explanation-content">
                <p className="explanation-text">{text}</p>

                {short_hint && (
                    <div className="hint-box">
                        <strong>💡 Hint:</strong> {short_hint}
                    </div>
                )}

                {followup_question && (
                    <div className="question-box">
                        <strong>🤔 Think about:</strong> {followup_question}
                    </div>
                )}

                <div className="confidence-indicator">
                    <span>Confidence:</span>
                    <div className="confidence-dots">
                        {['low', 'medium', 'high'].map((level, idx) => (
                            <div
                                key={level}
                                className={`dot ${confidence_estimate === 'high' && idx <= 2 ? 'active' :
                                        confidence_estimate === 'medium' && idx <= 1 ? 'active' :
                                            confidence_estimate === 'low' && idx === 0 ? 'active' : ''
                                    }`}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ExplanationPanel;
