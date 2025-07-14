import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { v4 as uuidv4 } from 'uuid';

import { logger } from './utils/logger';
import { rateLimiter } from './middleware/rateLimiter';
import { authenticateToken } from './middleware/auth';
import { errorHandler } from './middleware/errorHandler';
import { LLMChatService } from './services/LLMChatService';
import { AuthService } from './services/AuthService';
import { chatRoutes } from './routes/chat';
import { authRoutes } from './routes/auth';
import { healthRoutes } from './routes/health';

// Load environment variables
dotenv.config();

class LLMInferenceServer {
  private app: express.Application;
  private server: any;
  private llmChatService: LLMChatService;
  private authService: AuthService;

  constructor() {
    this.app = express();
    this.llmChatService = new LLMChatService();
    this.authService = new AuthService();
    this.initializeMiddleware();
    this.initializeRoutes();
    this.initializeErrorHandling();
  }

  private initializeMiddleware(): void {
    // Security middleware
    this.app.use(helmet({
      contentSecurityPolicy: {
        directives: {
          defaultSrc: ["'self'"],
          styleSrc: ["'self'", "'unsafe-inline'"],
          scriptSrc: ["'self'"],
          imgSrc: ["'self'", "data:", "https:"],
        },
      },
    }));

    // CORS configuration
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:8080'],
      credentials: true,
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
    }));

    // Compression
    this.app.use(compression());

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Rate limiting
    this.app.use(rateLimiter);

    // Request logging
    this.app.use((req, res, next) => {
      const requestId = uuidv4();
      req.requestId = requestId;
      logger.info(`${req.method} ${req.path}`, {
        requestId,
        ip: req.ip,
        userAgent: req.get('User-Agent'),
      });
      next();
    });
  }

  private initializeRoutes(): void {
    // Health check routes (no auth required)
    this.app.use('/api/health', healthRoutes);

    // Authentication routes
    this.app.use('/api/auth', authRoutes(this.authService));

    // Protected chat routes
    this.app.use('/api/chat', authenticateToken, chatRoutes(this.llmChatService));

    // OpenAI compatible endpoints
    this.app.use('/v1', authenticateToken, this.createOpenAICompatibleRoutes());

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        message: 'LLM Inference Server with LangChain.js',
        version: '1.0.0',
        endpoints: {
          health: '/api/health',
          auth: '/api/auth',
          chat: '/api/chat',
          openai_compatible: '/v1'
        },
        documentation: '/api/docs'
      });
    });
  }

  private createOpenAICompatibleRoutes(): express.Router {
    const router = express.Router();

    // OpenAI-compatible chat completions endpoint
    router.post('/chat/completions', async (req, res) => {
      try {
        const { messages, model, temperature, max_tokens, stream = false } = req.body;

        if (!messages || !Array.isArray(messages)) {
          return res.status(400).json({
            error: {
              message: 'Invalid request: messages array is required',
              type: 'invalid_request_error',
            }
          });
        }

        const response = await this.llmChatService.generateChatCompletion({
          messages,
          model: model || process.env.LLM_MODEL_NAME,
          temperature: temperature || parseFloat(process.env.LLM_TEMPERATURE || '0.7'),
          maxTokens: max_tokens || parseInt(process.env.LLM_MAX_TOKENS || '4096'),
          stream,
          userId: req.user?.id,
        });

        res.json(response);
      } catch (error) {
        logger.error('Error in chat completions:', error);
        res.status(500).json({
          error: {
            message: 'Internal server error',
            type: 'internal_error',
          }
        });
      }
    });

    // Models endpoint
    router.get('/models', async (req, res) => {
      res.json({
        object: 'list',
        data: [
          {
            id: process.env.LLM_MODEL_NAME || 'meta-llama/Llama-3.1-8B-Instruct',
            object: 'model',
            created: Date.now(),
            owned_by: 'local',
            permission: [],
            root: process.env.LLM_MODEL_NAME || 'meta-llama/Llama-3.1-8B-Instruct',
            parent: null,
          }
        ]
      });
    });

    return router;
  }

  private initializeErrorHandling(): void {
    // 404 handler
    this.app.use('*', (req, res) => {
      res.status(404).json({
        error: {
          message: `Route ${req.originalUrl} not found`,
          type: 'not_found_error',
        }
      });
    });

    // Global error handler
    this.app.use(errorHandler);
  }

  public async start(): Promise<void> {
    try {
      // Initialize LLM service
      await this.llmChatService.initialize();
      
      const port = process.env.PORT || 3000;
      
      this.server = createServer(this.app);
      
      this.server.listen(port, () => {
        logger.info(`🚀 LLM Inference Server running on port ${port}`);
        logger.info(`📚 Model: ${process.env.LLM_MODEL_NAME}`);
        logger.info(`🔒 JWT Authentication enabled`);
        logger.info(`📊 Health check: http://localhost:${port}/api/health`);
        logger.info(`🤖 OpenAI compatible API: http://localhost:${port}/v1`);
      });

      // Graceful shutdown
      process.on('SIGINT', () => this.shutdown());
      process.on('SIGTERM', () => this.shutdown());

    } catch (error) {
      logger.error('Failed to start server:', error);
      process.exit(1);
    }
  }

  private async shutdown(): Promise<void> {
    logger.info('🔄 Shutting down server...');
    
    if (this.server) {
      this.server.close(() => {
        logger.info('✅ Server closed');
        process.exit(0);
      });
    }
  }
}

// Start the server
const server = new LLMInferenceServer();
server.start().catch((error) => {
  logger.error('Failed to start server:', error);
  process.exit(1);
});

export default LLMInferenceServer;
