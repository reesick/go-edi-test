import React from 'react';
import './ControlPanel.css';

function ControlPanel({ onRun, onPause, onSpeedChange, isRunning }) {
    const [arrayInput, setArrayInput] = React.useState('5, 2, 8, 1, 9');
    const [algorithm, setAlgorithm] = React.useState('bubble_sort');
    const [speed, setSpeed] = React.useState(1.0);

    const handleStart = () => {
        const array = arrayInput
            .split(',')
            .map(x => parseInt(x.trim()))
            .filter(x => !isNaN(x));

        if (array.length === 0) {
            alert('Please enter valid numbers');
            return;
        }

        onRun(array, algorithm, speed);
    };

    const handleRandomize = () => {
        const size = 8;
        const randomArray = Array.from({ length: size }, () =>
            Math.floor(Math.random() * 100) + 1
        );
        setArrayInput(randomArray.join(', '));
    };

    const handleSpeedChange = (newSpeed) => {
        setSpeed(newSpeed);
        onSpeedChange(newSpeed);
    };

    return (
        <div className="control-panel glass">
            <h2 className="gradient-text">Algorithm Visualizer</h2>

            <div className="control-group">
                <label>Array Input</label>
                <div className="input-row">
                    <input
                        type="text"
                        value={arrayInput}
                        onChange={(e) => setArrayInput(e.target.value)}
                        placeholder="e.g., 5, 2, 8, 1, 9"
                        disabled={isRunning}
                    />
                    <button
                        className="btn btn-secondary"
                        onClick={handleRandomize}
                        disabled={isRunning}
                    >
                        🎲 Random
                    </button>
                </div>
            </div>

            <div className="control-group">
                <label>Algorithm</label>
                <select
                    value={algorithm}
                    onChange={(e) => setAlgorithm(e.target.value)}
                    disabled={isRunning}
                >
                    <option value="bubble_sort">Bubble Sort</option>
                    <option value="insertion_sort" disabled>Insertion Sort (Coming Soon)</option>
                    <option value="selection_sort" disabled>Selection Sort (Coming Soon)</option>
                </select>
            </div>

            <div className="control-group">
                <label>Playback Speed</label>
                <div className="speed-controls">
                    {[0.5, 1.0, 1.5, 2.0].map(s => (
                        <button
                            key={s}
                            className={`btn ${speed === s ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => handleSpeedChange(s)}
                            disabled={!isRunning}
                        >
                            {s}x
                        </button>
                    ))}
                </div>
            </div>

            <div className="control-actions">
                {!isRunning ? (
                    <button className="btn btn-primary" onClick={handleStart}>
                        ▶️ Start Visualization
                    </button>
                ) : (
                    <button className="btn btn-secondary" onClick={onPause}>
                        ⏸️ Pause
                    </button>
                )}
            </div>
        </div>
    );
}

export default ControlPanel;
