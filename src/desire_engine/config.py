"""Configuration for The Desire Engine.

Defines thresholds, model settings, and installation modes.
"""

from dataclasses import dataclass
from enum import Enum


class InstallationMode(Enum):
    """Installation modes as described in the concept."""

    ORACLE = "oracle"  # Confessional Oracle (recommended)
    TRIAL = "trial"  # Trial of Knowledge
    ASCETIC = "ascetic"  # Silent Ascetic Mode


@dataclass
class StateThresholds:
    """Thresholds for state transitions and end conditions."""

    # Liberation thresholds
    liberation_knowledge: float = 0.8  # Minimum knowledge for liberation
    liberation_desire: float = 0.2  # Maximum desire for liberation

    # Failure thresholds
    failure_desire: float = 0.9  # Desire level indicating failure
    stagnation_interactions: int = 30  # Interactions before checking stagnation

    # Update magnitudes (how much each interaction changes state)
    default_magnitude: float = 0.05
    silence_magnitude_per_second: float = 0.01  # How silence affects state


@dataclass
class VoiceConfig:
    """Voice I/O configuration."""

    # Speech-to-text
    whisper_model_size: str = "base"  # tiny, base, small, medium, large
    whisper_device: str = "cpu"  # cpu or cuda
    microphone_timeout: float = 10.0  # Seconds to wait for speech
    silence_duration: float = 2.0  # Seconds of silence before stopping

    # Text-to-speech
    speech_rate: int = 140  # Words per minute (slower = more deliberate)
    use_system_voice: bool | None = None  # Auto-detect (macOS uses 'say')
    pause_before_speech: float = 0.5  # Seconds
    pause_after_speech: float = 0.3  # Seconds


@dataclass
class LLMConfig:
    """Local LLM configuration."""

    model_name: str = "llama3"  # Ollama model name
    api_base: str = "http://localhost:11434"  # Ollama API endpoint
    temperature: float = 0.8  # Higher = more creative/varied
    max_tokens: int = 300  # Keep responses concise
    timeout: float = 30.0  # Seconds to wait for response


@dataclass
class EngineConfig:
    """Complete configuration for The Desire Engine."""

    mode: InstallationMode = InstallationMode.ORACLE
    thresholds: StateThresholds | None = None
    voice: VoiceConfig | None = None
    llm: LLMConfig | None = None

    # Session persistence
    save_session: bool = True
    session_file: str = ".desire_engine_session.json"

    # Logging
    verbose: bool = True  # Print state changes
    show_internal_state: bool = True  # Display state after each interaction

    def __post_init__(self):
        """Initialize nested configs if not provided."""
        if self.thresholds is None:
            self.thresholds = StateThresholds()
        if self.voice is None:
            self.voice = VoiceConfig()
        if self.llm is None:
            self.llm = LLMConfig()


# Default configurations for each mode
ORACLE_CONFIG = EngineConfig(
    mode=InstallationMode.ORACLE,
    thresholds=StateThresholds(
        liberation_knowledge=0.8,
        liberation_desire=0.2,
        failure_desire=0.9
    ),
    voice=VoiceConfig(
        speech_rate=140,
        silence_duration=3.0
    )
)

TRIAL_CONFIG = EngineConfig(
    mode=InstallationMode.TRIAL,
    thresholds=StateThresholds(
        liberation_knowledge=0.85,  # Harder to achieve
        liberation_desire=0.15,
        failure_desire=0.95
    ),
    voice=VoiceConfig(
        speech_rate=150,  # Slightly faster for Q&A
        silence_duration=2.0
    )
)

ASCETIC_CONFIG = EngineConfig(
    mode=InstallationMode.ASCETIC,
    thresholds=StateThresholds(
        liberation_knowledge=0.75,  # Easier through silence
        liberation_desire=0.25,
        failure_desire=0.85
    ),
    voice=VoiceConfig(
        speech_rate=120,  # Very slow, contemplative
        silence_duration=5.0,  # Longer silence periods
        pause_before_speech=1.0,
        pause_after_speech=0.8
    )
)


def get_config(mode: str = "oracle") -> EngineConfig:
    """Get configuration for a specific mode.

    Args:
        mode: Installation mode ("oracle", "trial", or "ascetic")

    Returns:
        EngineConfig for the specified mode
    """
    mode_lower = mode.lower()

    if mode_lower == "oracle":
        return ORACLE_CONFIG
    elif mode_lower == "trial":
        return TRIAL_CONFIG
    elif mode_lower == "ascetic":
        return ASCETIC_CONFIG
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'oracle', 'trial', or 'ascetic'.")
