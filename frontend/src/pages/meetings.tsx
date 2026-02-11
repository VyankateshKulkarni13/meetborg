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
        <Container maxWidth="lg" sx={{ py: 4 }}>
            {/* Header */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Typography variant="h4" component="h1" fontWeight="bold">
                    📅 Meetings
                </Typography>
                <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => setFormOpen(true)}
                    size="large"
                >
                    Add Meeting
                </Button>
            </Box>

            {/* Status Filter Tabs */}
            <Paper sx={{ mb: 3 }}>
                <Tabs
                    value={statusFilter}
                    onChange={(_, newValue) => setStatusFilter(newValue)}
                    variant="scrollable"
                    scrollButtons="auto"
                >
                    <Tab label="All" value="all" />
                    <Tab label="Scheduled" value="scheduled" />
                    <Tab label="In Progress" value="in_progress" />
                    <Tab label="Completed" value="completed" />
                    <Tab label="Cancelled" value="cancelled" />
                </Tabs>
            </Paper>

            {/* Meeting List */}
            {loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                    <CircularProgress />
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
            >
                <Alert severity="success" onClose={() => setSuccessMessage(null)}>
                    {successMessage}
                </Alert>
            </Snackbar>

            {/* Error Snackbar */}
            <Snackbar
                open={!!errorMessage}
                autoHideDuration={6000}
                onClose={() => setErrorMessage(null)}
            >
                <Alert severity="error" onClose={() => setErrorMessage(null)}>
                    {errorMessage}
                </Alert>
            </Snackbar>
        </Container>
    );
};

export default Meetings;
