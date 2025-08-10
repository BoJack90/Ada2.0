/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    console.log('[Next.js] Setting up API proxy to host.docker.internal:8090')
    return [
      {
        source: '/api/:path*',
        destination: 'http://host.docker.internal:8090/api/:path*',
      },
    ]
  },
};

module.exports = nextConfig;
