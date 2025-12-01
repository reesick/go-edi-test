import { useNavigate } from 'react-router-dom';
import './NotFound.css';

export default function NotFound() {
    const navigate = useNavigate();

    return (
        <div className="not-found">
            <div className="container text-center">
                <h1 className="error-code">404</h1>
                <p className="error-message">Page not found</p>
                <button onClick={() => navigate('/')} className="btn">
                    Go Home
                </button>
            </div>
        </div>
    );
}
