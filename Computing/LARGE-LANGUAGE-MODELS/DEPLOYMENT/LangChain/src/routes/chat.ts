import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { LLMChatService } from '../services/LLMChatService';
import { logger } from '../utils/logger';

export const chatRoutes = (llmService: LLMChatService): Router => {
  const router = Router();

  // Validation middleware
  const validateChatRequest = [
    body('message').notEmpty().withMessage('Message is required'),
    body('message').isLength({ max: 10000 }).withMessage('Message too long'),
  ];

  const validateChatCompletionRequest = [
    body('messages').isArray().withMessage('Messages must be an array'),
    body('messages').isLength({ min: 1 }).withMessage('At least one message is required'),
    body('model').optional().isString(),
    body('temperature').optional().isFloat({ min: 0, max: 2 }),
    body('max_tokens').optional().isInt({ min: 1, max: 8192 }),
  ];

  // Simple chat endpoint
  router.post('/message', validateChatRequest, async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: {
            message: 'Validation failed',
            type: 'validation_error',
            details: errors.array(),
          }
        });
      }

      const { message } = req.body;
      const userId = req.user?.id;

      const response = await llmService.generateChatCompletion({
        messages: [{ role: 'user', content: message }],
        userId,
      });

      res.json({
        message: response.choices[0].message.content,
        usage: response.usage,
        model: response.model,
      });
    } catch (error) {
      logger.error('Error in chat message:', error);
      res.status(500).json({
        error: {
          message: 'Failed to generate response',
          type: 'generation_error',
        }
      });
    }
  });

  // OpenAI-compatible chat completions
  router.post('/completions', validateChatCompletionRequest, async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: {
            message: 'Validation failed',
            type: 'validation_error',
            details: errors.array(),
          }
        });
      }

      const response = await llmService.generateChatCompletion({
        ...req.body,
        userId: req.user?.id,
      });

      res.json(response);
    } catch (error) {
      logger.error('Error in chat completions:', error);
      res.status(500).json({
        error: {
          message: 'Failed to generate completion',
          type: 'generation_error',
        }
      });
    }
  });

  // Get chat history
  router.get('/history', async (req: Request, res: Response) => {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return res.status(401).json({
          error: {
            message: 'User ID required',
            type: 'authentication_error',
          }
        });
      }

      const history = await llmService.getChatHistory(userId);
      res.json({ history });
    } catch (error) {
      logger.error('Error getting chat history:', error);
      res.status(500).json({
        error: {
          message: 'Failed to get chat history',
          type: 'retrieval_error',
        }
      });
    }
  });

  // Clear chat history
  router.delete('/history', async (req: Request, res: Response) => {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return res.status(401).json({
          error: {
            message: 'User ID required',
            type: 'authentication_error',
          }
        });
      }

      await llmService.clearChatHistory(userId);
      res.json({ message: 'Chat history cleared successfully' });
    } catch (error) {
      logger.error('Error clearing chat history:', error);
      res.status(500).json({
        error: {
          message: 'Failed to clear chat history',
          type: 'deletion_error',
        }
      });
    }
  });

  // Get model information
  router.get('/model', async (req: Request, res: Response) => {
    try {
      const modelInfo = llmService.getModelInfo();
      res.json(modelInfo);
    } catch (error) {
      logger.error('Error getting model info:', error);
      res.status(500).json({
        error: {
          message: 'Failed to get model information',
          type: 'retrieval_error',
        }
      });
    }
  });

  return router;
};
