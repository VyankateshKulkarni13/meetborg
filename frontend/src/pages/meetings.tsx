import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Button,
    Box,
    Paper,
    Tabs,
    Tab,
    Alert,
    Snackbar,
    CircularProgress,
    Grid,
    Chip,
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import MeetingForm from '../components/MeetingForm';
import MeetingList from '../components/MeetingList';
import { meetingsAPI, Meeting } from '../api/meetings';

const Meetings: React.FC = () => {
    const [meetings, setMeetings] = useState<Meeting[]>([]);
    const [loading, setLoading] = useState(true);
    const [formOpen, setFormOpen] = useState(false);
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [successMessage, setSuccessMessage] = useState<string | null>(null);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    // Load meetings
    const loadMeetings = async (status?: string) => {
        setLoading(true);
        try {
            const response = await meetingsAPI.list({
                status_filter: status !== 'all' ? status : undefined,
            });
            setMeetings(response.meetings);
        } catch (error: any) {
            console.error('Error loading meetings:', error);
            setErrorMessage('Failed to load meetings');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMeetings(statusFilter);
    }, [statusFilter]);

    const handleFormSuccess = () => {
        setSuccessMessage('Meeting added successfully!');
        loadMeetings(statusFilter);
    };

    const handleJoin = async (meeting: Meeting) => {
        try {
            // Trigger backend automation (opens in separate browser with full automation)
            await meetingsAPI.triggerJoin(meeting.id);
            setSuccessMessage(`Joining "${meeting.title}"...`);
            loadMeetings(statusFilter);
        } catch (error: any) {
            setErrorMessage(error.response?.data?.detail || 'Failed to trigger join');
        }
    };

    const handleEdit = (meeting: Meeting) => {
        // TODO: Implement edit functionality
        console.log('Edit:', meeting);
        setSuccessMessage('Edit functionality coming soon!');
    };

    const handleDelete = async (meeting: Meeting) => {
        if (!confirm(`Are you sure you want to delete "${meeting.title}"?`)) {
            return;
        }

        try {
            await meetingsAPI.delete(meeting.id);
            setSuccessMessage('Meeting deleted successfully');
            loadMeetings(statusFilter);
        } catch (error: any) {
            setErrorMessage(error.response?.data?.detail || 'Failed to delete meeting');
        }
    };

    return (
        <Box sx={{ minHeight: '100vh', bgcolor: 'grey.50', py: 4 }}>
            <Container maxWidth="xl">
                {/* Header */}
                {/* Enhanced Header Section */}
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        mb: 5,
                        position: 'relative',
                        zIndex: 1
                    }}
                >
                    <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                            <Box
                                sx={{
                                    width: 48,
                                    height: 48,
                                    borderRadius: 3,
                                    background: 'linear-gradient(135deg, #FF6B6B 0%, #556270 100%)', // Modern coral-blue gradient
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    boxShadow: '0 8px 16px -4px rgba(255, 107, 107, 0.4)',
                                    color: 'white'
                                }}
                            >
                                <Typography variant="h4" component="span">📅</Typography>
                            </Box>
                            <Typography variant="h4" component="h1" fontWeight="800" sx={{ color: 'text.primary', letterSpacing: '-0.02em' }}>
                                Meetings
                            </Typography>
                            <Chip
                                label="Beta"
                                size="small"
                                color="primary"
                                variant="outlined"
                                sx={{ fontWeight: 'bold', borderRadius: 1, height: 20, fontSize: '0.65rem' }}
                            />
                        </Box>
                        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, ml: 8 }}>
                            Manage your video conferences, track attendance, and automate joining.
                        </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 2 }}>
                        <Button
                            variant="contained"
                            startIcon={<AddIcon />}
                            onClick={() => setFormOpen(true)}
                            size="large"
                            disableElevation
                            sx={{
                                borderRadius: 3,
                                px: 4,
                                py: 1.5,
                                textTransform: 'none',
                                fontWeight: 'bold',
                                fontSize: '1rem',
                                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                                boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
                                '&:hover': {
                                    background: 'linear-gradient(45deg, #1976D2 30%, #00BCD4 90%)',
                                    transform: 'translateY(-2px)',
                                    boxShadow: '0 6px 10px 4px rgba(33, 203, 243, .3)',
                                },
                                transition: 'all 0.3s ease'
                            }}
                        >
                            New Meeting
                        </Button>
                    </Box>
                </Box>

                {/* Dashboard Summary */}
                <Grid container spacing={3} sx={{ mb: 5 }}>
                    <Grid item xs={12} md={8}>
                        <Paper
                            elevation={0}
                            sx={{
                                p: 4,
                                height: '100%',
                                background: 'linear-gradient(135deg, #1a2980 0%, #26d0ce 100%)',
                                color: 'white',
                                borderRadius: 4,
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'center',
                                position: 'relative',
                                overflow: 'hidden',
                                boxShadow: '0 10px 40px -10px rgba(0,0,0,0.3)',
                            }}
                        >
                            <Box sx={{ position: 'relative', zIndex: 1 }}>
                                <Typography variant="h4" fontWeight="800" gutterBottom sx={{ textShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>
                                    Welcome back! 👋
                                </Typography>
                                <Typography variant="h6" sx={{ opacity: 0.95, fontWeight: 'normal', maxWidth: '85%', lineHeight: 1.5 }}>
                                    You have <Box component="span" sx={{ fontWeight: 'bold', borderBottom: '2px solid white' }}>{meetings.filter(m => m.status === 'scheduled').length} upcoming meetings</Box> scheduled.
                                </Typography>
                                <Button
                                    variant="contained"
                                    sx={{
                                        mt: 3,
                                        bgcolor: 'rgba(255,255,255,0.2)',
                                        backdropFilter: 'blur(10px)',
                                        color: 'white',
                                        boxShadow: 'none',
                                        border: '1px solid rgba(255,255,255,0.3)',
                                        fontWeight: 'bold',
                                        px: 3,
                                        '&:hover': {
                                            bgcolor: 'rgba(255,255,255,0.35)',
                                            transform: 'translateY(-2px)',
                                        },
                                        transition: 'all 0.2s',
                                    }}
                                    onClick={() => setFormOpen(true)}
                                >
                                    Schedule New Meeting
                                </Button>
                            </Box>
                            {/* Decorative Circle */}
                            <Box
                                sx={{
                                    position: 'absolute',
                                    right: -60,
                                    top: -60,
                                    width: 320,
                                    height: 320,
                                    borderRadius: '50%',
                                    bgcolor: 'rgba(255,255,255,0.1)',
                                    backdropFilter: 'blur(5px)',
                                }}
                            />
                            <Box
                                sx={{
                                    position: 'absolute',
                                    bottom: -40,
                                    left: -40,
                                    width: 200,
                                    height: 200,
                                    borderRadius: '50%',
                                    bgcolor: 'rgba(255,255,255,0.05)',
                                }}
                            />
                        </Paper>
                    </Grid>
                    <Grid item xs={12} md={4}>
                        <Paper
                            elevation={0}
                            sx={{
                                p: 3,
                                height: '100%',
                                borderRadius: 4,
                                border: '1px solid',
                                borderColor: 'divider',
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'space-between',
                                bgcolor: 'background.paper',
                            }}
                        >
                            <Box>
                                <Typography variant="subtitle1" fontWeight="bold" color="text.secondary" gutterBottom sx={{ textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: 1 }}>
                                    Quick Stats
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                                    <Box sx={{ flex: 1 }}>
                                        <Typography variant="h3" fontWeight="800" color="primary.main" sx={{ lineHeight: 1 }}>
                                            {meetings.length}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ mt: 0.5, display: 'block' }}>
                                            TOTAL MEETINGS
                                        </Typography>
                                    </Box>
                                    <Box sx={{ width: 1, bgcolor: 'divider', my: 1 }} />
                                    <Box sx={{ flex: 1, pl: 2 }}>
                                        <Typography variant="h3" fontWeight="800" color="success.main" sx={{ lineHeight: 1 }}>
                                            {meetings.filter(m => m.status === 'completed').length}
                                        </Typography>
                                        <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ mt: 0.5, display: 'block' }}>
                                            COMPLETED
                                        </Typography>
                                    </Box>
                                </Box>
                            </Box>
                            <Box sx={{ mt: 4, p: 2, bgcolor: 'grey.50', borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                                    <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'warning.main' }} />
                                    <Typography variant="caption" color="text.secondary" fontWeight="bold" sx={{ textTransform: 'uppercase' }}>
                                        Up Next
                                    </Typography>
                                </Box>
                                <Typography variant="subtitle2" fontWeight="bold" noWrap sx={{ fontSize: '0.95rem' }}>
                                    {meetings.find(m => m.status === 'scheduled')?.title || "No meetings scheduled"}
                                </Typography>
                                {meetings.find(m => m.status === 'scheduled') && (
                                    <Typography variant="caption" color="text.secondary" display="block">
                                        {new Date(meetings.find(m => m.status === 'scheduled')?.scheduled_time!).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </Typography>
                                )}
                            </Box>
                        </Paper>
                    </Grid>
                </Grid>

                {/* Status Filter Tabs */}
                <Paper
                    elevation={0}
                    sx={{
                        mb: 4,
                        bgcolor: 'background.paper',
                        borderRadius: 3,
                        border: '1px solid',
                        borderColor: 'divider',
                        overflow: 'hidden'
                    }}
                >
                    <Tabs
                        value={statusFilter}
                        onChange={(_, newValue) => setStatusFilter(newValue)}
                        variant="scrollable"
                        scrollButtons="auto"
                        sx={{
                            '& .MuiTab-root': {
                                textTransform: 'none',
                                fontWeight: 'bold',
                                minHeight: 64,
                                fontSize: '0.95rem',
                            },
                        }}
                    >
                        <Tab label="All Meetings" value="all" />
                        <Tab label="Scheduled" value="scheduled" />
                        <Tab label="In Progress" value="in_progress" />
                        <Tab label="Completed" value="completed" />
                        <Tab label="Cancelled" value="cancelled" />
                    </Tabs>
                </Paper>

                {/* Meeting List */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
                        <CircularProgress size={60} thickness={4} />
                    </Box>
                ) : (
                    <MeetingList
                        meetings={meetings}
                        onJoin={handleJoin}
                        onEdit={handleEdit}
                        onDelete={handleDelete}
                    />
                )}

                {/* Meeting Form Dialog */}
                <MeetingForm
                    open={formOpen}
                    onClose={() => setFormOpen(false)}
                    onSuccess={handleFormSuccess}
                />

                {/* Success Snackbar */}
                <Snackbar
                    open={!!successMessage}
                    autoHideDuration={4000}
                    onClose={() => setSuccessMessage(null)}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    <Alert
                        severity="success"
                        onClose={() => setSuccessMessage(null)}
                        variant="filled"
                        sx={{ width: '100%', borderRadius: 2 }}
                    >
                        {successMessage}
                    </Alert>
                </Snackbar>

                {/* Error Snackbar */}
                <Snackbar
                    open={!!errorMessage}
                    autoHideDuration={6000}
                    onClose={() => setErrorMessage(null)}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    <Alert
                        severity="error"
                        onClose={() => setErrorMessage(null)}
                        variant="filled"
                        sx={{ width: '100%', borderRadius: 2 }}
                    >
                        {errorMessage}
                    </Alert>
                </Snackbar>
            </Container>
        </Box>
    );
};

export default Meetings;
