#!/usr/bin/env python3
"""Deployment validation script."""

import importlib
import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_required_files() -> List[Tuple[str, bool]]:
    """Check if all required files exist."""
    required_files = [
        "requirements.txt",
        "railway.toml",
        "Procfile",
        "app/main.py",
        "app/core/config.py",
        "app/core/logging_config.py",
    ]
    results = []
    for file in required_files:
        exists = Path(file).exists()
        results.append((file, exists))
    return results

def validate_imports() -> List[Tuple[str, bool]]:
    """Validate that all required packages can be imported."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "jinja2",
        "spotipy",
        "redis",
        "sentry_sdk",
    ]
    results = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            results.append((package, True))
        except ImportError:
            results.append((package, False))
    return results

def check_environment_variables() -> List[Tuple[str, bool]]:
    """Check if required environment variables are set."""
    required_vars = [
        "ENVIRONMENT",
        "SECRET_KEY",
        "_USE_HTTPS",
        "_ALLOWED_HOSTS",
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI",
    ]
    results = []
    for var in required_vars:
        exists = var in os.environ
        results.append((var, exists))
    return results

def main():
    """Run all validation checks."""
    print("🔍 Running deployment validation checks...")
    
    # Check required files
    print("\n📁 Checking required files:")
    file_results = check_required_files()
    for file, exists in file_results:
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
    
    # Check imports
    print("\n📦 Checking package imports:")
    import_results = validate_imports()
    for package, can_import in import_results:
        status = "✅" if can_import else "❌"
        print(f"{status} {package}")
    
    # Check environment variables
    print("\n🔐 Checking environment variables:")
    env_results = check_environment_variables()
    for var, exists in env_results:
        status = "✅" if exists else "❌"
        print(f"{status} {var}")
    
    # Check for failures
    all_results = file_results + import_results + env_results
    failures = [item for item, success in all_results if not success]
    
    if failures:
        print("\n❌ Validation failed! Please fix the following issues:")
        for item in failures:
            print(f"  - {item}")
        sys.exit(1)
    else:
        print("\n✅ All validation checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
