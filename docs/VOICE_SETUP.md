# Voice Assistant Setup

## 🎤 Voice Features Added!

Your MediMate app now has voice capabilities:

### ✨ Features:
1. **Voice Questions** - Speak your prescription questions instead of typing
2. **Read Aloud** - Listen to AI responses (click 🔊 button)
3. **Voice Drug Search** - Search medications using voice
4. **Multi-language Support** - Works in Hindi, Tamil, Telugu, and all supported languages

### 📦 Installation:

Run this command to install voice packages:

```powershell
pip install gTTS SpeechRecognition pyaudio
```

**Note for Windows users:** 
If `pyaudio` installation fails, use this instead:

```powershell
pip install pipwin
pipwin install pyaudio
```

Or download the wheel file:
- Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Download the `.whl` file for Python 3.10
- Install: `pip install PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl`

### 🎯 How to Use:

#### 1. **Voice Questions** (Chat Interface)
- Click the 🎤 button next to the chat input
- Speak your question clearly
- The AI will respond, and you can click 🔊 to hear the answer

#### 2. **Voice Drug Search**
- Go to "Drug Information" page
- Click the 🎤 button next to search box
- Say the drug name you want to search

#### 3. **Read Aloud**
- Any AI response has a 🔊 button
- Click it to hear the response in your selected language

### 🌍 Language Support:
- English (en-US)
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Bengali (bn-IN)
- Marathi (mr-IN)
- Gujarati (gu-IN)
- Kannada (kn-IN)
- Malayalam (ml-IN)
- Punjabi (pa-IN)

### 🔧 Troubleshooting:

**Microphone not working?**
- Check Windows microphone permissions
- Settings > Privacy > Microphone > Allow apps to access

**No audio output?**
- Check browser audio permissions
- Make sure volume is not muted

**Voice recognition not accurate?**
- Speak clearly and slowly
- Reduce background noise
- Try switching to English if regional language isn't working well

### 🚀 Quick Start:

1. Install packages (see above)
2. Restart the app
3. Click 🎤 to start speaking!

**That's it!** Your medical assistant can now listen and speak!
