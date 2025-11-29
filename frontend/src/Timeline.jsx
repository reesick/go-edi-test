import React from 'react';
import './Timeline.css';
import Logger from './Logger';

function Timeline({ currentStep, totalSteps, onSeek }) {
    const handleSeek = (stepIndex) => {
        Logger.logReplay(stepIndex);
        onSeek(stepIndex);
    };

    if (totalSteps === 0) {
        return null;
    }

    const progress = (currentStep / totalSteps) * 100;

    return (
        <div className="timeline glass">
            <div className="timeline-header">
                <span className="timeline-label">Step {currentStep} of {totalSteps}</span>
                <span className="timeline-percentage">{Math.round(progress)}%</span>
            </div>

            <div className="timeline-bar">
                <div
                    className="timeline-progress"
                    style={{ width: `${progress}%` }}
                />
                <input
                    type="range"
                    min="0"
                    max={totalSteps - 1}
                    value={currentStep}
                    onChange={(e) => handleSeek(parseInt(e.target.value))}
                    className="timeline-slider"
                />
            </div>

            <div className="timeline-markers">
                <span>Start</span>
                <span>End</span>
            </div>
        </div>
    );
}

export default Timeline;
