import React from 'react';
import VisualizerControls from './VisualizerControls';
import './Visualizer.css';

export default function Visualizer({ module, data, highlights = [], controlsProps }) {
    if (!data) {
        return (
            <div className="visualizer-container">
                <div className="visualizer">
                    <div className="empty-viz">
                        <p className="text-muted">Click "Run" to see visualization</p>
                    </div>
                </div>
                {controlsProps && <VisualizerControls {...controlsProps} />}
            </div>
        );
    }

    // Render based on module type
    const renderVisualization = () => {
        switch (module) {
            case 'array':
            case 'sorting':
            case 'searching':
                return <ArrayVisualizer data={data} highlights={highlights} />;
            case 'linkedlist':
                return <LinkedListVisualizer data={data} highlights={highlights} />;
            case 'bitmask':
                return <BitmaskVisualizer data={data} highlights={highlights} />;
            case 'binaryheap':
                return <HeapVisualizer data={data} highlights={highlights} />;
            default:
                return <div>Unsupported module type</div>;
        }
    };

    return (
        <div className="visualizer-container">
            <div className="visualizer">
                {renderVisualization()}
            </div>
            {controlsProps && <VisualizerControls {...controlsProps} />}
        </div>
    );
}

// Array/Sorting Visualizer
function ArrayVisualizer({ data, highlights }) {
    if (!Array.isArray(data)) return null;

    const maxVal = Math.max(...data, 1);
    const minVal = Math.min(...data, 0);
    const range = maxVal - minVal || 1;

    // Minimum height to ensure small values are visible
    const MIN_HEIGHT = 40;
    const MAX_HEIGHT = 250;
    const AVAILABLE_HEIGHT = MAX_HEIGHT - MIN_HEIGHT;

    return (
        <div className="array-viz">
            {data.map((value, index) => {
                const isHighlighted = highlights.includes(index);

                // Proportional scaling: map value to [MIN_HEIGHT, MAX_HEIGHT]
                const normalizedValue = (value - minVal) / range;
                const height = MIN_HEIGHT + (normalizedValue * AVAILABLE_HEIGHT);

                return (
                    <div key={index} className="bar-wrapper">
                        <div
                            className={`bar ${isHighlighted ? 'highlighted' : ''}`}
                            style={{ height: `${height}px` }}
                        >
                            <span className="bar-value">{value}</span>
                        </div>
                        <span className="bar-index">{index}</span>
                    </div>
                );
            })}
        </div>
    );
}

// Linked List Visualizer
function LinkedListVisualizer({ data }) {
    if (!Array.isArray(data)) return null;

    return (
        <div className="linkedlist-viz">
            {data.map((value, index) => (
                <React.Fragment key={index}>
                    <div className="node">
                        <span>{value}</span>
                    </div>
                    {index < data.length - 1 && <div className="arrow">→</div>}
                </React.Fragment>
            ))}
        </div>
    );
}

// Bitmask Visualizer
function BitmaskVisualizer({ data }) {
    const bits = data.toString(2).padStart(8, '0').split('');

    return (
        <div className="bitmask-viz">
            {bits.map((bit, index) => (
                <div key={index} className={`bit ${bit === '1' ? 'set' : 'unset'}`}>
                    {bit}
                </div>
            ))}
        </div>
    );
}

// Binary Heap Visualizer (simplified as array for now)
function HeapVisualizer({ data }) {
    return <ArrayVisualizer data={data} highlights={[]} />;
}
