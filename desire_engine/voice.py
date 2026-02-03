"""Voice I/O for The Desire Engine.

Handles speech-to-text input and text-to-speech output with ritual pacing.
"""

import time
from typing import Optional
import speech_recognition as sr
from faster_whisper import WhisperModel
import pyttsx3
import platform


class VoiceInput:
    """Captures and transcribes voice input from microphone."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        silence_duration: float = 2.0,
        timeout: float = 10.0
    ):
        """Initialize voice input.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda)
            silence_duration: Seconds of silence before stopping recording
            timeout: Maximum seconds to wait for speech
        """
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.whisper_model = WhisperModel(model_size, device=device)
        self.silence_duration = silence_duration
        self.timeout = timeout

        # Adjust for ambient noise
        print("Calibrating for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Calibration complete.")

    def listen(self) -> Optional[str]:
        """Listen for voice input and transcribe it.

        Returns:
            Transcribed text, or None if silence/timeout
        """
        try:
            print("\n[Listening...]")

            with self.microphone as source:
                # Listen for speech
                audio = self.recognizer.listen(
                    source,
                    timeout=self.timeout,
                    phrase_time_limit=None
                )

            # Save audio to temporary file for Whisper
            audio_data = audio.get_wav_data()

            # Transcribe using faster-whisper
            # Note: faster-whisper expects file path or file-like object
            import io
            audio_file = io.BytesIO(audio_data)

            segments, info = self.whisper_model.transcribe(audio_file)

            # Combine all segments
            transcription = " ".join([segment.text for segment in segments])

            if transcription.strip():
                print(f"[Heard: {transcription}]")
                return transcription.strip()
            else:
                print("[Silence detected]")
                return None

        except sr.WaitTimeoutError:
            print("[Timeout - no speech detected]")
            return None
        except Exception as e:
            print(f"[Error in voice input: {e}]")
            return None

    def detect_silence(self, duration: float = 5.0) -> bool:
        """Check if there's prolonged silence.

        Args:
            duration: Seconds to wait for silence

        Returns:
            True if silence persisted, False if speech detected
        """
        try:
            with self.microphone as source:
                self.recognizer.listen(source, timeout=duration, phrase_time_limit=1)
            return False  # Speech was detected
        except sr.WaitTimeoutError:
            return True  # Silence persisted


class VoiceOutput:
    """Converts text to speech with adjustable pacing for ritual effect."""

    def __init__(
        self,
        rate: int = 150,  # Words per minute (slower than default ~200)
        use_system_voice: bool | None = None
    ):
        """Initialize voice output.

        Args:
            rate: Speech rate in words per minute (lower = slower, more deliberate)
            use_system_voice: Use macOS 'say' command if True, pyttsx3 if False.
                             Auto-detect if None.
        """
        self.rate = rate

        # Auto-detect: use 'say' on macOS, pyttsx3 elsewhere
        if use_system_voice is None:
            self.use_system_voice = platform.system() == "Darwin"
        else:
            self.use_system_voice = use_system_voice

        if not self.use_system_voice:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            # Use a more solemn voice if available
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find a deeper/more neutral voice
                self.engine.setProperty('voice', voices[0].id) # pyright: ignore[reportIndexIssue]

    def speak(self, text: str, pause_before: float = 0.5, pause_after: float = 0.3):
        """Speak text with deliberate pacing.

        Args:
            text: Text to speak
            pause_before: Seconds to pause before speaking
            pause_after: Seconds to pause after speaking
        """
        if not text.strip():
            return

        print(f"\n[Agent speaks: {text}]")

        # Pause before speaking (creates anticipation)
        time.sleep(pause_before)

        if self.use_system_voice:
            # Use macOS 'say' command with specific voice
            import subprocess
            # Alex is a clear, neutral voice on macOS
            # Adjust rate: 'say' uses different scale (words per minute)
            subprocess.run(
                ["say", "-v", "Alex", "-r", str(self.rate), text],
                check=False
            )
        else:
            # Use pyttsx3
            self.engine.say(text)
            self.engine.runAndWait()

        # Pause after speaking (ritual cadence)
        time.sleep(pause_after)

    def whisper(self, text: str):
        """Speak text more quietly/slowly for emphasis.

        This simulates a whispered, more intimate delivery.
        """
        # Reduce rate for whisper effect
        original_rate = self.rate
        self.rate = int(self.rate * 0.7)  # 30% slower

        if not self.use_system_voice:
            self.engine.setProperty('rate', self.rate)

        self.speak(text, pause_before=1.0, pause_after=0.5)

        # Restore rate
        self.rate = original_rate
        if not self.use_system_voice:
            self.engine.setProperty('rate', self.rate)

    def long_pause(self, duration: float = 2.0):
        """Create a deliberate silence (meaningful hesitation).

        Args:
            duration: Seconds of silence
        """
        print(f"\n[Silence: {duration}s]")
        time.sleep(duration)
