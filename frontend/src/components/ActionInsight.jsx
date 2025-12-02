import './ActionInsight.css';

export default function ActionInsight({ action }) {
    if (!action) return null;

    return (
        <div className="action-insight">
            <div className="insight-header">
                <span className="insight-icon">🤖</span>
                <span className="insight-title">What's Happening:</span>
            </div>
            <div className="insight-text">
                {action}
            </div>
        </div>
    );
}
