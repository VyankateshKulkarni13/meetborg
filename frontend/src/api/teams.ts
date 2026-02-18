import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export interface TeamsSessionCreate {
    meeting_url: string;
    display_name: string;
    mic_enabled: boolean;
    camera_enabled: boolean;
    audio_input_device?: string;
    audio_output_device?: string;
    video_device?: string;
}

export interface TeamsSessionResponse {
    session_id: string;
    status: string;
    created_at: string;
}

export const teamsAPI = {
    joinSession: async (data: TeamsSessionCreate): Promise<TeamsSessionResponse> => {
        const response = await axios.post(`${API_URL}/teams/join-session`, data);
        return response.data;
    }
};
