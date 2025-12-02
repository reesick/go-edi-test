import './VisualizerControls.css';

export default function VisualizerControls({
    isPlaying,
    onPlayPause,
    currentStep,
    totalSteps,
    speed,
    onSpeedChange,
    onStepChange
}) {
    const handleProgressClick = (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const percent = (e.clientX - rect.left) / rect.width;
        const step = Math.floor(percent * totalSteps);
        onStepChange(Math.max(0, Math.min(step, totalSteps - 1)));
    };

    const handlePrevious = () => {
        if (currentStep > 0) {
            onStepChange(currentStep - 1);
        }
    };

    const handleNext = () => {
        if (currentStep < totalSteps - 1) {
            onStepChange(currentStep + 1);
        }
    };

    const speedOptions = [0.5, 1, 2, 3];
    const hasSteps = totalSteps > 0;

    return (
        <div className="visualizer-controls">
            {/* Play/Pause Button */}
            <button
                className="control-button"
                onClick={onPlayPause}
                disabled={!hasSteps}
                title={isPlaying ? 'Pause' : 'Play'}
            >
                {isPlaying ? '⏸' : '▶'}
            </button>

            {/* Previous/Next Step Buttons */}
            <div className="step-buttons">
                <button
                    className="step-button"
                    onClick={handlePrevious}
                    disabled={!hasSteps || currentStep === 0}
                    title="Previous step"
                >
                    ⏮
                </button>
                <button
                    className="step-button"
                    onClick={handleNext}
                    disabled={!hasSteps || currentStep >= totalSteps - 1}
                    title="Next step"
                >
                    ⏭
                </button>
            </div>

            <div className="controls-divider"></div>

            {/* Progress Bar */}
            <div className="progress-container">
                <div
                    className="progress-bar"
                    onClick={handleProgressClick}
                    title="Seek to step"
                >
                    <div
                        className="progress-filled"
                        style={{
                            width: hasSteps ? `${((currentStep + 1) / totalSteps) * 100}%` : '0%'
                        }}
                    />
                </div>
                <div className="step-indicator">
                    {hasSteps ? `Step ${currentStep + 1} / ${totalSteps}` : 'No steps'}
                </div>
            </div>

            <div className="controls-divider"></div>

            {/* Speed Selector */}
            <div className="speed-selector">
                {speedOptions.map(s => (
                    <button
                        key={s}
                        className={`speed-option ${speed === s ? 'active' : ''}`}
                        onClick={() => onSpeedChange(s)}
                        title={`${s}x speed`}
                    >
                        {s}x
                    </button>
                ))}
            </div>
        </div>
    );
}
