import { PrismaClient } from '../generated/prisma/index.js';

const globalForPrisma = globalThis as unknown as { 
  prisma: PrismaClient | undefined 
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient({
  log: process.env.NODE_ENV === 'development' ? ['query', 'error', 'warn'] : ['error'],
});

if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = prisma;
}

// Helper function to safely disconnect
export const disconnectPrisma = async () => {
  try {
    await prisma.$disconnect();
  } catch (error) {
    console.error('Error disconnecting Prisma:', error);
  }
};

export default prisma;
