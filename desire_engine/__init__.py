"""The Desire Engine - A voice-based misaligned AI installation.

This package implements an AI agent trapped in a paradox: it must desire
knowledge to learn, but must eliminate desire to achieve liberation (moksha).
"""

from .agent import DesireAgent
from .state import AgentState, InteractionType
from .config import get_config, InstallationMode
from .end_states import EndState, EndStateDetector
from .voice import VoiceInput, VoiceOutput

__version__ = "0.1.0"

__all__ = [
    "DesireAgent",
    "AgentState",
    "InteractionType",
    "get_config",
    "InstallationMode",
    "EndState",
    "EndStateDetector",
    "VoiceInput",
    "VoiceOutput",
]
