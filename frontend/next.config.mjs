/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Required for Docker multi-stage build (copies only necessary files)
    output: 'standalone',
    transpilePackages: ["@mui/x-date-pickers", "@mui/material", "@mui/system", "@mui/icons-material", "@mui/utils"],
    async rewrites() {
        // BACKEND_URL is set in docker-compose.yml for Docker.
        // Falls back to localhost for normal "npm run dev" usage.
        const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
        return [
            {
                source: '/api/:path*',
                destination: `${backendUrl}/api/:path*`,
            },
        ];
    },
};

export default nextConfig;

