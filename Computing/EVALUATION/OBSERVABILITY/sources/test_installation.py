"""
Installation Verification Script

This script checks if all required dependencies are properly installed
and configured for the AI agent observability project.
"""

import sys
import os


def check_python_version():
    """Check if Python version is 3.9 or higher."""
    print("\n" + "="*70)
    print("Checking Python Version")
    print("="*70)
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"Python version: {version_str}")
    
    if version.major >= 3 and version.minor >= 9:
        print("✓ Python version is compatible (3.9+)")
        return True
    else:
        print("✗ Python 3.9 or higher required")
        return False


def check_package(package_name: str, import_name: str = None) -> bool:
    """
    Check if a package is installed.
    
    Args:
        package_name: Display name of the package
        import_name: Name to use for import (defaults to package_name)
    
    Returns:
        True if package is installed, False otherwise
    """
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name}")
        return True
    except ImportError:
        print(f"✗ {package_name} - NOT INSTALLED")
        return False


def check_core_dependencies():
    """Check core observability packages."""
    print("\n" + "="*70)
    print("Checking Core Observability Packages")
    print("="*70)
    
    packages = [
        ("Langfuse", "langfuse"),
        ("Arize Phoenix", "phoenix"),
        ("OpenTelemetry API", "opentelemetry.api"),
        ("OpenTelemetry SDK", "opentelemetry.sdk"),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed


def check_llm_frameworks():
    """Check LLM framework packages."""
    print("\n" + "="*70)
    print("Checking LLM Framework Packages")
    print("="*70)
    
    packages = [
        ("LangChain", "langchain"),
        ("LangChain OpenAI", "langchain_openai"),
        ("LangChain Core", "langchain_core"),
        ("LangGraph", "langgraph"),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed


def check_ml_libraries():
    """Check ML framework packages."""
    print("\n" + "="*70)
    print("Checking ML Library Packages")
    print("="*70)
    
    packages = [
        ("PyTorch", "torch"),
        ("Transformers", "transformers"),
        ("Datasets", "datasets"),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed


def check_utility_packages():
    """Check utility packages."""
    print("\n" + "="*70)
    print("Checking Utility Packages")
    print("="*70)
    
    packages = [
        ("python-dotenv", "dotenv"),
        ("requests", "requests"),
        ("numpy", "numpy"),
    ]
    
    all_installed = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    return all_installed


def check_environment_variables():
    """Check if required environment variables are set."""
    print("\n" + "="*70)
    print("Checking Environment Variables")
    print("="*70)
    
    # Required variables
    required_vars = [
        "OPENAI_API_KEY",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]
    
    # Optional variables
    optional_vars = [
        "LANGFUSE_HOST",
        "ANTHROPIC_API_KEY",
        "HUGGINGFACE_API_KEY",
    ]
    
    all_set = True
    
    print("\nRequired:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"✓ {var} = {masked_value}")
        else:
            print(f"✗ {var} - NOT SET")
            all_set = False
    
    print("\nOptional:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"✓ {var} = {masked_value}")
        else:
            print(f"  {var} - not set")
    
    return all_set


def check_package_versions():
    """Check and display versions of key packages."""
    print("\n" + "="*70)
    print("Package Versions")
    print("="*70)
    
    packages_to_check = [
        "langfuse",
        "langchain",
        "langgraph",
        "torch",
        "transformers",
    ]
    
    for package_name in packages_to_check:
        try:
            package = __import__(package_name)
            version = getattr(package, "__version__", "unknown")
            print(f"{package_name}: {version}")
        except (ImportError, AttributeError):
            print(f"{package_name}: not installed")


def main():
    """Run all installation checks."""
    
    print("="*70)
    print("AI Agent Observability - Installation Verification")
    print("="*70)
    
    # Run all checks
    checks = [
        ("Python Version", check_python_version()),
        ("Core Observability", check_core_dependencies()),
        ("LLM Frameworks", check_llm_frameworks()),
        ("ML Libraries", check_ml_libraries()),
        ("Utility Packages", check_utility_packages()),
        ("Environment Variables", check_environment_variables()),
    ]
    
    # Display package versions
    check_package_versions()
    
    # Summary
    print("\n" + "="*70)
    print("Installation Summary")
    print("="*70)
    
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} | {check_name}")
    
    # Overall result
    all_passed = all(result for _, result in checks)
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
        print("="*70)
        print("\nYou're ready to run the observability examples!")
        print("\nNext steps:")
        print("  1. Run agent evaluation: python sources/agent_evaluation.py")
        print("  2. Run batch evaluation: python sources/run_evaluation.py")
        print("  3. View traces in Langfuse dashboard")
        return 0
    else:
        print("✗ SOME CHECKS FAILED")
        print("="*70)
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nAnd set missing environment variables in .env file")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
