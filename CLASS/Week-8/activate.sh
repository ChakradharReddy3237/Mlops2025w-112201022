#!/bin/bash
# Activation script for Week-8 virtual environment

cd /home/chakri/Documents/S-7/MLoPs/Mlops2025w-112201022/CLASS/Week-8

echo "════════════════════════════════════════════════════════════════"
echo "  Activating Week-8 Virtual Environment"
echo "════════════════════════════════════════════════════════════════"

source venv/bin/activate

echo "✓ Virtual environment activated!"
echo ""
echo "Installed packages:"
pip list | grep -E "(fastapi|uvicorn|wandb|scikit-learn|numpy|joblib)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Ready to work! You can now:"
echo "  • Run the FastAPI server: uvicorn app.main:app --reload"
echo "  • Test the API: python3 test_api.py"
echo "  • Deactivate: deactivate"
echo "════════════════════════════════════════════════════════════════"
echo ""
