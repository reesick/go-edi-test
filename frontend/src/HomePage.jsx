/**
 * HomePage.jsx - Landing page with mode selection
 */
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const modes = [
    {
        id: 'learn',
        name: '🎓 Learn Mode',
        description: 'Start from basics with detailed explanations',
        difficulty: 'Beginner',
        features: ['Small arrays (4-5 items)', 'Step-by-step guidance', 'Unlimited hints'],
        color: '#00d4aa'
    },
    {
        id: 'practice',
        name: '💪 Practice Mode',
        description: 'Reinforce understanding with repetition',
        difficulty: 'Intermediate',
        features: ['Medium arrays (8-10 items)', 'Focused learning', 'Limited hints'],
        color: '#64b5f6',
        requires: '50% mastery'
    },
    {
        id: 'challenge',
        name: '🏆 Challenge Mode',
        description: 'Test mastery with edge cases',
        difficulty: 'Advanced',
        features: ['Large arrays (15+ items)', 'Edge cases', 'Timed challenges'],
        color: '#e57373',
        requires: '80% mastery'
    },
    {
        id: 'explore',
        name: '🔬 Explore Mode',
        description: 'Compare algorithms side-by-side',
        difficulty: 'Any',
        features: ['Algorithm comparison', 'Performance metrics', 'Free experimentation'],
        color: '#ba68c8'
    },
    {
        id: 'custom',
        name: '💻 Custom Code',
        description: 'Write and run your own algorithms',
        difficulty: 'Any',
        features: ['Full code editor', 'Any sorting algorithm', 'Real-time visualization'],
        color: '#ffb74d'
    }
];

export default function HomePage() {
    const navigate = useNavigate();

    const handleModeSelect = (modeId) => {
        navigate(`/workspace/${modeId}`);
    };

    return (
        <div className="homepage">
            <header className="hero">
                <h1 className="hero-title">✨ Algorithm Learning Platform</h1>
                <p className="hero-subtitle">
                    Master algorithms through interactive visualization and AI-powered guidance
                </p>
            </header>

            <section className="modes-section">
                <h2>Choose Your Learning Path</h2>
                <div className="modes-grid">
                    {modes.map(mode => (
                        <div
                            key={mode.id}
                            className="mode-card"
                            style={{ '--mode-color': mode.color }}
                            onClick={() => handleModeSelect(mode.id)}
                        >
                            <div className="mode-header">
                                <h3>{mode.name}</h3>
                                <span className="mode-difficulty">{mode.difficulty}</span>
                            </div>

                            <p className="mode-description">{mode.description}</p>

                            {mode.requires && (
                                <div className="mode-requirement">
                                    <span>⚠️ Requires: {mode.requires}</span>
                                </div>
                            )}

                            <ul className="mode-features">
                                {mode.features.map((feature, idx) => (
                                    <li key={idx}>✓ {feature}</li>
                                ))}
                            </ul>

                            <button className="mode-button">
                                Start Learning →
                            </button>
                        </div>
                    ))}
                </div>
            </section>

            <section className="stats-section">
                <div className="stat-card">
                    <div className="stat-number">5</div>
                    <div className="stat-label">Learning Modes</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">3+</div>
                    <div className="stat-label">Algorithms</div>
                </div>
                <div className="stat-card">
                    <div className="stat-number">∞</div>
                    <div className="stat-label">Custom Code</div>
                </div>
            </section>
        </div>
    );
}
