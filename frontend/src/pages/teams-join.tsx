import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import {
    Box,
    Button,
    Container,
    Typography,
    Paper,
    TextField,
    Grid,
    IconButton,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Switch,
    FormControlLabel,
    Avatar,
    Stack,
    CircularProgress
} from '@mui/material';
import {
    Mic,
    MicOff,
    Videocam,
    VideocamOff,
    Settings,
    ArrowBack,
    Groups
} from '@mui/icons-material';
import { teamsAPI } from '../api/teams';

const TeamsJoinPage: React.FC = () => {
    const router = useRouter();
    const { url } = router.query;

    // State
    const [displayName, setDisplayName] = useState('Meeting Assistant');
    const [micEnabled, setMicEnabled] = useState(false);
    const [cameraEnabled, setCameraEnabled] = useState(false);
    const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
    const [selectedAudioInput, setSelectedAudioInput] = useState('');
    const [selectedAudioOutput, setSelectedAudioOutput] = useState('');
    const [selectedVideoInput, setSelectedVideoInput] = useState('');
    const [joining, setJoining] = useState(false);

    // Refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const streamRef = useRef<MediaStream | null>(null);

    // Initialize Devices
    useEffect(() => {
        const getDevices = async () => {
            try {
                // Request permissions first to enumerate labels
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
                stream.getTracks().forEach(track => track.stop()); // Stop immediately, just needed permission

                const deviceList = await navigator.mediaDevices.enumerateDevices();
                setDevices(deviceList);

                // Set defaults
                const audioInputs = deviceList.filter(d => d.kind === 'audioinput');
                const audioOutputs = deviceList.filter(d => d.kind === 'audiooutput');
                const videoInputs = deviceList.filter(d => d.kind === 'videoinput');

                if (audioInputs.length > 0) setSelectedAudioInput(audioInputs[0].deviceId);
                if (audioOutputs.length > 0) setSelectedAudioOutput(audioOutputs[0].deviceId);
                if (videoInputs.length > 0) setSelectedVideoInput(videoInputs[0].deviceId);

            } catch (err) {
                console.error("Error accessing media devices", err);
            }
        };

        getDevices();
    }, []);

    // Handle Camera Stream
    useEffect(() => {
        const startStream = async () => {
            if (cameraEnabled) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({
                        video: { deviceId: selectedVideoInput ? { exact: selectedVideoInput } : undefined }
                    });
                    if (videoRef.current) {
                        videoRef.current.srcObject = stream;
                    }
                    streamRef.current = stream;
                } catch (err) {
                    console.error("Error starting camera", err);
                }
            } else {
                if (streamRef.current) {
                    streamRef.current.getTracks().forEach(track => track.stop());
                }
                if (videoRef.current) {
                    videoRef.current.srcObject = null;
                }
            }
        };

        startStream();

        return () => {
            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }
        };
    }, [cameraEnabled, selectedVideoInput]);

    const handleJoin = async () => {
        if (!url) return;

        setJoining(true);
        try {
            await teamsAPI.joinSession({
                meeting_url: url as string,
                display_name: displayName,
                mic_enabled: micEnabled,
                camera_enabled: cameraEnabled,
                audio_input_device: selectedAudioInput,
                audio_output_device: selectedAudioOutput,
                video_device: selectedVideoInput
            });

            // Navigate back or show success
            router.push('/meetings');
        } catch (error) {
            console.error("Join failed", error);
            setJoining(false);
            alert("Failed to join meeting. Check backend logs.");
        }
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: '#1F1F1F', color: 'white', p: 3 }}>
            <Container maxWidth="lg">
                <Button
                    startIcon={<ArrowBack />}
                    onClick={() => router.back()}
                    sx={{ color: '#BDBDBD', mb: 4 }}
                >
                    Back to Meetings
                </Button>

                <Grid container spacing={4}>
                    {/* Left Panel - Preview */}
                    <Grid item xs={12} md={8}>
                        <Box sx={{
                            width: '100%',
                            height: 500,
                            bgcolor: '#000',
                            borderRadius: 2,
                            overflow: 'hidden',
                            position: 'relative',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '1px solid #333'
                        }}>
                            {cameraEnabled ? (
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    playsInline
                                    muted
                                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                />
                            ) : (
                                <Box sx={{ textAlign: 'center' }}>
                                    <Avatar sx={{ width: 80, height: 80, bgcolor: '#6264A7', fontSize: 32, mx: 'auto', mb: 2 }}>
                                        {displayName.charAt(0) || 'U'}
                                    </Avatar>
                                    <Typography variant="h6" color="#BDBDBD">Camera is off</Typography>
                                </Box>
                            )}

                            {/* Controls Overlay */}
                            <Box sx={{
                                position: 'absolute',
                                bottom: 20,
                                left: '50%',
                                transform: 'translateX(-50%)',
                                display: 'flex',
                                gap: 2,
                                bgcolor: 'rgba(0,0,0,0.6)',
                                p: 1.5,
                                borderRadius: 4
                            }}>
                                <IconButton
                                    onClick={() => setMicEnabled(!micEnabled)}
                                    sx={{
                                        bgcolor: micEnabled ? '#6264A7' : '#333',
                                        color: 'white',
                                        '&:hover': { bgcolor: micEnabled ? '#515391' : '#444' }
                                    }}
                                >
                                    {micEnabled ? <Mic /> : <MicOff />}
                                </IconButton>
                                <IconButton
                                    onClick={() => setCameraEnabled(!cameraEnabled)}
                                    sx={{
                                        bgcolor: cameraEnabled ? '#6264A7' : '#333',
                                        color: 'white',
                                        '&:hover': { bgcolor: cameraEnabled ? '#515391' : '#444' }
                                    }}
                                >
                                    {cameraEnabled ? <Videocam /> : <VideocamOff />}
                                </IconButton>
                            </Box>
                        </Box>
                    </Grid>

                    {/* Right Panel - Settings */}
                    <Grid item xs={12} md={4}>
                        <Paper sx={{ p: 4, bgcolor: '#2B2B2B', color: 'white', borderRadius: 2, height: '100%' }}>
                            <Typography variant="h5" fontWeight="bold" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Groups sx={{ color: '#6264A7' }} />
                                Join Meeting
                            </Typography>

                            <Box sx={{ mt: 4, display: 'flex', flexDirection: 'column', gap: 3 }}>
                                <TextField
                                    label="Display Name"
                                    fullWidth
                                    value={displayName}
                                    onChange={(e) => setDisplayName(e.target.value)}
                                    variant="outlined"
                                    sx={{
                                        '& .MuiOutlinedInput-root': { color: 'white', '& fieldset': { borderColor: '#555' } },
                                        '& .MuiInputLabel-root': { color: '#BDBDBD' }
                                    }}
                                />

                                <FormControl fullWidth>
                                    <InputLabel sx={{ color: '#BDBDBD' }}>Audio Device</InputLabel>
                                    <Select
                                        value={selectedAudioInput}
                                        label="Audio Device"
                                        onChange={(e) => setSelectedAudioInput(e.target.value)}
                                        sx={{ color: 'white', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#555' } }}
                                    >
                                        {devices.filter(d => d.kind === 'audioinput').map(d => (
                                            <MenuItem key={d.deviceId} value={d.deviceId}>{d.label || `Microphone ${d.deviceId.slice(0, 5)}`}</MenuItem>
                                        ))}
                                    </Select>
                                </FormControl>

                                <Box sx={{ py: 2 }}>
                                    <Typography variant="subtitle2" color="#BDBDBD" gutterBottom>AUDIO SETTINGS</Typography>
                                    <FormControlLabel
                                        control={<Switch checked={!micEnabled} onChange={() => setMicEnabled(false)} />}
                                        label="Don't use audio"
                                        sx={{ color: 'white' }}
                                    />
                                </Box>

                                <Button
                                    variant="contained"
                                    size="large"
                                    fullWidth
                                    onClick={handleJoin}
                                    disabled={joining}
                                    sx={{
                                        bgcolor: '#6264A7',
                                        py: 1.5,
                                        fontWeight: 'bold',
                                        fontSize: '1.1rem',
                                        '&:hover': { bgcolor: '#525494' }
                                    }}
                                >
                                    {joining ? <CircularProgress size={24} color="inherit" /> : 'Join now'}
                                </Button>

                                <Button
                                    variant="outlined"
                                    fullWidth
                                    onClick={() => router.back()}
                                    sx={{
                                        color: 'white',
                                        borderColor: '#555',
                                        '&:hover': { borderColor: '#777' }
                                    }}
                                >
                                    Cancel
                                </Button>
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>
            </Container>
        </Box>
    );
};

export default TeamsJoinPage;
