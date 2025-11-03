#!/usr/bin/env python3
"""
Quick Test Script for LLM-library Chat Test
Performs basic smoke tests to verify core functionality
"""

import os
import sys
import json
import requests
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(message, color=Colors.CYAN):
    print(f"{color}{message}{Colors.END}")

def success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def failure(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def test_basic_functionality():
    """Run basic functionality tests"""
    log(f"\n{Colors.BOLD}🧪 Quick Test - LLM-library Chat Test{Colors.END}")
    log("=" * 50)
    
    passed = 0
    failed = 0
    
    # Test 1: Check if main app file exists
    if Path("app_groq_chat.py").exists():
        success("Main app file exists")
        passed += 1
    else:
        failure("Main app file missing")
        failed += 1
    
    # Test 2: Check dependencies
    try:
        import streamlit, groq, requests
        success("All dependencies available")
        passed += 1
    except ImportError as e:
        failure(f"Missing dependency: {e}")
        failed += 1
    
    # Test 3: Test Groq API
    try:
        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            models = response.json().get("data", [])
            success(f"Groq API connected - {len(models)} models available")
            passed += 1
        else:
            failure(f"Groq API returned status {response.status_code}")
            failed += 1
    except Exception as e:
        failure(f"Groq API test failed: {str(e)}")
        failed += 1
    
    # Test 4: Test app imports
    try:
        sys.path.insert(0, str(Path.cwd()))
        import app_groq_chat
        success("App imports successfully")
        passed += 1
        
        # Test key functions
        if hasattr(app_groq_chat, 'get_groq_models'):
            success("get_groq_models function exists")
            passed += 1
        else:
            failure("get_groq_models function missing")
            failed += 1
            
    except Exception as e:
        failure(f"App import failed: {str(e)}")
        failed += 2
    
    # Test 5: Test model loading
    try:
        models = app_groq_chat.get_groq_models()
        if isinstance(models, dict) and len(models) > 0:
            success(f"Model loading works - {len(models)} models")
            passed += 1
        else:
            failure("Model loading failed")
            failed += 1
    except Exception as e:
        failure(f"Model loading error: {str(e)}")
        failed += 1
    
    # Test 6: Test authentication functions
    try:
        guest_id = app_groq_chat.generate_guest_id()
        if guest_id.startswith("Guest_"):
            success("Guest ID generation works")
            passed += 1
        else:
            failure("Guest ID generation failed")
            failed += 1
    except Exception as e:
        failure(f"Authentication test failed: {str(e)}")
        failed += 1
    
    # Test 7: Check deployment files
    deployment_files = ["README.md", "requirements.txt", "Dockerfile", "docker-compose.yml"]
    deployment_count = 0
    for file in deployment_files:
        if Path(file).exists():
            deployment_count += 1
    
    if deployment_count == len(deployment_files):
        success("All deployment files present")
        passed += 1
    else:
        failure(f"Missing deployment files: {len(deployment_files) - deployment_count}")
        failed += 1
    
    # Results
    log(f"\n{Colors.BOLD}📊 Quick Test Results{Colors.END}")
    log("=" * 30)
    total = passed + failed
    log(f"Total Tests: {total}")
    log(f"Passed: {passed}", Colors.GREEN if passed > 0 else Colors.RED)
    log(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN)
    log(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        log(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! Ready to run.{Colors.END}")
    else:
        log(f"\n{Colors.BOLD}{Colors.YELLOW}⚠️  Some tests failed. Check issues above.{Colors.END}")
    
    return failed == 0

if __name__ == "__main__":
    success_flag = test_basic_functionality()
    
    if success_flag:
        log(f"\n{Colors.BOLD}🚀 Ready to launch app:{Colors.END}")
        log("./launch_groq_app.sh")
        log("or")
        log("streamlit run app_groq_chat.py --server.port 8510")
    
    sys.exit(0 if success_flag else 1)