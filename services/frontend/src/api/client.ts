import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add JWT token
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

// Response interceptor for error handling
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
    register: (data: { username: string; email: string; password: string; role: string }) =>
        apiClient.post('/auth/register', data),

    login: (data: { username: string; password: string }) =>
        apiClient.post('/auth/login', data),
};

// Farmers API
export const farmersAPI = {
    create: (data: {
        farmer_id: string;
        name: string;
        mobile: string;
        consent_given: boolean;
    }) => apiClient.post('/farmers', data),

    getById: (id: string) => apiClient.get(`/farmers/${id}`),

    getAll: () => apiClient.get('/farmers'),
};

// Scoring API
export const scoringAPI = {
    computeScore: (farmer_id: string) =>
        apiClient.post('/score', { farmer_id }),

    getHistory: (farmer_id: string) =>
        apiClient.get(`/score/${farmer_id}/history`),
};

// Loan API
export const loanAPI = {
    getQuote: (data: {
        farmer_id: string;
        loan_amount: number;
        crop_type: string;
    }) => apiClient.post('/loan/quote', data),
};

// System API
export const systemAPI = {
    health: () => apiClient.get('/healthz'),
};

export default apiClient;
