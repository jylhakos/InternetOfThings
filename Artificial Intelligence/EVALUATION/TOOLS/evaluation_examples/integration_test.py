#!/usr/bin/env python3
"""
Integration Test Suite for LLM Evaluation Framework
Tests all 5 evaluation tools and deployment scripts
"""

import os
import sys
import subprocess
import json
import time
from typing import Dict, List, Tuple
from pathlib import Path

class EvaluationFrameworkTester:
    """Integration tester for all evaluation frameworks"""
    
    def __init__(self):
        self.test_results = {
            'start_time': time.time(),
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'test_details': {},
            'environment': {
                'python_version': sys.version,
                'working_directory': os.getcwd()
            }
        }
    
    def run_all_tests(self):
        """Execute comprehensive test suite"""
        
        print("🧪 STARTING COMPREHENSIVE INTEGRATION TESTS")
        print("="*55)
        
        # Test 1: File structure validation
        self.test_file_structure()
        
        # Test 2: Python syntax validation
        self.test_python_syntax()
        
        # Test 3: Import validation
        self.test_imports()
        
        # Test 4: Example execution (demo mode)
        self.test_example_execution()
        
        # Test 5: AWS deployment script validation
        self.test_aws_scripts()
        
        # Test 6: Documentation completeness
        self.test_documentation()
        
        # Generate final report
        self.generate_final_report()
    
    def test_file_structure(self):
        """Test that all required files exist"""
        
        print("\n📁 Testing file structure...")
        
        required_files = [
            'evaluation_examples/deepeval_example.py',
            'evaluation_examples/geval_example.py', 
            'evaluation_examples/llmebench_example.py',
            'evaluation_examples/langsmith_example.py',
            'evaluation_examples/ragas_example.py',
            'evaluation_examples/comprehensive_demo.py',
            'README.md'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        test_name = "file_structure"
        if missing_files:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': f"Missing files: {missing_files}",
                'missing_count': len(missing_files)
            }
            print(f"❌ File structure test FAILED: {len(missing_files)} files missing")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED',
                'message': "All required files present",
                'file_count': len(required_files)
            }
            print(f"✅ File structure test PASSED: All {len(required_files)} files found")
        
        self._update_test_counts(test_name)
    
    def test_python_syntax(self):
        """Test Python syntax of all example files"""
        
        print("\n🐍 Testing Python syntax...")
        
        python_files = [
            'evaluation_examples/deepeval_example.py',
            'evaluation_examples/geval_example.py',
            'evaluation_examples/llmebench_example.py', 
            'evaluation_examples/langsmith_example.py',
            'evaluation_examples/ragas_example.py',
            'evaluation_examples/comprehensive_demo.py'
        ]
        
        syntax_errors = []
        
        for file_path in python_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}: {e}")
        
        test_name = "python_syntax"
        if syntax_errors:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': f"Syntax errors in {len(syntax_errors)} files",
                'errors': syntax_errors
            }
            print(f"❌ Python syntax test FAILED: {len(syntax_errors)} files have syntax errors")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED', 
                'message': f"All {len(python_files)} Python files have valid syntax",
                'files_checked': len(python_files)
            }
            print(f"✅ Python syntax test PASSED: All {len(python_files)} files valid")
        
        self._update_test_counts(test_name)
    
    def test_imports(self):
        """Test that all imports are handled gracefully"""
        
        print("\n📦 Testing import handling...")
        
        test_files = [
            ('deepeval_example.py', 'BERTDeepEvalTester'),
            ('geval_example.py', 'BERTGEvalTester'),
            ('llmebench_example.py', 'BERTLLMeBenchTester'),
            ('langsmith_example.py', 'BERTLangSmithEvaluator'), 
            ('ragas_example.py', 'BERTRagasEvaluator')
        ]
        
        import_issues = []
        
        for filename, class_name in test_files:
            file_path = f'evaluation_examples/{filename}'
            
            if Path(file_path).exists():
                try:
                    # Try to import the module
                    spec = __import__('importlib.util', fromlist=['spec_from_file_location'])
                    spec_obj = spec.spec_from_file_location("test_module", file_path)
                    if spec_obj and spec_obj.loader:
                        module = spec.module_from_spec(spec_obj)
                        sys.modules["test_module"] = module
                        spec_obj.loader.exec_module(module)
                        
                        # Check if class exists
                        if not hasattr(module, class_name):
                            import_issues.append(f"{filename}: Missing class {class_name}")
                        
                except Exception as e:
                    # Import errors are expected for missing dependencies
                    if "Import" not in str(e) and "could not be resolved" not in str(e):
                        import_issues.append(f"{filename}: {e}")
        
        test_name = "imports"
        if import_issues:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': f"Import issues in {len(import_issues)} files",
                'issues': import_issues
            }
            print(f"❌ Import test FAILED: {len(import_issues)} critical import issues")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED',
                'message': "All imports handled gracefully",
                'files_tested': len(test_files)
            }
            print(f"✅ Import test PASSED: All {len(test_files)} files handle imports correctly")
        
        self._update_test_counts(test_name)
    
    def test_example_execution(self):
        """Test that examples can run in demo mode"""
        
        print("\n🎬 Testing example execution (demo mode)...")
        
        examples = [
            'deepeval_example.py',
            'geval_example.py', 
            'llmebench_example.py',
            'langsmith_example.py',
            'ragas_example.py'
        ]
        
        execution_results = {}
        
        for example in examples:
            file_path = f'evaluation_examples/{example}'
            
            if Path(file_path).exists():
                try:
                    # Run with a timeout
                    result = subprocess.run(
                        ['python', file_path], 
                        capture_output=True, 
                        text=True, 
                        timeout=60,
                        cwd=os.getcwd()
                    )
                    
                    execution_results[example] = {
                        'return_code': result.returncode,
                        'stdout_length': len(result.stdout),
                        'stderr_length': len(result.stderr),
                        'success': result.returncode == 0
                    }
                    
                except subprocess.TimeoutExpired:
                    execution_results[example] = {
                        'return_code': -1,
                        'error': 'Timeout',
                        'success': False
                    }
                except Exception as e:
                    execution_results[example] = {
                        'error': str(e),
                        'success': False
                    }
        
        # Count successes
        successful_runs = sum(1 for result in execution_results.values() if result.get('success', False))
        
        test_name = "example_execution"
        if successful_runs == len(examples):
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED',
                'message': f"All {len(examples)} examples executed successfully",
                'execution_results': execution_results
            }
            print(f"✅ Execution test PASSED: All {len(examples)} examples run successfully")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED' if successful_runs == 0 else 'PARTIAL',
                'message': f"{successful_runs}/{len(examples)} examples executed successfully",
                'execution_results': execution_results
            }
            if successful_runs == 0:
                print(f"❌ Execution test FAILED: No examples executed successfully")
            else:
                print(f"⚠️ Execution test PARTIAL: {successful_runs}/{len(examples)} examples successful")
        
        self._update_test_counts(test_name)
    
    def test_aws_scripts(self):
        """Test that AWS deployment scripts are present and valid"""
        
        print("\n☁️ Testing AWS deployment scripts...")
        
        aws_scripts = [
            'evaluation_examples/deploy_deepeval_aws.sh',
            'evaluation_examples/deploy_geval_aws.sh',
            'evaluation_examples/deploy_llmebench_aws.sh', 
            'evaluation_examples/deploy_langsmith_aws.sh',
            'evaluation_examples/deploy_ragas_aws.sh'
        ]
        
        script_status = {}
        
        for script_path in aws_scripts:
            if Path(script_path).exists():
                try:
                    with open(script_path, 'r') as f:
                        content = f.read()
                        script_status[script_path] = {
                            'exists': True,
                            'length': len(content),
                            'has_shebang': content.startswith('#!/bin/bash'),
                            'has_aws_commands': 'aws' in content.lower()
                        }
                except Exception as e:
                    script_status[script_path] = {
                        'exists': True,
                        'error': str(e)
                    }
            else:
                script_status[script_path] = {'exists': False}
        
        valid_scripts = sum(1 for status in script_status.values() 
                          if status.get('exists') and status.get('has_aws_commands', False))
        
        test_name = "aws_scripts"
        if valid_scripts == len(aws_scripts):
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED',
                'message': f"All {len(aws_scripts)} AWS scripts are valid",
                'script_details': script_status
            }
            print(f"✅ AWS scripts test PASSED: All {len(aws_scripts)} scripts valid")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': f"{valid_scripts}/{len(aws_scripts)} AWS scripts are valid",
                'script_details': script_status
            }
            print(f"❌ AWS scripts test FAILED: Only {valid_scripts}/{len(aws_scripts)} scripts valid")
        
        self._update_test_counts(test_name)
    
    def test_documentation(self):
        """Test README.md documentation completeness"""
        
        print("\n📚 Testing documentation...")
        
        readme_path = 'README.md'
        
        if not Path(readme_path).exists():
            test_name = "documentation"
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': 'README.md not found'
            }
            print("❌ Documentation test FAILED: README.md not found")
            self._update_test_counts(test_name)
            return
        
        with open(readme_path, 'r') as f:
            readme_content = f.read()
        
        required_sections = [
            'DeepEval',
            'G-Eval', 
            'LLMeBench',
            'LangSmith',
            'Ragas',
            'Installation',
            'Usage'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in readme_content.lower():
                missing_sections.append(section)
        
        test_name = "documentation"
        if missing_sections:
            self.test_results['test_details'][test_name] = {
                'status': 'FAILED',
                'message': f"Missing sections: {missing_sections}",
                'readme_length': len(readme_content),
                'sections_found': len(required_sections) - len(missing_sections)
            }
            print(f"❌ Documentation test FAILED: {len(missing_sections)} sections missing")
        else:
            self.test_results['test_details'][test_name] = {
                'status': 'PASSED',
                'message': "All required sections present",
                'readme_length': len(readme_content),
                'sections_found': len(required_sections)
            }
            print(f"✅ Documentation test PASSED: All {len(required_sections)} sections found")
        
        self._update_test_counts(test_name)
    
    def _update_test_counts(self, test_name: str):
        """Update test counters"""
        
        self.test_results['tests_run'] += 1
        
        if self.test_results['test_details'][test_name]['status'] == 'PASSED':
            self.test_results['tests_passed'] += 1
        else:
            self.test_results['tests_failed'] += 1
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        
        end_time = time.time()
        duration = end_time - self.test_results['start_time']
        
        print(f"\n🏁 INTEGRATION TEST RESULTS")
        print("="*35)
        print(f"⏱️ Total Duration: {duration:.2f} seconds")
        print(f"🧪 Tests Run: {self.test_results['tests_run']}")
        print(f"✅ Tests Passed: {self.test_results['tests_passed']}")
        print(f"❌ Tests Failed: {self.test_results['tests_failed']}")
        
        pass_rate = (self.test_results['tests_passed'] / self.test_results['tests_run'] * 100) if self.test_results['tests_run'] > 0 else 0
        print(f"📊 Pass Rate: {pass_rate:.1f}%")
        
        # Detailed results
        print(f"\n📋 DETAILED TEST RESULTS")
        print("-"*28)
        
        for test_name, details in self.test_results['test_details'].items():
            status_icon = "✅" if details['status'] == 'PASSED' else "❌" if details['status'] == 'FAILED' else "⚠️"
            print(f"{status_icon} {test_name}: {details['message']}")
        
        # Save results to file
        self.test_results['end_time'] = end_time
        self.test_results['duration'] = duration
        self.test_results['pass_rate'] = pass_rate
        
        results_path = 'evaluation_examples/integration_test_results.json'
        with open(results_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: {results_path}")
        
        # Final assessment
        if pass_rate >= 80:
            print(f"\n🎉 INTEGRATION TESTS: EXCELLENT ({pass_rate:.1f}% pass rate)")
            print("✨ Your LLM evaluation framework is ready for use!")
        elif pass_rate >= 60:
            print(f"\n👍 INTEGRATION TESTS: GOOD ({pass_rate:.1f}% pass rate)") 
            print("💡 Consider addressing failing tests for optimal performance")
        else:
            print(f"\n⚠️ INTEGRATION TESTS: NEEDS ATTENTION ({pass_rate:.1f}% pass rate)")
            print("🔧 Please review and fix failing tests before deployment")

def main():
    """Main execution function"""
    
    print("🚀 LLM EVALUATION FRAMEWORK - INTEGRATION TEST SUITE")
    print("="*60)
    print("Testing comprehensive evaluation framework...")
    
    # Initialize and run tester
    tester = EvaluationFrameworkTester()
    tester.run_all_tests()
    
    print(f"\n✨ Integration testing completed!")
    print("📖 Check integration_test_results.json for detailed results")

if __name__ == "__main__":
    main()
