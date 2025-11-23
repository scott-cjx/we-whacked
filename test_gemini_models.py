"""Test script to list available Gemini models."""

import google.generativeai as genai
import os
from pathlib import Path

# Load API key from .env
env_path = Path("src/backend/.env")
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY"):
                api_key = line.split("=")[1].strip().strip('"')
                genai.configure(api_key=api_key)
                break

print("Available Gemini models:")
print("-" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported: {', '.join(model.supported_generation_methods)}")
        print()