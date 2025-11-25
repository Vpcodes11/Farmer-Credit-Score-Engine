import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import FarmerOnboarding from './components/FarmerOnboarding';
import FarmerProfile from './components/FarmerProfile';
import { authAPI } from './api/client';
import './styles/index.css';

const App: React.FC = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));
    const [currentFarmerId, setCurrentFarmerId] = useState<string | null>(null);

    return (
        <Router>
            <div className="min-h-screen bg-gray-50">
                {isAuthenticated ? (
                    <AuthenticatedApp
                        onLogout={() => {
                            localStorage.removeItem('token');
                            setIsAuthenticated(false);
                            setCurrentFarmerId(null);
                        }}
                        currentFarmerId={currentFarmerId}
                        onFarmerOnboarded={setCurrentFarmerId}
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
    const [isRegister, setIsRegister] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (isRegister) {
                await authAPI.register({
                    ...formData,
                    role: 'agent',
                });
                // Auto-login after registration
                const loginResponse = await authAPI.login({
                    username: formData.username,
                    password: formData.password,
                });
                localStorage.setItem('token', loginResponse.data.access_token);
            } else {
                const response = await authAPI.login({
                    username: formData.username,
                    password: formData.password,
                });
                localStorage.setItem('token', response.data.access_token);
            }
            onLogin();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Authentication failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="card max-w-md w-full">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        🌾 Farmer Credit Score
                    </h1>
                    <p className="text-gray-600">Field Agent Portal</p>
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
                            className="input-field"
                            value={formData.username}
                            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        />
                    </div>

                    {isRegister && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                required
                                className="input-field"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Password
                        </label>
                        <input
                            type="password"
                            required
                            className="input-field"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>

                    <button type="submit" disabled={loading} className="btn-primary w-full">
                        {loading ? 'Please wait...' : isRegister ? 'Register' : 'Login'}
                    </button>
                </form>

                <div className="mt-4 text-center">
                    <button
                        onClick={() => {
                            setIsRegister(!isRegister);
                            setError(null);
                        }}
                        className="text-sm text-green-600 hover:text-green-700"
                    >
                        {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
                    </button>
                </div>
            </div>
        </div>
    );
};

// Authenticated App Component
interface AuthenticatedAppProps {
    onLogout: () => void;
    currentFarmerId: string | null;
    onFarmerOnboarded: (id: string) => void;
}

const AuthenticatedApp: React.FC<AuthenticatedAppProps> = ({
    onLogout,
    currentFarmerId,
    onFarmerOnboarded,
}) => {
    return (
        <>
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2">
                        <span className="text-2xl">🌾</span>
                        <h1 className="text-xl font-bold text-gray-800">Farmer Credit Score</h1>
                    </Link>
                    <nav className="flex items-center gap-4">
                        <Link to="/" className="text-gray-600 hover:text-gray-800 font-medium">
                            Onboard
                        </Link>
                        {currentFarmerId && (
                            <Link
                                to={`/farmer/${currentFarmerId}`}
                                className="text-gray-600 hover:text-gray-800 font-medium"
                            >
                                View Profile
                            </Link>
                        )}
                        <button onClick={onLogout} className="btn-secondary text-sm py-2 px-4">
                            Logout
                        </button>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                <Routes>
                    <Route
                        path="/"
                        element={
                            <div>
                                <div className="mb-8 text-center">
                                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                                        Welcome, Field Agent
                                    </h2>
                                    <p className="text-gray-600">
                                        Onboard farmers and compute transparent credit scores
                                    </p>
                                </div>
                                <FarmerOnboarding onSuccess={onFarmerOnboarded} />
                            </div>
                        }
                    />
                    <Route
                        path="/farmer/:id"
                        element={
                            currentFarmerId ? (
                                <FarmerProfile farmerId={currentFarmerId} />
                            ) : (
                                <Navigate to="/" replace />
                            )
                        }
                    />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </main>

            {/* Footer */}
            <footer className="mt-16 bg-white border-t border-gray-200 py-6">
                <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-600">
                    <p>Farmer Credit Score Engine - Transparent rural lending powered by Agri Stack</p>
                </div>
            </footer>
        </>
    );
};

export default App;
