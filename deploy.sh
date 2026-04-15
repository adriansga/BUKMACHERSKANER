#!/bin/bash
echo "🚀 Rozpoczynam automatyczny Deploy Skanera..."

# 1. Dodaj zmiany
git add .

# 2. Commit z datą
current_time=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto-deploy: $current_time"

# 3. Push na GitHub
git push origin main --force

echo "✅ Zmiany wypchnięte! Za chwilę GitHub i Vercel zaktualizują system."
