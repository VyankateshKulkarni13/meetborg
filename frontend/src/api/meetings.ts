// API Client for Meetings
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Meeting {
    id: string;
    url: string;
    platform: 'google_meet' | 'zoom' | 'microsoft_teams' | 'webex' | 'jitsi' | 'other';
    meeting_code: string | null;
    title: string;
    scheduled_time: string | null;
    duration_minutes: number;
    purpose: string | null;
    status: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'failed';
    user_id: string;
    created_at: string;
    updated_at: string;
    join_attempted_at: string | null;
    join_successful: string | null;
}

export interface MeetingCreate {
    url: string;
    title: string;
    scheduled_time?: string;
    duration_minutes?: number;
    purpose?: string;
}

export interface MeetingUpdate {
    title?: string;
    scheduled_time?: string;
    duration_minutes?: number;
    purpose?: string;
    status?: 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'failed';
}

export interface PlatformDetectionResponse {
    platform: string;
    meeting_code: string | null;
    is_valid: boolean;
    message: string;
}

// Get auth token from localStorage
const getAuthToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('token');
    }
    return null;
};

// API Client
export const meetingsAPI = {
    // Create a new meeting
    create: async (data: MeetingCreate): Promise<Meeting> => {
        const response = await axios.post<Meeting>(`${API_BASE_URL}/meetings`, data, {
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
        return response.data;
    },

    // List all meetings
    list: async (params?: { skip?: number; limit?: number; status_filter?: string }) => {
        const response = await axios.get(`${API_BASE_URL}/meetings`, {
            params,
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
        return response.data;
    },

    // Get a specific meeting
    get: async (id: string): Promise<Meeting> => {
        const response = await axios.get<Meeting>(`${API_BASE_URL}/meetings/${id}`, {
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
        return response.data;
    },

    // Update a meeting
    update: async (id: string, data: MeetingUpdate): Promise<Meeting> => {
        const response = await axios.put<Meeting>(`${API_BASE_URL}/meetings/${id}`, data, {
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
        return response.data;
    },

    // Delete a meeting
    delete: async (id: string): Promise<void> => {
        await axios.delete(`${API_BASE_URL}/meetings/${id}`, {
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
    },

    // Trigger join
    triggerJoin: async (id: string) => {
        const response = await axios.post(`${API_BASE_URL}/meetings/${id}/join`, {}, {
            headers: {
                Authorization: `Bearer ${getAuthToken()}`,
            },
        });
        return response.data;
    },

    // Detect platform from URL (no auth required)
    detectPlatform: async (url: string): Promise<PlatformDetectionResponse> => {
        const response = await axios.post<PlatformDetectionResponse>(
            `${API_BASE_URL}/meetings/detect-platform`,
            null,
            {
                params: { url },
            }
        );
        return response.data;
    },
};
