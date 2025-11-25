import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (data: { username: string; password: string }) =>
        apiClient.post('/auth/login', data),
};

// Farmers API
export const farmersAPI = {
    getAll: () => apiClient.get('/farmers'),
    getById: (id: string) => apiClient.get(`/farmers/${id}`),
};

// Scoring API
export const scoringAPI = {
    getHistory: (farmer_id: string) =>
        apiClient.get(`/score/${farmer_id}/history`),
};

export default apiClient;
