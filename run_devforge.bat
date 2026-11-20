@echo off
title DevForge AI
cd /d "%~dp0"

:: Keep Ollama models on drive E: (as before)
if exist "E:\OllamaModels" set OLLAMA_MODELS=E:\OllamaModels

:: The app starts Ollama itself if it is not running.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m devforge
) else (
    python -m devforge
)
if errorlevel 1 pause
