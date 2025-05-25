import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: '/chat/:path*',
        destination: 'http://localhost:8000/chat/:path*',
      },
      {
        source: '/plan/:path*',
        destination: 'http://localhost:8000/plan/:path*',
      },
      {
        source: '/preview',
        destination: 'http://localhost:8000/preview',
      },
      {
        source: '/upload',
        destination: 'http://localhost:8000/upload',
      }
    ];
  }
};

export default nextConfig;
