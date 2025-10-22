#!/bin/bash

set -e  # Exit on error (except where explicitly handled)

# ============================================================================
# Helper Functions
# ============================================================================

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: Python3 could not be found. Please install Python3 to proceed."
        exit 1
    fi
    echo "✓ Python3 found"
}

setup_venv() {
    if [[ -d "venv" ]]; then
        echo "✓ Virtual environment 'venv' already exists. Skipping creation."
    else
        echo "→ Creating virtual environment 'venv'..."
        python3 -m venv venv
        echo "✓ Virtual environment created"
    fi
}

activate_venv() {
    if [[ -f "venv/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    else
        echo "ERROR: venv/bin/activate not found. Virtual environment may not have been created correctly."
        exit 1
    fi
}

install_dependencies() {
    echo "→ Installing dependencies from requirements.txt..."
    if pip install -r requirements.txt; then
        echo "✓ Dependencies installed successfully"
    else
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
}

prompt_yes_no() {
    local prompt="$1"
    local response
    read -r -p "$prompt (y/N): " response
    response=${response,,}  # to lowercase
    [[ "$response" == "y" || "$response" == "yes" ]]
}

create_env_file() {
    local api_key="$1"
    local example_file=".env.example"
    local target_file=".env"
    
    if [[ -f "$example_file" ]]; then
        cp "$example_file" "$target_file"
        if grep -qE '^LANGCHAIN_API_KEY=' "$target_file"; then
            sed -i.bak -E "s|^LANGCHAIN_API_KEY=.*|LANGCHAIN_API_KEY=${api_key}|" "$target_file"
            rm -f "${target_file}.bak"
        else
            echo "LANGCHAIN_API_KEY=${api_key}" >> "$target_file"
        fi
        echo "✓ .env file created from $example_file"
    else
        cat > "$target_file" <<EOF
LANGCHAIN_TRACING_V2=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=agent-example
LANGCHAIN_API_KEY=${api_key}
EOF
        echo "✓ .env file created with default configuration"
    fi
}

setup_langchain_env() {
    if prompt_yes_no "Do you want to enter a LangSmith / LangChain API key now?"; then
        local api_key
        read -r -s -p "Enter your LANGCHAIN_API_KEY: " api_key
        echo  # newline after hidden input
        
        if [[ -z "$api_key" ]]; then
            echo "⚠ No API key entered; skipping .env creation."
            return 0
        fi
        
        create_env_file "$api_key"
    else
        echo "⊘ Skipping LangChain API key setup"
    fi
}

install_ollama() {
    if ! prompt_yes_no "Do you want to install Ollama?"; then
        echo "⊘ Skipping Ollama installation"
        return 0
    fi
    
    echo ""
    echo "⚠ WARNING: About to run the official Ollama remote installer script (curl | sh)."
    echo "  This will download and execute a script from https://ollama.com"
    echo ""
    
    if ! prompt_yes_no "Proceed with running the remote installer?"; then
        echo "⊘ Ollama installation cancelled"
        return 0
    fi
    
    echo "→ Running Ollama remote installer..."
    if curl -fsSL https://ollama.com/install.sh | sh; then
        echo "✓ Ollama installation completed"
        download_llama_model
    else
        echo "✗ Ollama installation failed"
        return 1
    fi
}

download_llama_model() {
    if ! prompt_yes_no "Do you want to download and run llama3.2 now? (This will pull the model)"; then
        echo "⊘ Skipping llama3.2 download"
        return 0
    fi
    
    if ! command -v ollama &> /dev/null; then
        echo "✗ Ollama command not found after install. Please ensure Ollama is in your PATH."
        return 1
    fi
    
    echo "→ Pulling and running llama3.2 (this may take a while)..."
    # Run ollama in foreground to see the download progress, then exit
    if ollama run llama3.2 --help &> /dev/null; then
        echo "✓ llama3.2 is ready to use"
        echo "  Run: ollama run llama3.2"
    else
        echo "⚠ To run llama3.2, use: ollama run llama3.2"
    fi
}

# ============================================================================
# Main Setup Flow
# ============================================================================

main() {
    echo "========================================"
    echo "  Project Setup Script"
    echo "========================================"
    echo ""
    
    check_python
    setup_venv
    activate_venv
    install_dependencies
    
    echo ""
    echo "========================================"
    echo "  Optional Configuration"
    echo "========================================"
    echo ""
    
    setup_langchain_env
    echo ""
    install_ollama
    
    echo ""
    echo "========================================"
    echo "✓ Setup Complete!"
    echo "========================================"
    echo ""
    echo "To activate the virtual environment later, run:"
    echo "  source venv/bin/activate"
}

# Run main function
main