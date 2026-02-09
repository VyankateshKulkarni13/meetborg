import DashboardLayout from '@/components/DashboardLayout';

export default function Dashboard() {
    return (
        <DashboardLayout currentPage="/dashboard">
            <div className="max-w-7xl">
                {/* Welcome Section */}
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl p-8 text-white mb-8">
                    <h2 className="text-3xl font-bold mb-2">Welcome to AI Meeting Bot</h2>
                    <p className="text-blue-50 text-lg">
                        Automate meeting attendance and never miss important discussions
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">🤖</span>
                            </div>
                            <span className="text-xs text-gray-500">This Month</span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900 mb-1">0</p>
                        <p className="text-sm text-gray-600">Active Missions</p>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">✓</span>
                            </div>
                            <span className="text-xs text-gray-500">Total</span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900 mb-1">0</p>
                        <p className="text-sm text-gray-600">Meetings Attended</p>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">🔐</span>
                            </div>
                            <span className="text-xs text-gray-500">Connected</span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900 mb-1">0</p>
                        <p className="text-sm text-gray-600">Platform Accounts</p>
                    </div>

                    <div className="bg-white rounded-lg border border-gray-200 p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                                <span className="text-2xl">⏱️</span>
                            </div>
                            <span className="text-xs text-gray-500">Saved</span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900 mb-1">0h</p>
                        <p className="text-sm text-gray-600">Time Automated</p>
                    </div>
                </div>

                {/* Getting Started */}
                <div className="bg-white rounded-lg border border-gray-200 p-8 mb-8">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">🚀 Getting Started</h3>
                    <div className="space-y-4">
                        <div className="flex items-start space-x-4">
                            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold flex-shrink-0">
                                1
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-900 mb-1">Add Platform Accounts</h4>
                                <p className="text-sm text-gray-600">Connect your Google Meet, Teams, and Zoom accounts to enable bot access.</p>
                                <a href="/platforms" className="inline-block mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                                    Configure Platforms →
                                </a>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4 opacity-50">
                            <div className="w-8 h-8 bg-gray-300 text-white rounded-full flex items-center justify-center font-semibold flex-shrink-0">
                                2
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-900 mb-1">Deploy Your First Bot</h4>
                                <p className="text-sm text-gray-600">Schedule a bot to attend an upcoming meeting automatically.</p>
                                <span className="inline-block mt-2 text-sm text-gray-500">Coming soon</span>
                            </div>
                        </div>

                        <div className="flex items-start space-x-4 opacity-50">
                            <div className="w-8 h-8 bg-gray-300 text-white rounded-full flex items-center justify-center font-semibold flex-shrink-0">
                                3
                            </div>
                            <div>
                                <h4 className="font-medium text-gray-900 mb-1">Monitor & Review</h4>
                                <p className="text-sm text-gray-600">Watch live feeds and review meeting transcripts with AI insights.</p>
                                <span className="inline-block mt-2 text-sm text-gray-500">Coming soon</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-lg border border-gray-200 p-8">
                    <h3 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h3>
                    <div className="text-center py-12">
                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                            <span className="text-4xl">📊</span>
                        </div>
                        <p className="text-gray-500">No activity yet. Start by adding platform accounts.</p>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
