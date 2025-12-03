import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css';

const MODULES = [
    {
        id: 'array',
        name: 'Array',
        description: 'Basic array operations - access, insert, delete, search'
    },
    {
        id: 'sorting',
        name: 'Sorting',
        description: 'Bubble, Selection, Insertion, Merge, Quick Sort'
    },
    {
        id: 'bitmask',
        name: 'Bitmask',
        description: 'Bit manipulation - set, clear, toggle, check bits'
    },
    {
        id: 'linkedlist',
        name: 'Linked List',
        description: 'Insert, delete, search, reverse linked nodes'
    },
    {
        id: 'binaryheap',
        name: 'Binary Heap',
        description: 'Min/Max heap - insert, extract, heapify'
    },
    {
        id: 'custom',
        name: 'Custom Code 🛠️',
        description: 'Write your own algorithms with AI-powered visualization',
        isCustom: true,
        badge: 'Beta'
    }
];

export default function HomePage() {
    const navigate = useNavigate();
    const [theme, setTheme] = useState('light');
    const [searchQuery, setSearchQuery] = useState('');

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    };

    const filteredModules = MODULES.filter(module =>
        module.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        module.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="homepage">
            {/* Header */}
            <header className="header">
                <div className="container">
                    <div className="header-content">
                        <h1 className="logo">AlgoVisual</h1>
                        <button onClick={toggleTheme} className="theme-toggle">
                            {theme === 'light' ? '🌙' : '☀️'}
                        </button>
                    </div>
                </div>
            </header>

            {/* Hero */}
            <section className="hero">
                <div className="container">
                    <h2 className="hero-title">Algorithm Visualization Platform</h2>
                    <p className="hero-subtitle text-muted">
                        Learn data structures and algorithms through animation
                    </p>
                </div>
            </section>

            {/* Search */}
            <section className="search-section">
                <div className="container">
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search modules..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
            </section>

            {/* Modules Grid */}
            <section className="modules-section">
                <div className="container">
                    <div className="modules-grid">
                        {filteredModules.map(module => (
                            <div
                                key={module.id}
                                className={`module-card card ${module.isCustom ? 'custom-card' : ''}`}
                                onClick={() => navigate(module.isCustom ? '/custom' : `/module/${module.id}`)}
                            >
                                <h3 className="module-name">
                                    {module.name}
                                    {module.badge && <span className="beta-badge">{module.badge}</span>}
                                </h3>
                                <p className="module-desc text-muted">{module.description}</p>
                                <div className="module-arrow">→</div>
                            </div>
                        ))}
                    </div>

                    {filteredModules.length === 0 && (
                        <div className="no-results text-center text-muted">
                            <p>No modules found matching "{searchQuery}"</p>
                        </div>
                    )}
                </div>
            </section>

            {/* Footer */}
            <footer className="footer">
                <div className="container text-center text-muted">
                    <p>© 2024 AlgoVisual - Educational Algorithm Visualization</p>
                </div>
            </footer>
        </div>
    );
}
