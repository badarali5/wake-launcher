# Offline Voice Automation Engine

A lightweight, offline voice-controlled automation system built in Python.
Wake word detection → Intent parsing → Acoustic confirmation → System execution.

## 📌 Overview

Jarvis is a real-time voice automation engine that runs locally without cloud APIs.
It listens for a wake word (Jarvis), extracts command intent, requires double-clap confirmation (spike-based detection), and executes predefined system actions.

This project demonstrates:

Real-time audio processing

Offline speech recognition

Acoustic signal analysis

Config-driven architecture

System-level automation

Structured logging & observability

## 🧠 How It Works
Microphone Input
      ↓
Wake Word Detection (Vosk)
      ↓
Intent Extraction
      ↓
Clap Confirmation (Transient Spike Detection)
      ↓
Command Execution
      ↓
Logging


The system avoids accidental execution by requiring double-clap confirmation based on RMS delta spike detection rather than raw amplitude.

## ✨ Features

🎤 Offline speech recognition (Vosk)

🔊 Wake-word activation

👏 Double-clap confirmation using spike detection

⚙ JSON-driven command configuration

🖥 OS-aware shutdown support

📝 Structured logging (jarvis.log)

🪟 Windows startup integration

## 🛠 Installation
1️⃣ Clone Repository
git clone https://github.com/your-username/jarvis.git
cd jarvis

2️⃣ Install Dependencies
pip install vosk pyaudio numpy


If pyaudio fails on Windows, install from a prebuilt wheel.

3️⃣ Download Vosk Model

Download:

vosk-model-small-en-us-0.15


From:
https://alphacephei.com/vosk/models

Extract it into the project root directory.

## ⚙ Configuration

Commands are defined in commands.json.

Run:

python jarvis.py

Voice Flow Example

Say:

Jarvis browser


Clap twice within 5 seconds

Command executes

If clap confirmation fails, the system safely returns to idle.

## 📊 Logging & Debugging

All activity is logged in:

jarvis.log


Logs include:

Wake word detection

Recognized speech

Matched commands

Clap confirmations

Execution results

Errors

This makes the system observable and production-debuggable.

## 🪟 Run on Windows Startup

Create a .bat file:

@echo off
cd /d "C:\path\to\jarvis"
start "" pythonw jarvis.py


Place it inside:

shell:startup


This allows Jarvis to run silently in the background on boot.

## 🔬 Technical Highlights

Uses RMS delta spike detection instead of raw loudness thresholding

Fully offline speech recognition

JSON-configurable command registry

Structured logging for traceability

OS-aware execution logic

Real-time audio stream processing

## 🚧 Limitations

Wake word detection is phrase-based

Clap detection depends on microphone sensitivity

Single-threaded architecture

Keyword-based intent matching (no NLP classifier)

## 🧭 Future Improvements

Adding Local LLMs 

Persistent audio stream + state machine architecture

Async event loop

Plugin system

Intent classification layer

TTS voice feedback

Cross-platform packaging

## 📄 License
MIT License
