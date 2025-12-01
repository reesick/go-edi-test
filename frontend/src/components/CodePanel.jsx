import './CodePanel.css';

export default function CodePanel({ operation, code, currentLine }) {
    const lines = code.split('\n');

    return (
        <div className="code-panel">
            <div className="code-header">
                <h3>Code</h3>
                <span className="operation-label text-muted">{operation}</span>
            </div>

            <div className="code-content">
                {lines.map((line, index) => (
                    <div
                        key={index}
                        className={`code-line ${currentLine === index + 1 ? 'active' : ''}`}
                    >
                        <span className="line-number">{index + 1}</span>
                        <pre className="line-code">{line || ' '}</pre>
                    </div>
                ))}
            </div>
        </div>
    );
}
