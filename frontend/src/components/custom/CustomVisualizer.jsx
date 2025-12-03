// Custom Visualizer Component
// Multi-data-structure visualizer that can render arrays, trees, graphs,
// stacks, queues, and variables based on Gemini AI output

import React from 'react';
import './CustomVisualizer.css';

// Sub-component renderers
const ArrayVisualizer = ({ data }) => {
    const max_value = Math.max(...data.values.map(v => Math.abs(v))) || 1;

    return (
        <div className="array-visualizer">
            <div className="structure-label">{data.name}</div>
            <div className="array-container">
                {data.values.map((value, index) => {
                    const isHighlighted = data.highlights?.indices?.includes(index);
                    const color = isHighlighted
                        ? data.highlights.colors[data.highlights.indices.indexOf(index)]
                        : '#3498db';
                    const label = isHighlighted
                        ? data.highlights.labels[data.highlights.indices.indexOf(index)]
                        : null;

                    return (
                        <div key={index} className="array-element">
                            {label && <div className="element-label">{label}</div>}
                            <div
                                className="array-bar"
                                style={{
                                    backgroundColor: color,
                                    height: `${(Math.abs(value) / max_value) * 100}px`
                                }}
                            >
                                <span className="array-value">{value}</span>
                            </div>
                            <div className="array-index">{index}</div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

const VariablesPanel = ({ variables }) => {
    return (
        <div className="variables-panel">
            <div className="structure-label">Variables</div>
            <div className="variables-grid">
                {variables.map((variable, index) => (
                    <div key={index} className="variable-item">
                        <span className="variable-name">{variable.name}</span>
                        <span className="variable-value">{variable.value}</span>
                        <span className="variable-type">{variable.type}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Main visualizer component
const CustomVisualizer = ({ frame, currentFrameIndex, totalFrames }) => {
    if (!frame) {
        return (
            <div className="custom-visualizer">
                <div className="visualizer-placeholder">
                    <div className="placeholder-icon">🎨</div>
                    <div className="placeholder-text">
                        Run your code to see visualization
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="custom-visualizer">
            <div className="visualizer-header">
                <span className="visualizer-title">Visualization</span>
                <span className="frame-counter">
                    Frame {currentFrameIndex + 1} / {totalFrames}
                </span>
            </div>

            <div className="visualizer-content">
                <div className="frame-description">{frame.description}</div>

                <div className="structures-grid">
                    {/* Render arrays */}
                    {frame.arrays?.map((arr, index) => (
                        <ArrayVisualizer key={`array-${index}`} data={arr} />
                    ))}
                </div>

                {/* Render variables panel */}
                {frame.variables && frame.variables.length > 0 && (
                    <VariablesPanel variables={frame.variables} />
                )}
            </div>
        </div>
    );
};

export default CustomVisualizer;
