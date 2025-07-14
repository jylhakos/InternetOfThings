#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { LLMInferenceServerStack } from './llm-inference-stack';

const app = new cdk.App();

new LLMInferenceServerStack(app, 'LLMInferenceServerStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  description: 'LLM Inference Server with LangChain.js and Meta Llama-3.1',
});
