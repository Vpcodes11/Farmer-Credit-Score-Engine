import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import Analytics from './components/Analytics';
import FarmerList from './components/FarmerList';
import FarmerDetail from './components/FarmerDetail';
import { authAPI } from './api/client';
import './styles/index.css';

const App: React.FC = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
    const [selectedFarmerId, setSelectedFarmerId] = useState<string | null>(null);

    return (
        <Router>
            <div className="min-h-screen bg-gray-100">
                {isAuthenticated ? (
                    <AuthenticatedApp
                        onLogout={() => {
                            localStorage.removeItem('token');
                            setIsAuthenticated(false);
                        }}
                        selectedFarmerId={selectedFarmerId}
                        onSelectFarmer={setSelectedFarmerId}
                    />
                ) : (
                    <LoginPage onLogin={() => setIsAuthenticated(true)} />
                )}
            </div>
        </Router>
    );
};

// Login Component
const LoginPage: React.FC<{ onLogin: () => void }> = ({ onLogin }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await authAPI.login(formData);
            localStorage.setItem('token', response.data.access_token);
            onLogin();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="card max-w-md w-full">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        🏦 Farmer Credit Score
                    </h1>
                    <p className="text-gray-600">Bank Dashboard</p>
                </div>

                {error && (
                    <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                        <p className="text-sm text-red-800">{error}</p>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Username
                        </label>
                        <input
                            type="text"
                            required
                            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            required
                            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>

                    <button type="submit" disabled={loading} className="btn-primary w-full">
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-xs text-blue-800">
                        <strong>Note:</strong> Use your bank admin credentials to access the dashboard.
                    </p>
                </div>
            </div>
        </div>
    );
};

// Authenticated App Component
interface AuthenticatedAppProps {
    onLogout: () => void;
    selectedFarmerId: string | null;
    onSelectFarmer: (id: string) => void;
}

const AuthenticatedApp: React.FC<AuthenticatedAppProps> = ({
    onLogout,
    selectedFarmerId,
    onSelectFarmer,
}) => {
    const [currentView, setCurrentView] = useState<'analytics' | 'farmers' | 'detail'>('analytics');

    const handleSelectFarmer = (farmerId: string) => {
        onSelectFarmer(farmerId);
        setCurrentView('detail');
    };

    const handleBackToList = () => {
        setCurrentView('farmers');
        onSelectFarmer(null);
    };

    return (
        <>
            {/* Sidebar */}
            <div className="flex h-screen">
                <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
                    <div className="p-6 border-b border-gray-200">
                        <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                            <span>🏦</span>
                            Bank Dashboard
                        </h1>
                    </div>

                    <nav className="flex-1 p-4 space-y-2">
                        <button
                            onClick={() => setCurrentView('analytics')}
                            className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-colors ${currentView === 'analytics'
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-700 hover:bg-gray-50'
                                }`}
                        >
                            📊 Analytics
                        </button>
                        <button
                            onClick={() => setCurrentView('farmers')}
                            className={`w-full text-left px-4 py-3 rounded-lg font-medium transition-colors ${currentView === 'farmers' || currentView === 'detail'
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-700 hover:bg-gray-50'
                                }`}
                        >
                            👨‍🌾 All Farmers
                        </button>
                    </nav>

                    <div className="p-4 border-t border-gray-200">
                        <button onClick={onLogout} className="btn-secondary w-full text-sm">
                            Logout
                        </button>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 overflow-y-auto bg-gray-100">
                    <div className="max-w-7xl mx-auto p-8">
                        {currentView === 'analytics' && <Analytics />}
                        {currentView === 'farmers' && <FarmerList onSelectFarmer={handleSelectFarmer} />}
                        {currentView === 'detail' && selectedFarmerId && (
                            <FarmerDetail farmerId={selectedFarmerId} onBack={handleBackToList} />
                        )}
                    </div>
                </main>
            </div>
        </>
    );
};

export default App;
