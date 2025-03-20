#!/usr/bin/env python3
import argparse
import json
import os
import sys
from typing import Dict, Any
import subprocess
import shutil
import platform

CONFIG_PATH = os.path.join("config", "ai_scientist_config.json")

def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"

def load_configuration() -> Dict[str, Any]:
    """Load configuration from file."""
    if not os.path.exists(CONFIG_PATH):
        print("Configuration not found. Please run config_ai_scientist.py first.")
        sys.exit(1)
    
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def validate_environment() -> None:
    """Validate environment setup."""
    required_commands = ['python', 'git']
    for cmd in required_commands:
        cmd_name = f"{cmd}.exe" if is_windows() else cmd
        if not shutil.which(cmd_name):
            print(f"Error: {cmd} not found in PATH")
            sys.exit(1)

def setup_environment(config: Dict[str, Any]) -> None:
    """Setup environment variables based on configuration."""
    provider_settings = config['llm_provider']['settings']
    
    if config['llm_provider']['provider_type'] == 'Custom Provider':
        os.environ['CUSTOM_API_KEY'] = provider_settings['api_key']
        os.environ['CUSTOM_API_BASE_URL'] = provider_settings['api_base_url']
    
    # Set system-specific environment variables
    os.environ['TEMP'] = config['system']['temp_directory']
    if is_windows():
        os.environ['TMP'] = config['system']['temp_directory']
    
    # Set CUDA_VISIBLE_DEVICES if parallel processing is enabled
    if int(config['experiment']['parallel_processes']) > 0 and config['system']['use_gpu']:
        os.environ['CUDA_VISIBLE_DEVICES'] = ','.join(
            str(i) for i in range(int(config['experiment']['parallel_processes']))
        )

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Launch AI Scientist experiments')
    parser.add_argument('--config', 
                       help='Path to custom configuration file',
                       default=CONFIG_PATH)
    parser.add_argument('--debug', 
                       action='store_true',
                       help='Enable debug mode')
    return parser.parse_args()

def build_launch_command(config: Dict[str, Any]) -> list:
    """Build the launch command based on configuration."""
    cmd = [
        'python',
        'launch_scientist.py',
        '--model', f"custom/{config['llm_provider']['settings']['model_name']}"
        if config['llm_provider']['provider_type'] == 'Custom Provider'
        else config['llm_provider']['settings']['model_name'],
        '--experiment', config['experiment']['experiment_type'],
        '--num-ideas', config['experiment']['num_ideas'],
        '--parallel', config['experiment']['parallel_processes']
    ]
    
    if config['experiment']['improvement_enabled']:
        cmd.append('--improvement')
    
    return cmd

def main() -> None:
    """Main launcher function."""
    args = parse_arguments()
    
    print("\nAI Scientist Launcher")
    print("====================\n")
    
    # Validate environment
    validate_environment()
    
    # Load configuration
    config = load_configuration()
    
    # Setup environment
    setup_environment(config)
    
    # Build and execute command
    cmd = build_launch_command(config)
    
    if args.debug:
        print("Debug: Launch command:", ' '.join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running AI Scientist: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExperiment cancelled by user.")
        sys.exit(1)

if __name__ == "__main__":
    main()
