/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    // Required for Docker multi-stage build (copies only necessary files)
    output: 'standalone',
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://localhost:8000/api/:path*',
            },
        ];
    },
};

export default nextConfig;

