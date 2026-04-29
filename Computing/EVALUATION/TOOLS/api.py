#!/usr/bin/env python3
"""
FastAPI backend for BERT Text Classification
Provides REST API endpoints for text classification using fine-tuned BERT model
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import torch
import logging
import os
import time
from datetime import datetime
from transformers import BertTokenizer, BertForSequenceClassification
import uvicorn
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BERT Text Classification API",
    description="REST API for sentiment analysis using fine-tuned BERT model",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class TextRequest(BaseModel):
    text: str = Field(..., description="Text to classify", min_length=1, max_length=512)
    return_confidence: bool = Field(False, description="Return confidence scores")

class BatchTextRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to classify", min_items=1, max_items=100)
    return_confidence: bool = Field(False, description="Return confidence scores")

class ClassificationResponse(BaseModel):
    text: str
    prediction: int = Field(..., description="0 for negative, 1 for positive")
    label: str = Field(..., description="Human-readable label")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    processing_time_ms: float

class BatchClassificationResponse(BaseModel):
    results: List[ClassificationResponse]
    total_texts: int
    total_processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str
    version: str

class ModelInfo(BaseModel):
    model_name: str
    model_path: str
    device: str
    tokenizer_vocab_size: int
    max_sequence_length: int

# Global model variables
model = None
tokenizer = None
device = None
model_info = {}

class BERTClassifier:
    def __init__(self, model_path: str = "bert-base-uncased"):
        """Initialize BERT classifier with model and tokenizer"""
        global device
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {device}")
        
        try:
            # Try to load fine-tuned model first
            if os.path.exists("./fine_tuned_bert"):
                self.model = BertForSequenceClassification.from_pretrained("./fine_tuned_bert")
                self.tokenizer = BertTokenizer.from_pretrained("./fine_tuned_bert")
                model_path = "./fine_tuned_bert"
                logger.info("Loaded fine-tuned BERT model")
            else:
                # Fall back to pre-trained model
                self.model = BertForSequenceClassification.from_pretrained(model_path, num_labels=2)
                self.tokenizer = BertTokenizer.from_pretrained(model_path)
                logger.info(f"Loaded pre-trained BERT model: {model_path}")
            
            self.model.to(device)
            self.model.eval()
            
            # Store model info
            global model_info
            model_info = {
                "model_name": model_path,
                "model_path": model_path,
                "device": str(device),
                "tokenizer_vocab_size": self.tokenizer.vocab_size,
                "max_sequence_length": 512
            }
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def classify_text(self, text: str, return_confidence: bool = False) -> Dict[str, Any]:
        """Classify single text"""
        start_time = time.time()
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            inputs = {key: val.to(device) for key, val in inputs.items()}
            
            # Get prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=-1)
                prediction = torch.argmax(logits, dim=-1).cpu().item()
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Prepare response
            result = {
                "text": text,
                "prediction": prediction,
                "label": "positive" if prediction == 1 else "negative",
                "processing_time_ms": round(processing_time, 2)
            }
            
            if return_confidence:
                confidence = probabilities.cpu().numpy()[0][prediction]
                result["confidence"] = round(float(confidence), 4)
            
            return result
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")
    
    def classify_batch(self, texts: List[str], return_confidence: bool = False) -> Dict[str, Any]:
        """Classify multiple texts"""
        start_time = time.time()
        results = []
        
        for text in texts:
            result = self.classify_text(text, return_confidence)
            results.append(result)
        
        total_time = (time.time() - start_time) * 1000
        
        return {
            "results": results,
            "total_texts": len(texts),
            "total_processing_time_ms": round(total_time, 2)
        }

# Initialize classifier
classifier = None

@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    global classifier
    try:
        logger.info("Initializing BERT classifier...")
        classifier = BERTClassifier()
        logger.info("BERT classifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "BERT Text Classification API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if classifier is not None else "unhealthy",
        model_loaded=classifier is not None,
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/model/info", response_model=ModelInfo)
async def get_model_info():
    """Get model information"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return ModelInfo(**model_info)

@app.post("/classify", response_model=ClassificationResponse)
async def classify_text(request: TextRequest):
    """Classify single text"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        result = classifier.classify_text(request.text, request.return_confidence)
        return ClassificationResponse(**result)
    except Exception as e:
        logger.error(f"Classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_batch(request: BatchTextRequest):
    """Classify multiple texts"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        result = classifier.classify_batch(request.texts, request.return_confidence)
        return BatchClassificationResponse(**result)
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/classify/demo")
async def demo_classification():
    """Demo endpoint with predefined examples"""
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    demo_texts = [
        "I absolutely love this product! It's amazing!",
        "This is terrible and completely useless.",
        "The quality is decent for the price.",
        "Worst purchase ever, would not recommend."
    ]
    
    results = []
    for text in demo_texts:
        result = classifier.classify_text(text, return_confidence=True)
        results.append(result)
    
    return {
        "demo_results": results,
        "note": "These are demo classifications using predefined texts"
    }

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
