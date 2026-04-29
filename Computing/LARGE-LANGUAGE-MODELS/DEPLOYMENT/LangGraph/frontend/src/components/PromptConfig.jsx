import React, { useState, useEffect } from 'react';
import { Settings, Save, RotateCcw, Brain, Code, AlertCircle } from 'lucide-react';
import { chatAPI } from '../services/api';

const PromptConfig = () => {
  const [selectedModel, setSelectedModel] = useState('arcee-ai/arcee-agent');
  const [prompts, setPrompts] = useState({
    system: '',
    rag_context: '',
    user_template: ''
  });
  const [settings, setSettings] = useState({
    temperature: 0.7,
    maxTokens: 500,
    topP: 0.9,
    topK: 40,
    repeatPenalty: 1.1
  });
  const [presets, setPresets] = useState([]);
  const [activePreset, setActivePreset] = useState('default');
  const [isSaving, setIsSaving] = useState(false);
  const [testQuery, setTestQuery] = useState('');
  const [testResponse, setTestResponse] = useState('');
  const [isTestingPrompt, setIsTestingPrompt] = useState(false);

  // Default prompts for different models
  const defaultPrompts = {
    'arcee-ai/arcee-agent': {
      system: `<|im_start|>system
You are Arcee Agent, a helpful AI assistant. You provide accurate, detailed, and thoughtful responses to user questions. When provided with context from documents, use that information to enhance your answers while being transparent about your sources.
<|im_end|>`,
      rag_context: `<|im_start|>system
Context from documents:
{context}

Use the above context to answer the user's question. If the context doesn't contain relevant information, say so clearly.
<|im_end|>`,
      user_template: `<|im_start|>user
{query}
<|im_end|>
<|im_start|>assistant`
    },
    'codellama:7b': {
      system: `# CodeLlama Assistant

You are a helpful coding assistant based on CodeLlama. You specialize in:
- Code explanation and analysis
- Programming problem solving
- Code optimization and best practices
- Debug assistance

When provided with context, use it to give more accurate and specific answers.`,
      rag_context: `# Relevant Code Context

{context}

---

Use the above context to help answer the user's coding question. Reference specific parts of the context when relevant.`,
      user_template: `{query}`
    },
    'codellama:13b': {
      system: `# CodeLlama 13B Assistant

You are an advanced coding assistant with deep knowledge of programming languages, frameworks, and software engineering practices. You excel at:
- Complex code analysis and architecture discussions
- Advanced debugging and optimization
- Code review and security analysis
- System design recommendations

When context is provided, integrate it thoughtfully into your responses.`,
      rag_context: `# Code Context and Documentation

{context}

---

Based on the provided context, answer the user's technical question with detailed explanations and code examples where appropriate.`,
      user_template: `Query: {query}

Please provide a comprehensive answer with code examples if applicable.`
    }
  };

  useEffect(() => {
    loadDefaultPrompts();
    loadPresets();
  }, [selectedModel]);

  const loadDefaultPrompts = () => {
    const modelDefaults = defaultPrompts[selectedModel] || defaultPrompts['arcee-ai/arcee-agent'];
    setPrompts(modelDefaults);
  };

  const loadPresets = () => {
    // In a real app, this would load from an API
    const modelPresets = [
      {
        id: 'default',
        name: 'Default',
        description: 'Standard configuration for general use'
      },
      {
        id: 'creative',
        name: 'Creative',
        description: 'Higher temperature for more creative responses',
        settings: { temperature: 1.2, topP: 0.95, repeatPenalty: 1.0 }
      },
      {
        id: 'precise',
        name: 'Precise',
        description: 'Lower temperature for more focused responses',
        settings: { temperature: 0.3, topP: 0.8, repeatPenalty: 1.2 }
      },
      {
        id: 'coding',
        name: 'Coding',
        description: 'Optimized for code generation and technical discussions',
        settings: { temperature: 0.1, topP: 0.9, maxTokens: 1000, repeatPenalty: 1.1 }
      }
    ];
    setPresets(modelPresets);
  };

  const applyPreset = (preset) => {
    setActivePreset(preset.id);
    if (preset.settings) {
      setSettings(prev => ({ ...prev, ...preset.settings }));
    }
    if (preset.prompts) {
      setPrompts(prev => ({ ...prev, ...preset.prompts }));
    }
  };

  const resetToDefaults = () => {
    loadDefaultPrompts();
    setSettings({
      temperature: 0.7,
      maxTokens: 500,
      topP: 0.9,
      topK: 40,
      repeatPenalty: 1.1
    });
    setActivePreset('default');
  };

  const saveConfiguration = async () => {
    setIsSaving(true);
    try {
      // In a real app, this would save to an API
      await new Promise(resolve => setTimeout(resolve, 1000));
      console.log('Configuration saved:', { prompts, settings, model: selectedModel });
      
      // Show success message
      const successMessage = document.createElement('div');
      successMessage.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
      successMessage.textContent = 'Configuration saved successfully!';
      document.body.appendChild(successMessage);
      setTimeout(() => successMessage.remove(), 3000);
    } catch (error) {
      console.error('Failed to save configuration:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const testPrompt = async () => {
    if (!testQuery.trim()) return;
    
    setIsTestingPrompt(true);
    setTestResponse('');
    
    try {
      const response = await chatAPI.query(
        testQuery,
        selectedModel,
        false, // Don't use RAG for testing
        settings
      );
      setTestResponse(response.response);
    } catch (error) {
      setTestResponse(`Error: ${error.message}`);
    } finally {
      setIsTestingPrompt(false);
    }
  };

  const getModelIcon = (modelName) => {
    if (modelName.includes('codellama')) {
      return <Code className="h-4 w-4" />;
    }
    return <Brain className="h-4 w-4" />;
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Settings className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Prompt Configuration</h1>
            <p className="text-gray-600">Customize prompts and parameters for different models</p>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={resetToDefaults}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center space-x-2"
          >
            <RotateCcw className="h-4 w-4" />
            <span>Reset</span>
          </button>
          <button
            onClick={saveConfiguration}
            disabled={isSaving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Save className="h-4 w-4" />
            <span>{isSaving ? 'Saving...' : 'Save'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Model & Prompts */}
        <div className="space-y-6">
          {/* Model Selection */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Model Selection</h2>
            <div className="space-y-3">
              {Object.keys(defaultPrompts).map((modelId) => (
                <div key={modelId} className="flex items-center space-x-3">
                  <input
                    type="radio"
                    id={modelId}
                    name="model"
                    value={modelId}
                    checked={selectedModel === modelId}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor={modelId} className="flex items-center space-x-2 cursor-pointer">
                    {getModelIcon(modelId)}
                    <span className="text-gray-900">{modelId}</span>
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Presets */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration Presets</h2>
            <div className="grid grid-cols-2 gap-2">
              {presets.map((preset) => (
                <button
                  key={preset.id}
                  onClick={() => applyPreset(preset)}
                  className={`p-3 text-left rounded-lg border ${
                    activePreset === preset.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <div className="font-medium text-sm">{preset.name}</div>
                  <div className="text-xs text-gray-600 mt-1">{preset.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Prompt Templates */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Prompt Templates</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  System Prompt
                </label>
                <textarea
                  value={prompts.system}
                  onChange={(e) => setPrompts(prev => ({ ...prev, system: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={6}
                  placeholder="Define the AI assistant's behavior and personality..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  RAG Context Template
                </label>
                <textarea
                  value={prompts.rag_context}
                  onChange={(e) => setPrompts(prev => ({ ...prev, rag_context: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  placeholder="Template for inserting document context. Use {context} placeholder..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use <code className="bg-gray-100 px-1 rounded">{"{context}"}</code> where document content should be inserted
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User Query Template
                </label>
                <textarea
                  value={prompts.user_template}
                  onChange={(e) => setPrompts(prev => ({ ...prev, user_template: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Template for user queries. Use {query} placeholder..."
                />
                <p className="text-xs text-gray-500 mt-1">
                  Use <code className="bg-gray-100 px-1 rounded">{"{query}"}</code> where user input should be inserted
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Parameters & Testing */}
        <div className="space-y-6">
          {/* Model Parameters */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Model Parameters</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
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
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>More focused</span>
                  <span>More creative</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="50"
                  max="4000"
                  value={settings.maxTokens}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    maxTokens: parseInt(e.target.value)
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Top-p (Nucleus Sampling): {settings.topP}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.05"
                  value={settings.topP}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    topP: parseFloat(e.target.value)
                  }))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Top-k: {settings.topK}
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={settings.topK}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    topK: parseInt(e.target.value)
                  }))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Repeat Penalty: {settings.repeatPenalty}
                </label>
                <input
                  type="range"
                  min="1"
                  max="2"
                  step="0.1"
                  value={settings.repeatPenalty}
                  onChange={(e) => setSettings(prev => ({
                    ...prev,
                    repeatPenalty: parseFloat(e.target.value)
                  }))}
                  className="w-full"
                />
              </div>
            </div>
          </div>

          {/* Prompt Testing */}
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Test Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Test Query
                </label>
                <textarea
                  value={testQuery}
                  onChange={(e) => setTestQuery(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Enter a test question to see how your configuration works..."
                />
              </div>

              <button
                onClick={testPrompt}
                disabled={!testQuery.trim() || isTestingPrompt}
                className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                {isTestingPrompt ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Testing...</span>
                  </>
                ) : (
                  <span>Test Prompt</span>
                )}
              </button>

              {testResponse && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Response
                  </label>
                  <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="whitespace-pre-wrap text-sm">{testResponse}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Tips */}
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start space-x-2">
              <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-sm font-medium text-amber-800 mb-2">Configuration Tips</h3>
                <ul className="text-sm text-amber-700 space-y-1">
                  <li>• Lower temperature (0.1-0.3) for factual, consistent responses</li>
                  <li>• Higher temperature (0.8-1.2) for creative, varied responses</li>
                  <li>• Adjust max tokens based on expected response length</li>
                  <li>• Test your prompts with various queries before saving</li>
                  <li>• Use model-specific formatting (ChatML for ArceeAgent)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptConfig;
