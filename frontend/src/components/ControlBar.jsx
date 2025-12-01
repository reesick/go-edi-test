import './ControlBar.css';

export default function ControlBar({
    operations,
    currentOperation,
    onOperationChange,
    isPlaying,
    onPlayPause,
    onExecute,
    speed,
    onSpeedChange,
    currentStep,
    totalSteps
}) {
    return (
        <div className="control-bar">
            {/* Operation Selector */}
            <div className="control-group">
                <label>Algorithm:</label>
                <select
                    value={currentOperation}
                    onChange={(e) => onOperationChange(e.target.value)}
                    disabled={isPlaying}
                >
                    {operations.map(op => (
                        <option key={op.id} value={op.id}>
                            {op.name}
                        </option>
                    ))}
                </select>
            </div>

            {/* Execute Button */}
            <button
                onClick={onExecute}
                disabled={isPlaying}
                className="btn execute-btn"
            >
                ▶ Execute
            </button>

            {/* Play/Pause */}
            {totalSteps > 0 && (
                <>
                    <button onClick={onPlayPause} className="btn-secondary">
                        {isPlaying ? '❚❚ Pause' : '▶ Play'}
                    </button>

                    {/* Speed Control */}
                    <div className="control-group">
                        <label>Speed:</label>
                        <select value={speed} onChange={(e) => onSpeedChange(Number(e.target.value))}>
                            <option value={0.5}>0.5x</option>
                            <option value={1}>1x</option>
                            <option value={2}>2x</option>
                            <option value={4}>4x</option>
                        </select>
                    </div>

                    {/* Progress */}
                    <div className="progress-info">
                        <span>Step {currentStep} / {totalSteps}</span>
                        <div className="progress-bar">
                            <div
                                className="progress-fill"
                                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                            />
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
