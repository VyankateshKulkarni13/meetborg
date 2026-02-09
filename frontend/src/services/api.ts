import axios from 'axios';

const API_URL = '/api/v1';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auth APIs
export const auth = {
    register: (data: { username: string; email?: string; password: string }) =>
        apiClient.post('/auth/register', data),

    login: (data: { username: string; password: string }) =>
        apiClient.post('/auth/login', data),

    getProfile: () => apiClient.get('/auth/me'),

    checkFirstUser: () => apiClient.get('/auth/first-user'),
};

// Platform APIs
export const platforms = {
    list: () => apiClient.get('/platforms'),

    create: (data: { platform_type: string; email: string; password?: string }) =>
        apiClient.post('/platforms', data),

    delete: (id: string) => apiClient.delete(`/platforms/${id}`),

    test: (id: string) => apiClient.post(`/platforms/${id}/test`),
};

export default apiClient;
