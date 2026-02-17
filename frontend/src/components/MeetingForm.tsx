import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    Box,
    Typography,
    Chip,
    Alert,
    CircularProgress,
} from '@mui/material';
import { LocalizationProvider, DateTimePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { meetingsAPI, MeetingCreate } from '../api/meetings';
import {
    VideoCall as GoogleMeetIcon,
    Videocam as ZoomIcon,
    Groups as TeamsIcon,
    CameraAlt as WebexIcon,
    Public as JitsiIcon,
    Link as OtherIcon,
} from '@mui/icons-material';

interface MeetingFormProps {
    open: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

const MeetingForm: React.FC<MeetingFormProps> = ({ open, onClose, onSuccess }) => {
    const [url, setUrl] = useState('');
    const [title, setTitle] = useState('');
    const [scheduledTime, setScheduledTime] = useState<Date | null>(null);
    const [duration, setDuration] = useState(60);
    const [purpose, setPurpose] = useState('');

    const [platform, setPlatform] = useState<string | null>(null);
    const [meetingCode, setMeetingCode] = useState<string | null>(null);
    const [detecting, setDetecting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    // Debounced platform detection
    useEffect(() => {
        if (!url || url.length < 10) {
            setPlatform(null);
            setMeetingCode(null);
            return;
        }

        const timeoutId = setTimeout(async () => {
            setDetecting(true);
            try {
                const result = await meetingsAPI.detectPlatform(url);
                if (result.is_valid) {
                    setPlatform(result.platform);
                    setMeetingCode(result.meeting_code);
                    setError(null);
                } else {
                    setPlatform(null);
                    setMeetingCode(null);
                    setError('Could not detect a supported platform from this URL');
                }
            } catch (err) {
                console.error('Platform detection error:', err);
            } finally {
                setDetecting(false);
            }
        }, 500);

        return () => clearTimeout(timeoutId);
    }, [url]);

    const handleSubmit = async () => {
        if (!url || !title) {
            setError('URL and Title are required');
            return;
        }

        if (!platform) {
            setError('Please enter a valid meeting URL from a supported platform');
            return;
        }

        setSubmitting(true);
        setError(null);

        try {
            const data: MeetingCreate = {
                url,
                title,
                scheduled_time: scheduledTime?.toISOString(),
                duration_minutes: duration,
                purpose: purpose || undefined,
            };

            await meetingsAPI.create(data);
            onSuccess();
            handleClose();
        } catch (err: any) {
            // Handle Pydantic validation errors
            const detail = err.response?.data?.detail;
            if (Array.isArray(detail)) {
                // Pydantic validation error format
                const errorMessages = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
                setError(errorMessages);
            } else if (typeof detail === 'string') {
                setError(detail);
            } else {
                setError('Failed to create meeting');
            }
        } finally {
            setSubmitting(false);
        }
    };

    const handleClose = () => {
        setUrl('');
        setTitle('');
        setScheduledTime(null);
        setDuration(60);
        setPurpose('');
        setPlatform(null);
        setMeetingCode(null);
        setError(null);
        onClose();
    };

    const getPlatformIcon = (platformType: string) => {
        switch (platformType) {
            case 'google_meet':
                return <GoogleMeetIcon />;
            case 'zoom':
                return <ZoomIcon />;
            case 'microsoft_teams':
                return <TeamsIcon />;
            case 'webex':
                return <WebexIcon />;
            case 'jitsi':
                return <JitsiIcon />;
            default:
                return <OtherIcon />;
        }
    };

    const getPlatformColor = (platformType: string) => {
        switch (platformType) {
            case 'google_meet':
                return 'success';
            case 'zoom':
                return 'primary';
            case 'microsoft_teams':
                return 'secondary';
            case 'webex':
                return 'warning';
            case 'jitsi':
                return 'info';
            default:
                return 'default';
        }
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="sm"
            fullWidth
            PaperProps={{
                sx: {
                    borderRadius: 3,
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                }
            }}
        >
            <DialogTitle sx={{ pb: 1, fontWeight: 'bold' }}>Add New Meeting</DialogTitle>
            <DialogContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
                    {error && <Alert severity="error">{error}</Alert>}

                    {/* Meeting URL */}
                    <TextField
                        label="Meeting URL"
                        placeholder="https://meet.google.com/abc-defg-hij"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        fullWidth
                        required
                        InputProps={{
                            endAdornment: detecting ? <CircularProgress size={20} /> : null,
                        }}
                    />

                    {/* Platform Detection Result */}
                    {platform && (
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2" color="text.secondary">
                                Detected:
                            </Typography>
                            <Chip
                                icon={getPlatformIcon(platform)}
                                label={platform.replace('_', ' ').toUpperCase()}
                                color={getPlatformColor(platform) as any}
                                size="small"
                            />
                            {meetingCode && (
                                <Typography variant="caption" color="text.secondary">
                                    Code: {meetingCode}
                                </Typography>
                            )}
                        </Box>
                    )}

                    {/* Title */}
                    <TextField
                        label="Meeting Title"
                        placeholder="Weekly Team Standup"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        fullWidth
                        required
                    />

                    {/* Scheduled Time */}
                    <LocalizationProvider dateAdapter={AdapterDateFns}>
                        <DateTimePicker
                            label="Scheduled Time (Optional)"
                            value={scheduledTime}
                            onChange={(newValue) => setScheduledTime(newValue)}
                            slotProps={{ textField: { fullWidth: true } }}
                        />
                    </LocalizationProvider>

                    {/* Duration */}
                    <TextField
                        label="Duration (minutes)"
                        type="number"
                        value={duration}
                        onChange={(e) => setDuration(parseInt(e.target.value) || 60)}
                        fullWidth
                        inputProps={{ min: 1, max: 480 }}
                    />

                    {/* Purpose */}
                    <TextField
                        label="Purpose (Optional)"
                        placeholder="Discuss Q1 goals and action items"
                        value={purpose}
                        onChange={(e) => setPurpose(e.target.value)}
                        fullWidth
                        multiline
                        rows={3}
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} disabled={submitting}>
                    Cancel
                </Button>
                <Button
                    onClick={handleSubmit}
                    variant="contained"
                    disabled={submitting || !url || !title || !platform}
                >
                    {submitting ? 'Saving...' : 'Add Meeting'}
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default MeetingForm;
