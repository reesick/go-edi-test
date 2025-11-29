import React from 'react';
import './VisualizerEngine.css';

function VisualizerEngine({ array, pointers, swapOccurred, action }) {
    if (!array || array.length === 0) {
        return (
            <div className="visualizer glass">
                <div className="empty-state">
                    <p>🎯 Enter an array and click Start to begin</p>
                </div>
            </div>
        );
    }

    const maxValue = Math.max(...array);
    const i = pointers?.i;
    const j = pointers?.j;

    return (
        <div className="visualizer glass">
            <div className="bars-container">
                {array.map((value, index) => {
                    const height = (value / maxValue) * 100;

                    let className = 'bar';
                    let barColor = 'var(--accent-blue)';

                    // Highlight active pointers
                    if (index === i) {
                        className += ' bar-active-i';
                        barColor = 'var(--accent-purple)';
                    } else if (index === j) {
                        className += ' bar-active-j';
                        barColor = 'var(--accent-pink)';
                    }

                    // Animation classes
                    if (action === 'compare' && (index === i || index === j)) {
                        className += ' bar-comparing';
                    }
                    if (swapOccurred && (index === i || index === j)) {
                        className += ' bar-swapping';
                    }
                    if (action === 'done') {
                        className += ' bar-done';
                    }

                    return (
                        <div
                            key={index}
                            className="bar-wrapper"
                            style={{ flex: 1 }}
                        >
                            <div
                                className={className}
                                style={{
                                    height: `${height}%`,
                                    background: barColor,
                                    boxShadow: `0 0 20px ${barColor}40`
                                }}
                            >
                                <span className="bar-value">{value}</span>
                            </div>
                            <span className="bar-index">{index}</span>
                        </div>
                    );
                })}
            </div>

            <div className="action-indicator">
                {action === 'compare' && '🔍 Comparing'}
                {action === 'swap' && '🔄 Swapping'}
                {action === 'done' && '✅ Sorted!'}
            </div>
        </div>
    );
}

export default VisualizerEngine;
