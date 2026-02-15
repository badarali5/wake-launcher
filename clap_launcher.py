import platform
import subprocess
import time
import json
import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer
import webbrowser


class WakeClapLauncher:

    def __init__(self):
        self.os_type = platform.system()
        self.sample_rate = 16000
        self.chunk_size = 1024

        self.model = Model("vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

        self.clap_threshold = 10
        self.clap_cooldown = 0.3
        self.commands = {
        "browser": self.open_browser,
        "classroom": self.open_classroom,
        "sleep": self.shutdown_system
        }


    # ---------------- LISTEN FOR FULL COMMAND ----------------

    def listen_for_command(self):
        print("Say: jarvis google / jarvis classroom / jarvis sleep")

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.sample_rate,
                         input=True,
                         frames_per_buffer=4000)

        stream.start_stream()

        while True:
            data = stream.read(4000, exception_on_overflow=False)

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower()
                print("Heard:", text)

                if "jarvis" in text:
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    self.recognizer.Reset()
                    return text

    # ---------------- CLAP CONFIRMATION ----------------

    def listen_for_claps(self, duration=5):
        print("Clap twice to confirm...")

        clap_count = 0
        last_clap_time = 0

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.sample_rate,
                         input=True,
                         frames_per_buffer=self.chunk_size)

        start_time = time.time()

        while time.time() - start_time < duration:
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16)

            rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
            current_time = time.time()

            if rms > self.clap_threshold:
                if current_time - last_clap_time > self.clap_cooldown:
                    clap_count += 1
                    last_clap_time = current_time
                    print(f"Clap detected ({clap_count})")

            if clap_count >= 2:
                stream.stop_stream()
                stream.close()
                pa.terminate()
                print("Confirmed.")
                return True

        stream.stop_stream()
        stream.close()
        pa.terminate()
        print("Clap timeout.")
        return False

    # ---------------- COMMAND HANDLER ----------------

    def handle_command(self, text):
        for key, action in self.commands.items():
            if key in text:
                if self.listen_for_claps():
                    action()
                return

        print("Unknown command.")


    # ---------------- ACTIONS ----------------

    def open_browser(self):
        print("Opening Google...")
        webbrowser.open("https://www.google.com")

    def open_classroom(self):
        print("Opening Google Classroom...")
        webbrowser.open("https://classroom.google.com/u/1/?pli=1")

    def shutdown_system(self):
        print("Shutting down in 5 seconds...")
        subprocess.Popen(["shutdown", "/s", "/t", "5"])

    # ---------------- MAIN LOOP ----------------

    def run(self):
        print("System ready...")

        while True:
            command_text = self.listen_for_command()
            self.handle_command(command_text)
            print("Returning to idle...\n")


if __name__ == "__main__":
    launcher = WakeClapLauncher()
    launcher.run()
