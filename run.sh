#!/bin/bash

# Define the path to your virtual environment's activate script
venv_activate="venv/bin/activate"

# Check if the virtual environment activation script exists
if [ -f "$venv_activate" ]; then
    # Activate the virtual environment
    source "$venv_activate"

    # Run your Python script
    python main.py 
else
    echo "Virtual environment not found or activation script missing."
fi