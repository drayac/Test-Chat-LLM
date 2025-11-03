#!/usr/bin/env python3
"""
Test Suite for LLM-library Chat Test Application
Tests core functionality, API integration, authentication, and UI components
"""

import os
import sys
import json
import time
import requests
import subprocess
import tempfile
import threading
from pathlib import Path

# Add the app directory to the path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Test configuration
TEST_CONFIG = {
    "app_port": 8511,  # Use different port for testing
    "test_timeout": 30,
    "api_timeout": 10,
    "groq_api_key": "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"
}

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.app_process = None
        self.test_data_file = None
        
    def log(self, message, color=Colors.WHITE):
        """Print colored log message"""
        print(f"{color}{message}{Colors.END}")
        
    def success(self, message):
        """Print success message"""
        self.log(f"✅ {message}", Colors.GREEN)
        self.passed += 1
        
    def failure(self, message):
        """Print failure message"""
        self.log(f"❌ {message}", Colors.RED)
        self.failed += 1
        
    def info(self, message):
        """Print info message"""
        self.log(f"ℹ️  {message}", Colors.CYAN)
        
    def warning(self, message):
        """Print warning message"""
        self.log(f"⚠️  {message}", Colors.YELLOW)

    def test_dependencies(self):
        """Test if all required dependencies are installed"""
        self.log(f"\n{Colors.BOLD}🔍 Testing Dependencies{Colors.END}")
        
        required_packages = ['streamlit', 'groq', 'requests']
        
        for package in required_packages:
            try:
                __import__(package)
                self.success(f"{package} is installed")
            except ImportError:
                self.failure(f"{package} is NOT installed")
                
    def test_file_structure(self):
        """Test if all required files exist"""
        self.log(f"\n{Colors.BOLD}📁 Testing File Structure{Colors.END}")
        
        required_files = [
            'app_groq_chat.py',
            'requirements.txt',
            'README.md',
            'DEPLOYMENT.md',
            'launch_groq_app.sh',
            'Dockerfile',
            'docker-compose.yml',
            'Procfile',
            '.streamlit/config.toml',
            '.gitignore'
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                self.success(f"{file_path} exists")
            else:
                self.failure(f"{file_path} is missing")

    def test_groq_api_connection(self):
        """Test Groq API connectivity"""
        self.log(f"\n{Colors.BOLD}🌐 Testing Groq API Connection{Colors.END}")
        
        try:
            headers = {
                "Authorization": f"Bearer {TEST_CONFIG['groq_api_key']}",
                "Content-Type": "application/json"
            }
            
            # Test models endpoint
            response = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers=headers,
                timeout=TEST_CONFIG['api_timeout']
            )
            
            if response.status_code == 200:
                models_data = response.json()
                model_count = len(models_data.get("data", []))
                self.success(f"Groq API connected - {model_count} models available")
                
                # Test specific models
                common_models = ["llama3-8b-8192", "mixtral-8x7b-32768"]
                available_models = [model["id"] for model in models_data.get("data", [])]
                
                for model in common_models:
                    if model in available_models:
                        self.success(f"Model {model} is available")
                    else:
                        self.warning(f"Model {model} not found")
                        
            else:
                self.failure(f"Groq API returned status {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.failure("Groq API connection timeout")
        except Exception as e:
            self.failure(f"Groq API error: {str(e)}")

    def test_app_imports(self):
        """Test if the main app can be imported without errors"""
        self.log(f"\n{Colors.BOLD}📦 Testing App Imports{Colors.END}")
        
        try:
            # Test importing app components
            import app_groq_chat
            self.success("Main app module imports successfully")
            
            # Test key functions exist
            required_functions = [
                'get_groq_models',
                'test_groq_api', 
                'generate_guest_id',
                'load_user_data',
                'save_user_data',
                'authenticate_user',
                'register_user'
            ]
            
            for func_name in required_functions:
                if hasattr(app_groq_chat, func_name):
                    self.success(f"Function {func_name} exists")
                else:
                    self.failure(f"Function {func_name} is missing")
                    
        except Exception as e:
            self.failure(f"App import failed: {str(e)}")

    def start_test_app(self):
        """Start the Streamlit app for testing"""
        self.log(f"\n{Colors.BOLD}🚀 Starting Test App{Colors.END}")
        
        try:
            # Create a temporary users file for testing
            self.test_data_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            self.test_data_file.write('{}')
            self.test_data_file.close()
            
            # Start the app
            cmd = [
                sys.executable, "-m", "streamlit", "run", "app_groq_chat.py",
                "--server.port", str(TEST_CONFIG['app_port']),
                "--server.address", "localhost",
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            self.app_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=app_dir
            )
            
            # Wait for app to start
            self.info("Waiting for app to start...")
            time.sleep(10)
            
            # Check if app is running
            if self.app_process.poll() is None:
                self.success(f"App started on port {TEST_CONFIG['app_port']}")
                return True
            else:
                stdout, stderr = self.app_process.communicate()
                self.failure(f"App failed to start: {stderr.decode()}")
                return False
                
        except Exception as e:
            self.failure(f"Failed to start app: {str(e)}")
            return False

    def test_app_endpoints(self):
        """Test app HTTP endpoints"""
        self.log(f"\n{Colors.BOLD}🌐 Testing App Endpoints{Colors.END}")
        
        base_url = f"http://localhost:{TEST_CONFIG['app_port']}"
        
        endpoints = [
            "/",
            "/_stcore/health"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(
                    f"{base_url}{endpoint}",
                    timeout=TEST_CONFIG['api_timeout']
                )
                
                if response.status_code == 200:
                    self.success(f"Endpoint {endpoint} is accessible")
                else:
                    self.failure(f"Endpoint {endpoint} returned {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.failure(f"Cannot connect to {endpoint}")
            except Exception as e:
                self.failure(f"Error testing {endpoint}: {str(e)}")

    def test_authentication_functions(self):
        """Test authentication functions"""
        self.log(f"\n{Colors.BOLD}🔐 Testing Authentication Functions{Colors.END}")
        
        try:
            import app_groq_chat as app
            
            # Test guest ID generation
            guest_id = app.generate_guest_id()
            if guest_id.startswith("Guest_") and len(guest_id) == 14:
                self.success("Guest ID generation works")
            else:
                self.failure(f"Invalid guest ID format: {guest_id}")
            
            # Test password hashing
            password = "test123"
            hashed = app.hash_password(password)
            if len(hashed) == 64:  # SHA256 produces 64 character hex string
                self.success("Password hashing works")
            else:
                self.failure("Password hashing failed")
                
            # Test user registration (with temporary file)
            test_email = "test@example.com"
            success, message = app.register_user(test_email, password, is_guest=False)
            if success:
                self.success("User registration works")
            else:
                self.failure(f"User registration failed: {message}")
                
            # Test authentication
            success, message = app.authenticate_user(test_email, password)
            if success:
                self.success("User authentication works")
            else:
                self.failure(f"User authentication failed: {message}")
                
        except Exception as e:
            self.failure(f"Authentication test error: {str(e)}")

    def test_model_loading(self):
        """Test model loading functionality"""
        self.log(f"\n{Colors.BOLD}🤖 Testing Model Loading{Colors.END}")
        
        try:
            import app_groq_chat as app
            
            # Test API model fetching
            models = app.get_groq_models()
            if isinstance(models, dict) and len(models) > 0:
                self.success(f"Model loading works - {len(models)} models loaded")
                
                # Check for expected models
                expected_models = ["llama3-8b-8192", "mixtral-8x7b-32768"]
                for model in expected_models:
                    if model in models:
                        self.success(f"Expected model {model} found")
                    else:
                        self.warning(f"Expected model {model} not found")
            else:
                self.failure("Model loading failed or returned empty")
                
            # Test fallback models
            fallback_models = app.get_fallback_models()
            if isinstance(fallback_models, dict) and len(fallback_models) > 0:
                self.success(f"Fallback models work - {len(fallback_models)} models")
            else:
                self.failure("Fallback models failed")
                
        except Exception as e:
            self.failure(f"Model loading test error: {str(e)}")

    def stop_test_app(self):
        """Stop the test app"""
        if self.app_process:
            self.info("Stopping test app...")
            self.app_process.terminate()
            time.sleep(2)
            if self.app_process.poll() is None:
                self.app_process.kill()
                
        # Clean up test data file
        if self.test_data_file:
            try:
                os.unlink(self.test_data_file.name)
            except:
                pass

    def test_docker_setup(self):
        """Test Docker configuration"""
        self.log(f"\n{Colors.BOLD}🐳 Testing Docker Setup{Colors.END}")
        
        # Check if Docker files are valid
        try:
            with open('Dockerfile', 'r') as f:
                dockerfile_content = f.read()
                if 'FROM python:3.9-slim' in dockerfile_content:
                    self.success("Dockerfile has correct base image")
                if 'EXPOSE 8510' in dockerfile_content:
                    self.success("Dockerfile exposes correct port")
                if 'streamlit run' in dockerfile_content:
                    self.success("Dockerfile has correct CMD")
                    
        except Exception as e:
            self.failure(f"Dockerfile test failed: {str(e)}")
            
        # Check docker-compose.yml
        try:
            with open('docker-compose.yml', 'r') as f:
                compose_content = f.read()
                if 'ports:' in compose_content and '8510:8510' in compose_content:
                    self.success("docker-compose.yml has correct port mapping")
                if 'GROQ_API_KEY' in compose_content:
                    self.success("docker-compose.yml has environment variable")
                    
        except Exception as e:
            self.failure(f"docker-compose.yml test failed: {str(e)}")

    def run_all_tests(self):
        """Run the complete test suite"""
        self.log(f"\n{Colors.BOLD}{Colors.BLUE}🧪 LLM-library Chat Test - Test Suite{Colors.END}")
        self.log(f"{Colors.BOLD}==========================================={Colors.END}")
        
        start_time = time.time()
        
        # Run tests
        self.test_dependencies()
        self.test_file_structure()
        self.test_groq_api_connection()
        self.test_app_imports()
        self.test_authentication_functions()
        self.test_model_loading()
        self.test_docker_setup()
        
        # Optional: Test running app (can be slow)
        if len(sys.argv) > 1 and sys.argv[1] == "--full":
            if self.start_test_app():
                self.test_app_endpoints()
                self.stop_test_app()
        
        # Results
        duration = time.time() - start_time
        total_tests = self.passed + self.failed
        
        self.log(f"\n{Colors.BOLD}📊 Test Results{Colors.END}")
        self.log(f"{'='*50}")
        self.log(f"Total Tests: {total_tests}")
        self.success(f"Passed: {self.passed}")
        if self.failed > 0:
            self.failure(f"Failed: {self.failed}")
        else:
            self.log(f"Failed: {self.failed}", Colors.GREEN)
        self.log(f"Duration: {duration:.2f} seconds")
        self.log(f"{'='*50}")
        
        if self.failed == 0:
            self.log(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ALL TESTS PASSED! App is ready for deployment.{Colors.END}")
            return True
        else:
            self.log(f"\n{Colors.BOLD}{Colors.RED}❌ {self.failed} test(s) failed. Please fix issues before deployment.{Colors.END}")
            return False

if __name__ == "__main__":
    # Change to app directory
    os.chdir(app_dir)
    
    # Run tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)