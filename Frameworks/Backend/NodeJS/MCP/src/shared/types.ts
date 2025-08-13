/**
 * Shared types and interfaces for the MCP Node.js implementation
 */

export interface McpServerConfig {
  port: number;
  transport: 'stdio' | 'http' | 'streamable-http';
  ollamaUrl?: string;
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

export interface McpClientConfig {
  serverUrl: string;
  interactive: boolean;
  timeout?: number;
  retries?: number;
}

export interface LlamaConfig {
  model: string;
  ollamaUrl: string;
  temperature?: number;
  maxTokens?: number;
  context?: number;
}

export interface ToolDefinition {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
  handler: (input: any) => Promise<any>;
}

export interface ResourceDefinition {
  uri: string;
  name: string;
  description?: string;
  mimeType?: string;
  handler: () => Promise<string | Buffer>;
}

export interface PromptDefinition {
  name: string;
  description?: string;
  template: string;
  variables?: string[];
}

export interface McpError extends Error {
  code?: string;
  details?: any;
}

export interface OllamaResponse {
  model: string;
  created_at: string;
  response?: string;
  done: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  prompt_eval_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

export interface OllamaGenerateRequest {
  model: string;
  prompt: string;
  context?: number[];
  options?: {
    temperature?: number;
    top_k?: number;
    top_p?: number;
    num_ctx?: number;
    num_predict?: number;
  };
  stream?: boolean;
}

export interface SystemInfo {
  timestamp: string;
  platform: string;
  arch: string;
  nodeVersion: string;
  memory: {
    total: number;
    free: number;
    used: number;
  };
  uptime: number;
}

export interface WeatherData {
  location: string;
  temperature: number;
  description: string;
  humidity?: number;
  windSpeed?: number;
  timestamp: string;
}

export interface FileSystemInfo {
  path: string;
  type: 'file' | 'directory';
  size?: number;
  modified?: string;
  permissions?: string;
}
