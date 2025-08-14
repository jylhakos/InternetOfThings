/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  serverExternalPackages: ['@prisma/client'],
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3000/api/:path*',
      },
    ];
  },
  webpack: (config, { dev, isServer }) => {
    // Add support for ESM
    config.experiments = { ...config.experiments, topLevelAwait: true };
    
    if (!dev && isServer) {
      // Optimize for production builds
      config.cache = false;
    }
    
    return config;
  },
};

export default nextConfig;
