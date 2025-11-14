#!/usr/bin/env python3
"""
Virtual environment setup script for XiaoyaoSearch backend.

This script helps create and configure the Python virtual environment
for the backend development.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and handle errors."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=False,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e}")
        if check:
            sys.exit(1)
        return e


def create_virtual_environment():
    """Create Python virtual environment."""
    venv_path = Path("venv")

    if venv_path.exists():
        print(f"Virtual environment already exists at {venv_path}")
        return True

    print(f"Creating virtual environment at {venv_path}...")

    try:
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        print(f"✓ Virtual environment created successfully")

        # Upgrade pip
        pip_path = venv_path / "Scripts" if os.name == "nt" else venv_path / "bin" / "pip"
        run_command(f'"{pip_path}" install --upgrade pip')

        return True
    except Exception as e:
        print(f"✗ Failed to create virtual environment: {e}")
        return False


def install_requirements():
    """Install requirements in virtual environment."""
    requirements_files = [
        "requirements.txt",
        "requirements-dev.txt"
    ]

    venv_path = Path("venv")
    pip_path = venv_path / "Scripts" / "pip" if os.name == "nt" else venv_path / "bin" / "pip"

    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"Installing {req_file}...")
            run_command(f'"{pip_path}" install -r {req_file}')
        else:
            print(f"Warning: {req_file} not found")


def setup_pre_commit():
    """Setup pre-commit hooks."""
    venv_path = Path("venv")
    precommit_path = venv_path / "Scripts" / "pre-commit" if os.name == "nt" else venv_path / "bin" / "pre-commit"

    if Path(".pre-commit-config.yaml").exists():
        print("Setting up pre-commit hooks...")
        run_command(f'"{precommit_path}" install')
    else:
        print("No .pre-commit-config.yaml found, skipping pre-commit setup")


def create_env_file():
    """Create .env file from example if it doesn't exist."""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_example.exists() and not env_file.exists():
        print("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("✓ .env file created")
        print("⚠️  Please review and update the .env file with your settings")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("No .env.example file found, creating basic .env file...")
        basic_env = """# XiaoyaoSearch Backend Environment Configuration

# Database
DATABASE_URL=sqlite+aiosqlite:///./xiaoyaosearch.db

# Security
SECRET_KEY=your-secret-key-change-in-production

# API Configuration
API_V1_STR=/api/v1
DEBUG=False

# File Storage
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE=10485760

# AI Model Settings
AI_MODEL_DIR=./ai-models
OLLAMA_URL=http://localhost:11434
# OPENAI_API_KEY=your-openai-api-key-here

# Vector Search
VECTOR_INDEX_PATH=./data/vector_index.faiss
FULLTEXT_INDEX_PATH=./data/fulltext_index
"""
        env_file.write_text(basic_env)
        print("✓ Basic .env file created")


def print_next_steps():
    """Print next steps for the user."""
    venv_path = Path("venv")

    if os.name == "nt":
        activate_cmd = f"{venv_path}\\Scripts\\activate"
    else:
        activate_cmd = f"source {venv_path}/bin/activate"

    print("\n" + "="*50)
    print("🎉 Setup complete!")
    print("="*50)
    print("\nNext steps:")
    print(f"1. Activate virtual environment:")
    print(f"   {activate_cmd}")
    print("\n2. Review and update .env file if needed")
    print("\n3. Start the development server:")
    print("   uvicorn main:app --reload")
    print("\n4. Access API documentation:")
    print("   http://127.0.0.1:8000/docs")
    print("\n5. Run tests:")
    print("   pytest")
    print("\n6. Code formatting:")
    print("   black .")
    print("\n7. Type checking:")
    print("   mypy .")


def main():
    """Main setup function."""
    print("🔧 XiaoyaoSearch Backend Environment Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

    print(f"✓ Python version: {sys.version}")

    # Change to backend directory if not already there
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"✓ Working directory: {backend_dir}")

    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)

    # Install requirements
    install_requirements()

    # Setup pre-commit hooks
    setup_pre_commit()

    # Create .env file
    create_env_file()

    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()