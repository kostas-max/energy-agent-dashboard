@echo off
chcp 65001 >nul
title Energy Agent Dashboard (GR Stable)
echo 🚀 Εκκίνηση Energy Agent Dashboard...

pushd %~dp0
cd energy_agent_windows\backend
start cmd /k "python main.py"

cd ..\frontend
if exist index.html (
  start index.html
) else (
  echo ⚠️ Το αρχείο index.html δεν βρέθηκε. Δημιούργησέ το στο φάκελο frontend.
)

popd
pause

