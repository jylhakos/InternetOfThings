import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Settings, Brain, Code } from 'lucide-react';
import { chatAPI } from '../services/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [model, setModel] = useState('arcee-ai/arcee-agent');
  const [useRag, setUseRag] = useState(true);
  const [settings, setSettings] = useState({
    temperature: 0.7,
    maxTokens: 500,
    topP: 0.9
  });
  const [showSettings, setShowSettings] = useState(false);
  
  const messagesEndRef = useRef(null);
  const currentStreamRef = useRef('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || isStreaming) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');

    // Create placeholder for bot response
    const botMessageId = Date.now() + 1;
    const botMessage = {
      id: botMessageId,
      type: 'bot',
      content: '',
      timestamp: new Date(),
      model: model,
      useRag: useRag,
      sources: [],
      processing: true
    };

    setMessages(prev => [...prev, botMessage]);

    try {
      if (useStreamingResponse()) {
        await handleStreamingResponse(inputMessage, botMessageId);
      } else {
        await handleRegularResponse(inputMessage, botMessageId);
      }
    } catch (error) {
      updateBotMessage(botMessageId, {
        content: `Error: ${error.message}`,
        processing: false,
        error: true
      });
    }
  };

  const useStreamingResponse = () => {
    // Use streaming for longer responses or when explicitly enabled
    return settings.maxTokens > 300;
  };

  const handleStreamingResponse = async (message, botMessageId) => {
    setIsStreaming(true);
    currentStreamRef.current = '';

    await chatAPI.stream(
      message,
      model,
      useRag,
      // onMessage
      (content) => {
        currentStreamRef.current += content;
        updateBotMessage(botMessageId, {
          content: currentStreamRef.current,
          processing: true
        });
      },
      // onError
      (error) => {
        updateBotMessage(botMessageId, {
          content: `Streaming error: ${error}`,
          processing: false,
          error: true
        });
        setIsStreaming(false);
      },
      // onComplete
      () => {
        updateBotMessage(botMessageId, {
          content: currentStreamRef.current,
          processing: false
        });
        setIsStreaming(false);
        currentStreamRef.current = '';
      }
    );
  };

  const handleRegularResponse = async (message, botMessageId) => {
    setIsLoading(true);

    try {
      const response = await chatAPI.query(
        message,
        model,
        useRag,
        {
          maxTokens: settings.maxTokens,
          temperature: settings.temperature,
          topP: settings.topP
        }
      );

      updateBotMessage(botMessageId, {
        content: response.response,
        processing: false,
        sources: response.sources || [],
        processingTime: response.processing_time,
        contextUsed: response.context_used
      });
    } finally {
      setIsLoading(false);
    }
  };

  const updateBotMessage = (messageId, updates) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId ? { ...msg, ...updates } : msg
    ));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getModelIcon = (modelName) => {
    if (modelName.includes('codellama')) {
      return <Code className="h-4 w-4" />;
    }
    return <Brain className="h-4 w-4" />;
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center space-x-3">
            <Bot className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                LangGraph RAG Assistant
              </h1>
              <p className="text-sm text-gray-500">
                Model: {model} {useRag ? '(with RAG)' : '(direct)'}
              </p>
            </div>
          </div>
          
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="max-w-4xl mx-auto mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Model
                </label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                >
                  <option value="arcee-ai/arcee-agent">ArceeAgent</option>
                  <option value="codellama:7b">CodeLlama 7B</option>
                  <option value="codellama:13b">CodeLlama 13B</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Use RAG
                </label>
                <div className="flex items-center space-x-3 mt-2">
                  <button
                    onClick={() => setUseRag(true)}
                    className={`px-3 py-1 rounded text-sm ${
                      useRag ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    On
                  </button>
                  <button
                    onClick={() => setUseRag(false)}
                    className={`px-3 py-1 rounded text-sm ${
                      !useRag ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
                    }`}
                  >
                    Off
                  </button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    temperature: parseFloat(e.target.value)
                  }))}
                  className="w-full"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="50"
                  max="2000"
                  value={settings.maxTokens}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    maxTokens: parseInt(e.target.value)
                  }))}
                  className="w-full px-3 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Bot className="h-16 w-16 text-gray-300 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-500 mb-2">
                Welcome to LangGraph RAG Assistant
              </h2>
              <p className="text-gray-400">
                Ask me anything about your uploaded documents or general questions.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl p-4 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.error
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-white border border-gray-200'
                }`}
              >
                <div className="flex items-start space-x-3">
                  {message.type === 'user' ? (
                    <User className="h-5 w-5 mt-1 flex-shrink-0" />
                  ) : (
                    <div className="flex-shrink-0 mt-1">
                      {getModelIcon(message.model)}
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm font-medium ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-900'
                      }`}>
                        {message.type === 'user' ? 'You' : message.model}
                      </span>
                      <span className={`text-xs ${
                        message.type === 'user' ? 'text-blue-200' : 'text-gray-500'
                      }`}>
                        {formatTimestamp(message.timestamp)}
                      </span>
                    </div>
                    
                    <div className={`prose prose-sm max-w-none ${
                      message.type === 'user' ? 'prose-invert' : ''
                    }`}>
                      {message.processing && (
                        <div className="flex items-center space-x-2 mb-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span className="text-sm text-gray-500">
                            {isStreaming ? 'Streaming...' : 'Thinking...'}
                          </span>
                        </div>
                      )}
                      
                      <div className="whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                    
                    {/* Message metadata */}
                    {message.type === 'bot' && !message.processing && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <div className="flex items-center space-x-4">
                            {message.contextUsed && (
                              <span className="text-green-600">✓ Used RAG</span>
                            )}
                            {message.sources && message.sources.length > 0 && (
                              <span>{message.sources.length} sources</span>
                            )}
                          </div>
                          {message.processingTime && (
                            <span>{message.processingTime.toFixed(2)}s</span>
                          )}
                        </div>
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-2">
                            <div className="text-xs font-medium text-gray-700 mb-1">
                              Sources:
                            </div>
                            <div className="flex flex-wrap gap-1">
                              {message.sources.map((source, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                                >
                                  {source}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={`Ask me anything${useRag ? ' about your documents' : ''}...`}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={1}
                disabled={isLoading || isStreaming}
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading || isStreaming}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading || isStreaming ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
