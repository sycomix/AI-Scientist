#!/bin/bash

# Check if conda environment exists
if ! conda env list | grep -q "ai_scientist"; then
    echo "Creating conda environment 'ai_scientist'..."
    conda create -n ai_scientist python=3.9 -y
fi

# Activate conda environment
echo "Activating conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ai_scientist

# Install requirements if needed
if [ ! -f "requirements.installed" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    pip install inquirer
    touch requirements.installed
fi

# Run configuration if needed
if [ ! -f "config/ai_scientist_config.json" ] || [ "$1" == "--configure" ]; then
    echo "Running configuration wizard..."
    python config_ai_scientist.py
fi

# Launch the AI Scientist
echo "Launching AI Scientist..."
python launch_ai_scientist.py "$@"