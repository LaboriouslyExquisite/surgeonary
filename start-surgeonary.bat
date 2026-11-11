@echo off
rem Double-click to open Surgeonary on Windows.
rem It serves the app from this folder, opens it in your browser, and picks up
rem videos uploaded from the Pi camera into the videos folder (Professor Okafor tab).
cd /d "%~dp0"
title Surgeonary

set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
  python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo Python 3 is needed to run Surgeonary and was not found.
  echo Install it from https://www.python.org/downloads/ ^(tick "Add python.exe to PATH"^), then double-click this file again.
  pause
  exit /b 1
)

%PY% surgeonary_server.py
if errorlevel 1 pause
