import React from 'react';
import {
    Card,
    CardContent,
    CardActions,
    Typography,
    Button,
    Chip,
    Box,
    IconButton,
    Grid,
    Tooltip,
} from '@mui/material';
import {
    PlayArrow,
    Edit,
    Delete,
    VideoCall,
    Videocam,
    Groups,
    CameraAlt,
    Public,
    Link as LinkIcon,
} from '@mui/icons-material';
import { Meeting } from '../api/meetings';
import { format } from 'date-fns';

interface MeetingListProps {
    meetings: Meeting[];
    onJoin: (meeting: Meeting) => void;
    onEdit: (meeting: Meeting) => void;
    onDelete: (meeting: Meeting) => void;
}

const MeetingList: React.FC<MeetingListProps> = ({ meetings, onJoin, onEdit, onDelete }) => {
    const getPlatformIcon = (platform: string) => {
        switch (platform) {
            case 'google_meet':
                return <VideoCall />;
            case 'zoom':
                return <Videocam />;
            case 'microsoft_teams':
                return <Groups />;
            case 'webex':
                return <CameraAlt />;
            case 'jitsi':
                return <Public />;
            default:
                return <LinkIcon />;
        }
    };

    const getPlatformColor = (platform: string) => {
        switch (platform) {
            case 'google_meet':
                return '#4285f4';
            case 'zoom':
                return '#2d8cff';
            case 'microsoft_teams':
                return '#6264a7';
            case 'webex':
                return '#00bceb';
            case 'jitsi':
                return '#1d76ba';
            default:
                return '#666';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'scheduled':
                return 'info';
            case 'in_progress':
                return 'warning';
            case 'completed':
                return 'success';
            case 'cancelled':
                return 'default';
            case 'failed':
                return 'error';
            default:
                return 'default';
        }
    };

    const formatScheduledTime = (timeString: string | null) => {
        if (!timeString) return 'Not scheduled';
        try {
            return format(new Date(timeString), 'MMM dd, yyyy hh:mm a');
        } catch {
            return 'Invalid date';
        }
    };

    if (meetings.length === 0) {
        return (
            <Box sx={{ textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                    No meetings yet
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Click "Add Meeting" to get started
                </Typography>
            </Box>
        );
    }

    return (
        <Grid container spacing={3}>
            {meetings.map((meeting) => (
                <Grid size={{ xs: 12, md: 6, lg: 4 }} key={meeting.id}>
                    <Card
                        sx={{
                            height: '100%',
                            display: 'flex',
                            flexDirection: 'column',
                            borderLeft: `4px solid ${getPlatformColor(meeting.platform)}`,
                        }}
                    >
                        <CardContent sx={{ flexGrow: 1 }}>
                            {/* Platform and Status */}
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                <Chip
                                    icon={getPlatformIcon(meeting.platform)}
                                    label={meeting.platform.replace('_', ' ').toUpperCase()}
                                    size="small"
                                    sx={{ bgcolor: getPlatformColor(meeting.platform), color: 'white' }}
                                />
                                <Chip
                                    label={meeting.status.toUpperCase()}
                                    size="small"
                                    color={getStatusColor(meeting.status) as any}
                                />
                            </Box>

                            {/* Title */}
                            <Typography variant="h6" component="div" gutterBottom>
                                {meeting.title}
                            </Typography>

                            {/* Scheduled Time */}
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                📅 {formatScheduledTime(meeting.scheduled_time)}
                            </Typography>

                            {/* Duration */}
                            <Typography variant="body2" color="text.secondary" gutterBottom>
                                ⏱️ {meeting.duration_minutes} minutes
                            </Typography>

                            {/* Meeting Code */}
                            {meeting.meeting_code && (
                                <Typography variant="caption" color="text.secondary" display="block">
                                    Code: {meeting.meeting_code}
                                </Typography>
                            )}

                            {/* Purpose */}
                            {meeting.purpose && (
                                <Typography variant="body2" sx={{ mt: 1 }} color="text.secondary">
                                    {meeting.purpose.length > 100
                                        ? `${meeting.purpose.substring(0, 100)}...`
                                        : meeting.purpose}
                                </Typography>
                            )}
                        </CardContent>

                        <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                            <Box>
                                <Tooltip title="Edit meeting">
                                    <IconButton size="small" onClick={() => onEdit(meeting)}>
                                        <Edit fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                                <Tooltip title="Delete meeting">
                                    <IconButton size="small" color="error" onClick={() => onDelete(meeting)}>
                                        <Delete fontSize="small" />
                                    </IconButton>
                                </Tooltip>
                            </Box>
                            <Button
                                variant="contained"
                                size="small"
                                startIcon={<PlayArrow />}
                                onClick={() => onJoin(meeting)}
                                disabled={meeting.status === 'in_progress' || meeting.status === 'completed'}
                            >
                                Join Now
                            </Button>
                        </CardActions>
                    </Card>
                </Grid>
            ))}
        </Grid>
    );
};

export default MeetingList;
