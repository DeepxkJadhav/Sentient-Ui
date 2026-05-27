import subprocess
import os

print("Building Sentient-UI Executable...")

# Use PyInstaller to create the executable
# --noconsole removes the command prompt window
# --onefile makes a single .exe
# --add-data includes the json files and modules
subprocess.run([
    "pyinstaller",
    "--noconsole",
    "--onefile",
    "--add-data", "theme.json;.",
    "--add-data", "config.json;.",
    "--hidden-import", "customtkinter",
    "--hidden-import", "websocket",
    "--collect-all", "customtkinter",
    "--name", "SentientUI",
    "main.py"
])

print("Build complete! Executable is in the 'dist' folder.")
