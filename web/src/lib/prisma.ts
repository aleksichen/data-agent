import { PrismaClient } from '@prisma/client';

// PrismaClient 是一个重量级对象，不应该在每次请求中创建多个实例
// 使用 globalThis 确保在开发环境中的热重载不会创建多个实例

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;

export default prisma;
