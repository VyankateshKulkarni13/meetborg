import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import DashboardLayout from '@/components/DashboardLayout';

export default function PlatformsPage() {
    const router = useRouter();
    const [platforms, setPlatforms] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [selectedPlatform, setSelectedPlatform] = useState<'google_meet' | 'microsoft_teams' | 'zoom'>('microsoft_teams');
    const [formData, setFormData] = useState({ email: '', password: '' });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) router.push('/login');
        else fetchPlatforms();
    }, []);

    const fetchPlatforms = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/v1/platforms', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            const data = await response.json();
            setPlatforms(data.platforms || []);
        } catch (error) {
            console.error('Failed to fetch platforms:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async () => {
        if (!formData.email || !formData.password) {
            alert('Please fill in all fields');
            return;
        }

        setSubmitting(true);
        try {
            const res = await fetch('/api/v1/platforms', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                },
                body: JSON.stringify({
                    platform_type: selectedPlatform,
                    email: formData.email,
                    password: formData.password
                })
            });

            if (res.ok) {
                setShowModal(false);
                setFormData({ email: '', password: '' });
                fetchPlatforms();
                alert('Platform added successfully!');
            } else {
                const error = await res.json();
                alert(error.detail || 'Failed to add platform');
            }
        } catch (error) {
            alert('Failed to add platform');
        } finally {
            setSubmitting(false);
        }
    };

    const handleTest = async (id: string) => {
        try {
            const res = await fetch(`/api/v1/platforms/${id}/test`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (res.ok) {
                fetchPlatforms();
                alert('Connection test successful!');
            }
        } catch (error) {
            alert('Test failed');
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Remove this platform?')) return;
        try {
            const res = await fetch(`/api/v1/platforms/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (res.ok) fetchPlatforms();
        } catch (error) {
            alert('Delete failed');
        }
    };

    const platformNames = {
        google_meet: 'Google Meet',
        microsoft_teams: 'Microsoft Teams',
        zoom: 'Zoom'
    };

    return (
        <DashboardLayout currentPage="/platforms">
            <div className="max-w-7xl">
                <div className="mb-8 flex justify-between items-center">
                    <div>
                        <p className="text-sm text-gray-700 mb-1">Credentials Management</p>
                        <h2 className="text-2xl font-bold text-gray-900">Platform Accounts</h2>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                    >
                        + Add Account
                    </button>
                </div>

                <div className="grid grid-cols-3 gap-6 mb-8">
                    <div className="bg-white rounded-lg border p-6">
                        <p className="text-sm text-gray-700 mb-1">Total Accounts</p>
                        <p className="text-3xl font-bold text-gray-900">{platforms.length}</p>
                    </div>
                    <div className="bg-white rounded-lg border p-6">
                        <p className="text-sm text-gray-700 mb-1">Active</p>
                        <p className="text-3xl font-bold text-green-600">
                            {platforms.filter(p => p.status === 'active').length}
                        </p>
                    </div>
                    <div className="bg-white rounded-lg border p-6">
                        <p className="text-sm text-gray-700 mb-1">Need Attention</p>
                        <p className="text-3xl font-bold text-red-600">
                            {platforms.filter(p => p.status === 'inactive' || p.status === 'error').length}
                        </p>
                    </div>
                </div>

                {platforms.length === 0 && !loading ? (
                    <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No platform accounts</h3>
                        <p className="text-gray-500 mb-6">Add your first platform account to get started</p>
                        <button
                            onClick={() => setShowModal(true)}
                            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                        >
                            Add Your First Account
                        </button>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {platforms.map((platform) => (
                            <div key={platform.id} className="bg-white rounded-lg border p-6 hover:shadow-md transition-shadow">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-semibold text-gray-900 mb-1">{platformNames[platform.platform_type as keyof typeof platformNames]}</h3>
                                        <p className="text-sm text-gray-600 mb-3">{platform.email}</p>
                                        <div className="flex space-x-6 text-sm">
                                            <div>
                                                <span className="text-gray-700 font-medium">Status: </span>
                                                <span className={`inline-flex items-center px-2.5 py-1 rounded font-medium ${platform.status?.toLowerCase() === 'active' ? 'bg-green-100 text-green-700' :
                                                        platform.status?.toLowerCase() === 'error' ? 'bg-red-100 text-red-700' :
                                                            'bg-gray-100 text-gray-700'
                                                    }`}>
                                                    {platform.status?.toLowerCase() === 'active' ? '✓ Connected' :
                                                        platform.status?.toLowerCase() === 'error' ? '⚠ Error' :
                                                            '○ Disconnected'}
                                                </span>
                                                {platform.status === 'error' && platform.error_message && (
                                                    <div className="mt-1 text-xs text-red-600 max-w-xs break-words">
                                                        {platform.error_message}
                                                    </div>
                                                )}
                                            </div>
                                            {platform.last_tested_at && (
                                                <div>
                                                    <span className="text-gray-700 font-medium">Last tested: </span>
                                                    <span className="text-gray-900">{new Date(platform.last_tested_at).toLocaleString()}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => handleTest(platform.id)}
                                            className="px-4 py-2 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-blue-600 hover:border-blue-300 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                            </svg>
                                            <span>Test</span>
                                        </button>
                                        <button
                                            onClick={() => handleDelete(platform.id)}
                                            className="px-4 py-2 bg-white border border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1"
                                        >
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                            </svg>
                                            <span>Remove</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {showModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
                        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
                            <div className="px-6 py-4 border-b flex justify-between items-center">
                                <h3 className="text-xl font-semibold text-gray-900">Add Platform Account</h3>
                                <button onClick={() => setShowModal(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="p-6 space-y-6 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 140px)' }}>
                                {/* Platform Selection Cards */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-3">Select Platform</label>
                                    <div className="grid grid-cols-3 gap-4">
                                        {/* Google Meet */}
                                        <button
                                            onClick={() => setSelectedPlatform('google_meet')}
                                            className={`p-4 rounded-lg border-2 transition-all ${selectedPlatform === 'google_meet'
                                                ? 'border-blue-500 bg-blue-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="text-3xl mb-2">📹</div>
                                            <p className={`text-sm font-medium ${selectedPlatform === 'google_meet' ? 'text-blue-700' : 'text-gray-700'
                                                }`}>
                                                Google Meet
                                            </p>
                                        </button>

                                        {/* Microsoft Teams */}
                                        <button
                                            onClick={() => setSelectedPlatform('microsoft_teams')}
                                            className={`p-4 rounded-lg border-2 transition-all ${selectedPlatform === 'microsoft_teams'
                                                ? 'border-purple-500 bg-purple-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="text-3xl mb-2">👥</div>
                                            <p className={`text-sm font-medium ${selectedPlatform === 'microsoft_teams' ? 'text-purple-700' : 'text-gray-700'
                                                }`}>
                                                Microsoft Teams
                                            </p>
                                        </button>

                                        {/* Zoom */}
                                        <button
                                            onClick={() => setSelectedPlatform('zoom')}
                                            className={`p-4 rounded-lg border-2 transition-all ${selectedPlatform === 'zoom'
                                                ? 'border-indigo-500 bg-indigo-50'
                                                : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                        >
                                            <div className="text-3xl mb-2">🎥</div>
                                            <p className={`text-sm font-medium ${selectedPlatform === 'zoom' ? 'text-indigo-700' : 'text-gray-700'
                                                }`}>
                                                Zoom
                                            </p>
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Email / Username</label>
                                    <input
                                        type="text"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        placeholder="bot@company.com"
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-400"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                                    <input
                                        type="password"
                                        value={formData.password}
                                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                        placeholder="Enter password"
                                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white placeholder-gray-400"
                                    />
                                </div>

                                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                    <div className="flex space-x-3">
                                        <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                        </svg>
                                        <div className="flex-1">
                                            <h4 className="text-sm font-medium text-blue-900 mb-1">Secure Credential Storage</h4>
                                            <p className="text-sm text-blue-700">
                                                Your credentials are encrypted using AES-256 and stored securely. We use browser automation to maintain active sessions without storing passwords in plain text.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="px-6 py-4 bg-gray-50 border-t flex justify-end space-x-3">
                                <button
                                    onClick={() => setShowModal(false)}
                                    className="px-5 py-2.5 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg font-medium transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={submitting}
                                    className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 flex items-center space-x-2"
                                >
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                    </svg>
                                    <span>{submitting ? 'Adding...' : 'Add & Verify Account'}</span>
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
