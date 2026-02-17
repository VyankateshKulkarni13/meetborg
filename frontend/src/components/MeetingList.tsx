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
    alpha,
    useTheme,
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
    AccessTime,
    CalendarToday,
    Timer,
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
    const theme = useTheme();

    const getPlatformConfig = (platform: string) => {
        switch (platform) {
            case 'google_meet':
                return {
                    icon: <VideoCall fontSize="large" />,
                    color: '#00ac47', // Google Meet Green
                    bgColor: '#e6f4ea',
                    label: 'Google Meet',
                };
            case 'zoom':
                return {
                    icon: <Videocam fontSize="large" />,
                    color: '#2d8cff', // Zoom Blue
                    bgColor: '#ebf5ff',
                    label: 'Zoom',
                };
            case 'microsoft_teams':
                return {
                    icon: <Groups fontSize="large" />,
                    color: '#6264a7',
                    bgColor: '#f0f0f5',
                    label: 'Teams',
                };
            default:
                return {
                    icon: <LinkIcon fontSize="large" />,
                    color: theme.palette.grey[600],
                    bgColor: theme.palette.grey[100],
                    label: platform.replace('_', ' ').toUpperCase(),
                };
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'scheduled':
                return 'primary';
            case 'in_progress':
                return 'warning';
            case 'completed':
                return 'success';
            case 'cancelled':
                return 'default';
            default:
                return 'default';
        }
    };

    const formatScheduledTime = (timeString: string | null) => {
        if (!timeString) return 'Not scheduled';
        try {
            return format(new Date(timeString), 'MMM dd, yyyy • h:mm a');
        } catch {
            return 'Invalid date';
        }
    };

    if (meetings.length === 0) {
        return (
            <Box
                sx={{
                    textAlign: 'center',
                    py: 10,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    bgcolor: 'background.paper',
                    borderRadius: 4,
                    border: '1px dashed',
                    borderColor: 'divider',
                }}
            >
                <Box
                    sx={{
                        bgcolor: 'primary.lighter',
                        p: 3,
                        borderRadius: '50%',
                        mb: 3,
                        color: 'primary.main',
                        display: 'flex'
                    }}
                >
                    <CalendarToday sx={{ fontSize: 48 }} />
                </Box>
                <Typography variant="h5" fontWeight="bold" gutterBottom>
                    No meetings scheduled
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 500, mb: 4 }}>
                    Your schedule is clear! You can use this time to focus on deep work, or schedule a new meeting to collaborate with your team.
                </Typography>
            </Box>
        );
    }

    return (
        <Grid container spacing={3}>
            {meetings.map((meeting) => {
                const platformConfig = getPlatformConfig(meeting.platform);
                const isJoinable = meeting.status === 'scheduled' || meeting.status === 'in_progress';

                return (
                    <Grid size={{ xs: 12, md: 6, lg: 4 }} key={meeting.id}>
                        <Card
                            elevation={0}
                            sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                borderRadius: 3,
                                border: '1px solid',
                                borderColor: 'divider',
                                transition: 'transform 0.2s, box-shadow 0.2s',
                                '&:hover': {
                                    transform: 'translateY(-4px)',
                                    boxShadow: theme.shadows[4],
                                    borderColor: platformConfig.color,
                                },
                            }}
                        >
                            <Box
                                sx={{
                                    p: 2,
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    bgcolor: alpha(platformConfig.color, 0.08),
                                    borderBottom: '1px solid',
                                    borderColor: 'divider',
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Box sx={{ color: platformConfig.color, display: 'flex' }}>
                                        {platformConfig.icon}
                                    </Box>
                                    <Typography variant="subtitle1" fontWeight="bold" color="text.primary">
                                        {platformConfig.label}
                                    </Typography>
                                </Box>
                                <Chip
                                    label={meeting.status.replace('_', ' ').toUpperCase()}
                                    size="small"
                                    color={getStatusColor(meeting.status) as any}
                                    sx={{ fontWeight: 'bold', fontSize: '0.7rem' }}
                                />
                            </Box>

                            <CardContent sx={{ flexGrow: 1, p: 3 }}>
                                <Typography variant="h6" fontWeight="bold" gutterBottom sx={{ mb: 2, lineHeight: 1.3 }}>
                                    {meeting.title}
                                </Typography>

                                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, color: 'text.secondary' }}>
                                        <CalendarToday fontSize="small" color="action" />
                                        <Typography variant="body2" fontWeight="medium">
                                            {formatScheduledTime(meeting.scheduled_time)}
                                        </Typography>
                                    </Box>

                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, color: 'text.secondary' }}>
                                        <Timer fontSize="small" color="action" />
                                        <Typography variant="body2">
                                            {meeting.duration_minutes} min duration
                                        </Typography>
                                    </Box>

                                    {meeting.purpose && (
                                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                                            {meeting.purpose}
                                        </Typography>
                                    )}
                                </Box>
                            </CardContent>

                            <CardActions sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider', justifyContent: 'space-between' }}>
                                <Box>
                                    <Tooltip title="Edit details">
                                        <IconButton size="small" onClick={() => onEdit(meeting)} sx={{ color: 'text.secondary', '&:hover': { color: 'primary.main', bgcolor: 'primary.lighter' } }}>
                                            <Edit fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Delete meeting">
                                        <IconButton size="small" onClick={() => onDelete(meeting)} sx={{ color: 'text.secondary', '&:hover': { color: 'error.main', bgcolor: 'error.lighter' } }}>
                                            <Delete fontSize="small" />
                                        </IconButton>
                                    </Tooltip>
                                </Box>
                                <Button
                                    variant="contained"
                                    disableElevation
                                    startIcon={<PlayArrow />}
                                    onClick={() => onJoin(meeting)}
                                    // disabled={!isJoinable} // Allow joining anytime for demo purposes or manual override
                                    sx={{
                                        textTransform: 'none',
                                        fontWeight: 'bold',
                                        bgcolor: isJoinable ? platformConfig.color : 'action.disabledBackground',
                                        '&:hover': {
                                            bgcolor: isJoinable ? alpha(platformConfig.color, 0.9) : 'action.disabledBackground',
                                        },
                                    }}
                                >
                                    {meeting.status === 'in_progress' ? 'Re-Join' : 'Join Now'}
                                </Button>
                            </CardActions>
                        </Card>
                    </Grid>
                );
            })}
        </Grid>
    );
};

export default MeetingList;
