#!/bin/bash

# Test Runner for LLM-library Chat Test
# Provides multiple test options for verifying app functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BOLD}${BLUE}🧪 LLM-library Chat Test - Test Runner${NC}"
echo -e "${BOLD}=======================================${NC}"

# Function to print colored output
log_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log_success "Virtual environment is activated: $VIRTUAL_ENV"
        return 0
    else
        log_warning "Virtual environment not activated. Attempting to activate..."
        if [ -d "groq_env" ]; then
            source groq_env/bin/activate
            log_success "Activated groq_env virtual environment"
            return 0
        else
            log_error "No virtual environment found. Creating one..."
            python3 -m venv groq_env
            source groq_env/bin/activate
            pip install -r requirements.txt
            log_success "Created and activated new virtual environment"
            return 0
        fi
    fi
}

# Function to run quick test
run_quick_test() {
    log_info "Running quick functionality test..."
    python3 quick_test.py
    return $?
}

# Function to run comprehensive test
run_full_test() {
    log_info "Running comprehensive test suite..."
    python3 test_app.py
    return $?
}

# Function to run full test with live app
run_live_test() {
    log_info "Running comprehensive test suite with live app testing..."
    python3 test_app.py --full
    return $?
}

# Function to test API connectivity
test_api() {
    log_info "Testing Groq API connectivity..."
    
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" \
        -H "Authorization: Bearer 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" \
        -H "Content-Type: application/json" \
        "https://api.groq.com/openai/v1/models")
    
    http_status=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_status" = "200" ]; then
        model_count=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*//' | jq '.data | length' 2>/dev/null || echo "unknown")
        log_success "Groq API connected successfully - $model_count models available"
        return 0
    else
        log_error "Groq API connection failed with status: $http_status"
        return 1
    fi
}

# Function to test Docker setup
test_docker() {
    log_info "Testing Docker setup..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker is installed"
        
        # Test build
        log_info "Testing Docker build..."
        if docker build -t llm-library-chat-test . &> /dev/null; then
            log_success "Docker build successful"
            
            # Clean up test image
            docker rmi llm-library-chat-test &> /dev/null || true
            return 0
        else
            log_error "Docker build failed"
            return 1
        fi
    else
        log_warning "Docker not installed - skipping Docker tests"
        return 0
    fi
}

# Function to validate file structure
validate_files() {
    log_info "Validating file structure..."
    
    required_files=(
        "app_groq_chat.py"
        "requirements.txt"
        "README.md"
        "DEPLOYMENT.md"
        "launch_groq_app.sh"
        "Dockerfile"
        "docker-compose.yml"
        "Procfile"
        ".streamlit/config.toml"
        ".gitignore"
    )
    
    missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "$file exists"
        else
            log_error "$file is missing"
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        log_success "All required files present"
        return 0
    else
        log_error "${#missing_files[@]} files missing"
        return 1
    fi
}

# Function to run integration test
run_integration_test() {
    log_info "Running integration test..."
    python3 integration_test.py
    return $?
}

# Function to show help
show_help() {
    echo -e "${BOLD}Available test options:${NC}"
    echo ""
    echo -e "${CYAN}./run_tests.sh quick${NC}       - Run quick functionality test (recommended)"
    echo -e "${CYAN}./run_tests.sh full${NC}        - Run comprehensive test suite"
    echo -e "${CYAN}./run_tests.sh live${NC}        - Run full tests including live app testing"
    echo -e "${CYAN}./run_tests.sh integration${NC} - Run end-to-end integration test"
    echo -e "${CYAN}./run_tests.sh api${NC}         - Test only API connectivity"
    echo -e "${CYAN}./run_tests.sh docker${NC}      - Test Docker setup"
    echo -e "${CYAN}./run_tests.sh files${NC}       - Validate file structure"
    echo -e "${CYAN}./run_tests.sh all${NC}         - Run all tests"
    echo -e "${CYAN}./run_tests.sh help${NC}        - Show this help"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  ${CYAN}./run_tests.sh quick${NC}        # Fast test before launching app"
    echo -e "  ${CYAN}./run_tests.sh integration${NC}  # End-to-end test with live app"
    echo -e "  ${CYAN}./run_tests.sh all${NC}          # Complete validation before deployment"
}

# Main execution
main() {
    local test_type=${1:-"help"}
    local exit_code=0
    
    case "$test_type" in
        "quick")
            check_venv
            run_quick_test
            exit_code=$?
            ;;
        "full")
            check_venv
            run_full_test
            exit_code=$?
            ;;
        "live")
            check_venv
            run_live_test
            exit_code=$?
            ;;
        "api")
            test_api
            exit_code=$?
            ;;
        "docker")
            test_docker
            exit_code=$?
            ;;
        "files")
            validate_files
            exit_code=$?
            ;;
        "integration")
            run_integration_test
            exit_code=$?
            ;;
        "all")
            log_info "Running complete test suite..."
            echo ""
            
            validate_files
            test_api
            test_docker
            check_venv
            run_full_test
            
            # Check overall result
            if [ $? -eq 0 ]; then
                log_success "All tests completed successfully!"
                exit_code=0
            else
                log_error "Some tests failed"
                exit_code=1
            fi
            ;;
        "help"|*)
            show_help
            exit_code=0
            ;;
    esac
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        log_success "Test completed successfully!"
        echo -e "${BOLD}${GREEN}🚀 Ready to launch: ./launch_groq_app.sh${NC}"
    else
        log_error "Test failed! Please fix issues before deployment."
    fi
    
    return $exit_code
}

# Execute main function
main "$@"
exit $?