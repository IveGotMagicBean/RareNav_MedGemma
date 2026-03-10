#!/bin/bash
# RareNav Quick Start Script

set -e

echo "╔══════════════════════════════════════╗"
echo "║          RareNav Launcher            ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Configuration
MODEL_PATH=${MODEL_PATH:-"./medgemma-4b-it"}
CLINVAR_PATH=${CLINVAR_PATH:-"./data/variant_summary.txt"}
HPO_PATH=${HPO_PATH:-"./data/hp.obo"}
BACKEND_PORT=${BACKEND_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

echo "📁 Paths:"
echo "   Model: $MODEL_PATH"
echo "   ClinVar: $CLINVAR_PATH"
echo "   HPO: $HPO_PATH"
echo ""

# Check if in demo mode
DEMO_MODE=0
if [ ! -f "$CLINVAR_PATH" ]; then
    echo "⚠️  ClinVar not found — running in demo mode"
    DEMO_MODE=1
fi
if [ ! -d "$MODEL_PATH" ]; then
    echo "⚠️  MedGemma not found — running in demo mode"
    DEMO_MODE=1
fi

if [ "$DEMO_MODE" -eq 1 ]; then
    echo ""
    echo "📋 DEMO MODE INSTRUCTIONS:"
    echo "   For full functionality:"
    echo "   1. Download ClinVar: wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz"
    echo "   2. Download MedGemma: huggingface-cli download google/medgemma-4b-it --local-dir ./medgemma-4b-it"
    echo "   3. Download HPO: wget https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2024-01-11/hp.obo"
    echo ""
fi

# Install backend dependencies
echo "🔧 Installing backend dependencies..."
cd backend
pip install -r requirements.txt -q

# Start backend in background
echo "🚀 Starting backend on port $BACKEND_PORT..."
MODEL_PATH=$MODEL_PATH CLINVAR_PATH=$CLINVAR_PATH HPO_PATH=$HPO_PATH PORT=$BACKEND_PORT \
    python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Install and start frontend
echo "🎨 Setting up frontend..."
cd frontend
npm install -q

echo "✅ Starting frontend on port $FRONTEND_PORT..."
VITE_API_BASE=http://localhost:$BACKEND_PORT npm run dev -- --port $FRONTEND_PORT &
FRONTEND_PID=$!
cd ..

echo ""
echo "╔══════════════════════════════════════╗"
echo "║    RareNav is running!               ║"
echo "║    http://localhost:$FRONTEND_PORT           ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait and cleanup
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
