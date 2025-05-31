import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  eslint: {
    // Ignore ESLint errors during production build
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Ignore TypeScript errors during production build
    ignoreBuildErrors: true,
  },
  async rewrites() {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    return [
      {
        source: '/chat/:path*',
        destination: `${API_URL}/chat/:path*`,
      },
      {
        source: '/plan/:path*',
        destination: `${API_URL}/plan/:path*`,
      },
      {
        source: '/preview',
        destination: `${API_URL}/preview`,
      },
      {
        source: '/upload',
        destination: `${API_URL}/upload`,
      }
    ];
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
  }
};

export default nextConfig;
