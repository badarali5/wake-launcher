from logging import config
import platform
import subprocess
import time
import json
import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer
import webbrowser
import logging
logging.basicConfig(
    filename="jarvis.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)



class WakeClapLauncher:

    def __init__(self):
        self.os_type = platform.system()
        self.sample_rate = 16000
        self.chunk_size = 1024

        self.model = Model("vosk-model-small-en-us-0.15")
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

        self.clap_threshold = 10
        self.clap_cooldown = 0.3
        with open("commands.json") as f:
            self.commands = json.load(f)



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
        for key, config in self.commands.items():
            if key in text:
                logging.info("Wake word detected")
                if self.listen_for_claps():
                    self.execute_command(config)
                return


        print("Unknown command.")


    # ---------------- ACTIONS ----------------

    def execute_command(self, config):
        cmd_type = config["type"]

        if cmd_type == "browser":
            webbrowser.open(config["value"])

        elif cmd_type == "classroom":
            subprocess.Popen([config["value"]])

        elif cmd_type == "shutdown":
            subprocess.Popen(["shutdown", "/s", "/t", str(config["value"])])
    

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
