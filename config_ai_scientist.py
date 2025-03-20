import json
import os
import sys
from pathlib import Path
import inquirer
from typing import Dict, Any
import platform

DEFAULT_CONFIG_PATH = os.path.join("config", "ai_scientist_config.json")

def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"

def ensure_directory(path: str) -> None:
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def clear_screen() -> None:
    """Clear the console screen in a cross-platform way."""
    os.system('cls' if is_windows() else 'clear')

def load_existing_config() -> Dict[Any, Any]:
    """Load existing configuration if available."""
    if os.path.exists(DEFAULT_CONFIG_PATH):
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def validate_api_key(key: str) -> bool:
    """Validate API key format."""
    return bool(key and len(key.strip()) > 10)

def get_default_cuda_devices() -> str:
    """Get default CUDA devices based on platform."""
    if is_windows():
        import subprocess
        try:
            # Try to get nvidia-smi output
            subprocess.check_output(['nvidia-smi'])
            return '0'  # Default to first GPU if available
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ''  # No CUDA devices found
    else:
        return '0'  # Default for non-Windows platforms

def configure_llm_provider() -> Dict[str, Any]:
    """Configure LLM provider settings."""
    clear_screen()
    print("\nLLM Provider Configuration")
    print("========================\n")
    
    questions = [
        inquirer.List('provider_type',
            message="Select your LLM provider type",
            choices=[
                'OpenAI Compatible',
                'Anthropic',
                'Custom Provider'
            ]
        )
    ]
    answers = inquirer.prompt(questions)
    
    provider_config = {}
    
    if answers['provider_type'] == 'Custom Provider':
        custom_questions = [
            inquirer.Text('api_base_url',
                message="Enter your API base URL",
                validate=lambda _, x: bool(x.strip())
            ),
            inquirer.Text('api_key',
                message="Enter your API key",
                validate=lambda _, x: validate_api_key(x)
            ),
            inquirer.Text('model_name',
                message="Enter your model name",
                validate=lambda _, x: bool(x.strip())
            ),
            inquirer.Text('max_tokens',
                message="Enter maximum tokens supported",
                default="8192",
                validate=lambda _, x: x.isdigit()
            ),
            inquirer.Confirm('supports_functions',
                message="Does your model support OpenAI functions?",
                default=False
            ),
            inquirer.Text('temperature',
                message="Enter default temperature (0.0-1.0)",
                default="0.7",
                validate=lambda _, x: 0 <= float(x) <= 1
            )
        ]
        custom_answers = inquirer.prompt(custom_questions)
        provider_config.update(custom_answers)
        
    return {
        'provider_type': answers['provider_type'],
        'settings': provider_config
    }

def configure_experiment_settings() -> Dict[str, Any]:
    """Configure experiment settings."""
    clear_screen()
    print("\nExperiment Configuration")
    print("======================\n")
    
    questions = [
        inquirer.Text('num_ideas',
            message="Number of ideas to generate",
            default="50",
            validate=lambda _, x: x.isdigit()
        ),
        inquirer.List('experiment_type',
            message="Select experiment type",
            choices=[
                'nanoGPT',
                'nanoGPT_lite',
                'custom'
            ]
        ),
        inquirer.Text('parallel_processes',
            message="Number of parallel processes (0 for sequential)",
            default=get_default_cuda_devices(),
            validate=lambda _, x: x.isdigit()
        ),
        inquirer.Confirm('improvement_enabled',
            message="Enable improvement based on reviews?",
            default=True
        )
    ]
    
    return inquirer.prompt(questions)

def configure_system_settings() -> Dict[str, Any]:
    """Configure system-specific settings."""
    clear_screen()
    print("\nSystem Configuration")
    print("===================\n")
    
    questions = [
        inquirer.Text('temp_directory',
            message="Temporary directory path",
            default=os.getenv('TEMP' if is_windows() else 'TMPDIR', os.path.join(os.path.expanduser("~"), "temp")),
            validate=lambda _, x: bool(x.strip())
        ),
        inquirer.Confirm('use_gpu',
            message="Use GPU if available?",
            default=True
        )
    ]
    
    return inquirer.prompt(questions)

def save_configuration(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    ensure_directory(os.path.dirname(DEFAULT_CONFIG_PATH))
    with open(DEFAULT_CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"\nConfiguration saved to {DEFAULT_CONFIG_PATH}")

def main() -> None:
    """Main configuration function."""
    clear_screen()
    print("\nAI Scientist Configuration Wizard")
    print("================================\n")
    
    existing_config = load_existing_config()
    
    if existing_config:
        questions = [
            inquirer.Confirm('use_existing',
                message="Existing configuration found. Would you like to use it?",
                default=True
            )
        ]
        answers = inquirer.prompt(questions)
        if answers['use_existing']:
            return
    
    config = {
        'llm_provider': configure_llm_provider(),
        'experiment': configure_experiment_settings(),
        'system': configure_system_settings(),
        'platform': platform.system(),
        'version': '1.0'
    }
    
    save_configuration(config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nConfiguration cancelled.")
        sys.exit(1)
