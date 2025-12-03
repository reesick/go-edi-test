import { Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ModulePage from './pages/ModulePage';
import CustomCodePage from './pages/CustomCodePage';
import NotFound from './pages/NotFound';

export default function App() {
    return (
        <div className="app">
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/module/:moduleName" element={<ModulePage />} />
                <Route path="/custom" element={<CustomCodePage />} />
                <Route path="*" element={<NotFound />} />
            </Routes>
        </div>
    );
}
