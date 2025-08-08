import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for LLM responses
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Document API
export const documentAPI = {
  upload: async (file, metadata = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    if (Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    const response = await api.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (page = 1, pageSize = 20, category = null) => {
    const params = { page, page_size: pageSize };
    if (category) params.category = category;
    
    const response = await api.get('/api/v1/documents/', { params });
    return response.data;
  },

  delete: async (documentId) => {
    const response = await api.delete(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  get: async (documentId) => {
    const response = await api.get(`/api/v1/documents/${documentId}`);
    return response.data;
  },

  getChunks: async (documentId) => {
    const response = await api.get(`/api/v1/documents/${documentId}/chunks`);
    return response.data;
  },

  search: async (query, topK = 5, scoreThreshold = 0.7) => {
    const response = await api.post('/api/v1/documents/search', {
      query,
      top_k: topK,
      score_threshold: scoreThreshold,
    });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/api/v1/documents/stats/collection');
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  query: async (message, model = 'arcee-ai/arcee-agent', useRag = true, options = {}) => {
    const response = await api.post('/api/v1/chat/query', {
      message,
      model,
      use_rag: useRag,
      max_tokens: options.maxTokens || 500,
      temperature: options.temperature || 0.7,
      top_p: options.topP || 0.9,
      ...options,
    });
    return response.data;
  },

  ragQuery: async (query, model = 'arcee-ai/arcee-agent', topK = 5, scoreThreshold = 0.7) => {
    const response = await api.post('/api/v1/chat/rag', {
      query,
      top_k: topK,
      score_threshold: scoreThreshold,
    }, {
      params: { model }
    });
    return response.data;
  },

  stream: async (message, model = 'arcee-ai/arcee-agent', useRag = true, onMessage, onError, onComplete) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message,
          model,
          use_rag: useRag,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\\n');

        for (const line of lines) {
          if (line.trim() === '') continue;
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.error) {
                onError(data.error);
              } else if (data.content) {
                onMessage(data.content);
              }
              
              if (data.done) {
                onComplete();
                return;
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      onError(error.message);
    }
  },

  batchProcess: async (queries, model = 'arcee-ai/arcee-agent', useRag = true) => {
    const response = await api.post('/api/v1/chat/batch', {
      queries,
      model,
      use_rag: useRag,
    });
    return response.data;
  },

  getHistory: async (conversationId = null, limit = 50) => {
    const params = { limit };
    if (conversationId) params.conversation_id = conversationId;
    
    const response = await api.get('/api/v1/chat/history', { params });
    return response.data;
  },

  clearHistory: async (conversationId) => {
    const response = await api.delete(`/api/v1/chat/history/${conversationId}`);
    return response.data;
  },
};

// Models API
export const modelsAPI = {
  list: async () => {
    const response = await api.get('/api/v1/chat/models');
    return response.data;
  },

  switch: async (modelName) => {
    const response = await api.post('/api/v1/chat/models/switch', {
      model_name: modelName,
    });
    return response.data;
  },
};

// Health API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  chatHealth: async () => {
    const response = await api.get('/api/v1/chat/health');
    return response.data;
  },
};

export default api;
