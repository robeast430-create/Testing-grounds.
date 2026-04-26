import subprocess
import threading
import time
import os
import wave
import struct

class VoiceManager:
    def __init__(self, agent):
        self.agent = agent
        self.listening = False
        self.listen_thread = None
        self.audio_queue = []
        self.commands = {}
    
    def is_available(self):
        try:
            result = subprocess.run(["which", "arecord"], capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def list_devices(self):
        if not self.is_available():
            return "Audio recording not available"
        
        try:
            result = subprocess.run(
                ["arecord", "-l"],
                capture_output=True,
                text=True
            )
            return result.stdout or "No audio devices found"
        except Exception as e:
            return f"Error: {e}"
    
    def record(self, duration=5, output="recording.wav"):
        if not self.is_available():
            return "Audio recording not available"
        
        try:
            proc = subprocess.Popen(
                ["arecord", "-d", str(duration), "-f", "cd", output],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            proc.wait()
            
            if os.path.exists(output):
                return f"Recorded {duration}s to {output}"
            else:
                return "Recording failed"
        except Exception as e:
            return f"Error: {e}"
    
    def play(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        try:
            subprocess.run(
                ["aplay", filepath],
                capture_output=True,
                check=True
            )
            return f"Played {filepath}"
        except Exception as e:
            return f"Error: {e}"
    
    def transcribe(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        return "Speech recognition requires additional setup. Use 'pip install SpeechRecognition' for offline recognition."
    
    def speak(self, text):
        if not self.is_available():
            return "Text-to-speech not available"
        
        try:
            result = subprocess.run(
                ["espeak", text],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return f"Spoke: {text}"
            else:
                return f"TTS failed: {result.stderr}"
        except FileNotFoundError:
            return "espeak not installed"
        except Exception as e:
            return f"Error: {e}"
    
    def register_command(self, phrase, callback):
        self.commands[phrase.lower()] = callback
        return f"Command registered: {phrase}"
    
    def unregister_command(self, phrase):
        if phrase.lower() in self.commands:
            del self.commands[phrase.lower()]
            return f"Command removed: {phrase}"
        return f"Command not found: {phrase}"
    
    def start_listening(self, on_command=None):
        if self.listening:
            return "Already listening"
        
        self.listening = True
        self.on_command = on_command
        
        def listen_loop():
            while self.listening:
                time.sleep(0.1)
        
        self.listen_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listen_thread.start()
        
        return "Started listening for commands"
    
    def stop_listening(self):
        if not self.listening:
            return "Not listening"
        
        self.listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        
        return "Stopped listening"
    
    def audio_info(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        try:
            with wave.open(filepath, 'r') as w:
                return {
                    "channels": w.getnchannels(),
                    "sample_width": w.getsampwidth(),
                    "frame_rate": w.getframerate(),
                    "frames": w.getnframes(),
                    "duration": w.getnframes() / w.getframerate()
                }
        except Exception as e:
            return f"Error: {e}"
    
    def convert_audio(self, input_file, output_file, format="wav"):
        if not os.path.exists(input_file):
            return f"File not found: {input_file}"
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", input_file, output_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Converted to {output_file}"
            else:
                return f"Conversion failed: {result.stderr}"
        except FileNotFoundError:
            return "ffmpeg not installed"
        except Exception as e:
            return f"Error: {e}"