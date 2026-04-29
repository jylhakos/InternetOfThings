#!/usr/bin/env python3
"""
Test script for Open Source LLM Evaluation Tools (2025)
Verifies availability and basic functionality of evaluation frameworks
"""

import sys
import importlib
from typing import Dict, List, Any

def test_evaluation_tools():
    """Test availability of open-source LLM evaluation tools"""
    
    print("🛠️ TESTING OPEN SOURCE LLM EVALUATION TOOLS (2025)")
    print("="*65)
    
    tools_status = {}
    
    # Test core evaluation tools
    evaluation_tools = [
        {
            "name": "DeepEval",
            "module": "deepeval",
            "description": "Comprehensive LLM testing framework",
            "github": "https://github.com/confident-ai/deepeval",
            "install": "pip install deepeval",
            "required": False
        },
        {
            "name": "BERTScore", 
            "module": "bert_score",
            "description": "BERT-based semantic similarity evaluation",
            "github": "https://github.com/Tiiiger/bert_score",
            "install": "pip install bert-score",
            "required": True
        },
        {
            "name": "ROUGE",
            "module": "rouge_score",
            "description": "Traditional text similarity metrics",
            "github": "https://github.com/google-research/google-research/tree/master/rouge",
            "install": "pip install rouge-score",
            "required": True
        },
        {
            "name": "BLEU (SacreBLEU)",
            "module": "sacrebleu",
            "description": "BLEU score evaluation",
            "github": "https://github.com/mjpost/sacrebleu",
            "install": "pip install sacrebleu",
            "required": True
        },
        {
            "name": "Ragas",
            "module": "ragas",
            "description": "RAG application evaluation toolkit",
            "github": "https://github.com/explodinggradients/ragas",
            "install": "pip install ragas",
            "required": False
        },
        {
            "name": "LangSmith",
            "module": "langsmith",
            "description": "LangChain evaluation and monitoring",
            "github": "https://github.com/langchain-ai/langsmith-sdk",
            "install": "pip install langsmith",
            "required": False
        }
    ]
    
    print("📋 TOOL AVAILABILITY CHECK")
    print("-" * 50)
    
    available_tools = []
    missing_tools = []
    
    for tool in evaluation_tools:
        try:
            module = importlib.import_module(tool["module"])
            status = "✅ Available"
            tools_status[tool["name"]] = True
            available_tools.append(tool)
            
            # Get version if available
            version = ""
            if hasattr(module, "__version__"):
                version = f" (v{module.__version__})"
            
            print(f"{tool['name']:<15} {status}{version}")
            print(f"   📝 {tool['description']}")
            
        except ImportError:
            status = "❌ Not installed"
            tools_status[tool["name"]] = False
            missing_tools.append(tool)
            print(f"{tool['name']:<15} {status}")
            print(f"   📦 Install: {tool['install']}")
            print(f"   🔗 GitHub: {tool['github']}")
        
        print()
    
    # Summary
    print("📊 EVALUATION TOOLS SUMMARY")
    print("-" * 30)
    print(f"✅ Available: {len(available_tools)}")
    print(f"❌ Missing: {len(missing_tools)}")
    print(f"📈 Coverage: {len(available_tools)}/{len(evaluation_tools)} ({len(available_tools)/len(evaluation_tools)*100:.0f}%)")
    
    # Installation guide for missing tools
    if missing_tools:
        print(f"\n📦 INSTALLATION GUIDE FOR MISSING TOOLS")
        print("-" * 45)
        print("Run these commands to install missing evaluation tools:")
        print()
        
        for tool in missing_tools:
            print(f"# {tool['name']}")
            print(f"{tool['install']}")
            print()
    
    # Quick functionality test for available tools
    print("🧪 BASIC FUNCTIONALITY TESTS")
    print("-" * 35)
    
    if tools_status.get("BERTScore"):
        try:
            from bert_score import BERTScorer
            scorer = BERTScorer(lang="en", rescale_with_baseline=True)
            print("✅ BERTScore: Basic initialization successful")
        except Exception as e:
            print(f"⚠️ BERTScore: Initialization issue - {e}")
    
    if tools_status.get("ROUGE"):
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'])
            print("✅ ROUGE: Basic initialization successful")
        except Exception as e:
            print(f"⚠️ ROUGE: Initialization issue - {e}")
    
    if tools_status.get("BLEU (SacreBLEU)"):
        try:
            import sacrebleu
            print("✅ SacreBLEU: Import successful")
        except Exception as e:
            print(f"⚠️ SacreBLEU: Import issue - {e}")
    
    # Framework recommendations
    print(f"\n🎯 FRAMEWORK RECOMMENDATIONS")
    print("-" * 32)
    print("🏆 **Production Ready**: BERTScore, ROUGE, BLEU")
    print("🚀 **Advanced Features**: DeepEval (if installed)")
    print("🔧 **RAG Applications**: Ragas (for retrieval-augmented generation)")
    print("📊 **LangChain Integration**: LangSmith (for LangChain apps)")
    
    print(f"\n📚 DOCUMENTATION LINKS")
    print("-" * 25)
    for tool in evaluation_tools:
        print(f"📖 {tool['name']}: {tool['github']}")
    
    print(f"\n✨ NEXT STEPS")
    print("-" * 15)
    print("1. Install missing tools based on your needs")
    print("2. Run comprehensive evaluation: python src/bert_evaluation.py")
    print("3. Explore advanced metrics: python demo_evaluation.py") 
    print("4. Check G-Eval integration: python src/geval_integration.py")
    
    return tools_status

if __name__ == "__main__":
    print("Testing availability of modern LLM evaluation tools...")
    print()
    
    status = test_evaluation_tools()
    
    # Exit with appropriate code
    required_tools = ["BERTScore", "ROUGE", "BLEU (SacreBLEU)"]
    missing_required = [tool for tool in required_tools if not status.get(tool, False)]
    
    if missing_required:
        print(f"\n⚠️ Warning: Missing required tools: {', '.join(missing_required)}")
        print("Please install missing tools before running evaluations.")
        sys.exit(1)
    else:
        print(f"\n🎉 All required evaluation tools are available!")
        print("Your environment is ready for comprehensive LLM evaluation.")
        sys.exit(0)
