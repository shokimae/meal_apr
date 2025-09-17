/** @type {import('next').NextConfig} */
const API_BASE = process.env.API_BASE || 'http://backend:8000';
const nextConfig = {
  async rewrites() {
    return [{ source: '/api/:path*', destination: `${API_BASE}/:path*` }];
  },
};
module.exports = nextConfig;
