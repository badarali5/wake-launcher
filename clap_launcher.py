import platform
import subprocess
import time
import json
import numpy as np
import pyaudio
from vosk import Model, KaldiRecognizer
import webbrowser
import logging
import sys

# ---------------- LOGGING SETUP ----------------

logging.basicConfig(
    filename="jarvis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class WakeClapLauncher:

    def __init__(self):
        try:
            self.os_type = platform.system()
            self.sample_rate = 16000
            self.chunk_size = 1024

            logging.info("Initializing Vosk model...")
            self.model = Model("vosk-model-small-en-us-0.15")
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)

            # Clap detection tuning
            self.clap_spike_threshold = 3000
            self.clap_cooldown = 0.3

            # Load commands
            with open("commands.json") as f:
                self.commands = json.load(f)

            logging.info("System initialized successfully.")

        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            sys.exit(1)

    # ---------------- LISTEN FOR WAKE + COMMAND ----------------

    def listen_for_command(self):
        logging.info("Listening for wake word...")

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.sample_rate,
                         input=True,
                         frames_per_buffer=4000)

        stream.start_stream()

        try:
            while True:
                data = stream.read(4000, exception_on_overflow=False)

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()

                    if text:
                        logging.info(f"Heard: {text}")
                        print("Heard:", text)

                    if "jarvis" in text:
                        logging.info("Wake word detected.")
                        stream.stop_stream()
                        stream.close()
                        pa.terminate()
                        self.recognizer.Reset()
                        return text

        except Exception as e:
            logging.error(f"Error during command listening: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    # ---------------- CLAP CONFIRMATION ----------------

    def listen_for_claps(self, duration=5):
        logging.info("Waiting for clap confirmation...")

        clap_count = 0
        last_clap_time = 0
        previous_rms = 0

        pa = pyaudio.PyAudio()
        stream = pa.open(format=pyaudio.paInt16,
                         channels=1,
                         rate=self.sample_rate,
                         input=True,
                         frames_per_buffer=self.chunk_size)

        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)

                rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
                delta = rms - previous_rms
                previous_rms = rms

                current_time = time.time()

                # Detect sudden spike (clap-like transient)
                if delta > self.clap_spike_threshold:
                    if current_time - last_clap_time > self.clap_cooldown:
                        clap_count += 1
                        last_clap_time = current_time
                        logging.info(f"Clap detected ({clap_count})")
                        print(f"Clap detected ({clap_count})")

                if clap_count >= 2:
                    logging.info("Clap confirmation successful.")
                    return True

            logging.info("Clap confirmation timeout.")
            return False

        except Exception as e:
            logging.error(f"Error during clap detection: {e}")
            return False

        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()

    # ---------------- COMMAND HANDLER ----------------

    def handle_command(self, text):
        for keyword, config in self.commands.items():
            if keyword in text:
                logging.info(f"Command matched: {keyword}")

                confirmed = self.listen_for_claps()

                if confirmed:
                    self.execute_command(config)
                else:
                    logging.info("Command canceled due to missing clap confirmation.")

                return

        logging.info("Unknown command received.")
        print("Unknown command.")

    # ---------------- ACTION EXECUTION ----------------

    def execute_command(self, config):
        try:
            cmd_type = config["type"]
            value = config["value"]

            logging.info(f"Executing command type: {cmd_type}")

            if cmd_type == "browser":
                webbrowser.open(value)

            elif cmd_type == "program":
                subprocess.Popen([value])

            elif cmd_type == "shutdown":
                if self.os_type == "Windows":
                    subprocess.Popen(["shutdown", "/s", "/t", str(value)])
                elif self.os_type == "Linux":
                    subprocess.Popen(["shutdown", "-h", str(value)])
                else:
                    logging.warning("Unsupported OS for shutdown command.")

            logging.info("Command executed successfully.")

        except Exception as e:
            logging.error(f"Command execution failed: {e}")

    # ---------------- MAIN LOOP ----------------

    def run(self):
        print("System ready...")
        logging.info("Jarvis system started.")

        while True:
            command_text = self.listen_for_command()
            if command_text:
                self.handle_command(command_text)
                print("Returning to idle...\n")


if __name__ == "__main__":
    launcher = WakeClapLauncher()
    launcher.run()
