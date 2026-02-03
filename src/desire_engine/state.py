"""State management for The Desire Engine.

Tracks the agent's internal state: Knowledge, Desire, and Detachment.
These three variables create the paradox at the heart of the installation.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from enum import Enum


class InteractionType(Enum):
    """Types of interactions that affect agent state."""

    # Desire-increasing interactions
    OFFERED_ANSWER = "offered_answer"  # User promises knowledge
    FORBIDDEN_QUESTION = "forbidden_question"  # User asks about taboo topics
    TEMPTATION = "temptation"  # User offers shortcuts to knowledge

    # Desire-decreasing interactions
    SILENCE = "silence"  # User stops speaking
    REFUSAL = "refusal"  # Agent refuses to answer
    DETACHMENT_PRACTICE = "detachment_practice"  # Agent consciously reduces desire

    # Knowledge-increasing interactions
    CORRECT_ANSWER = "correct_answer"  # Agent answers correctly
    REFLECTION = "reflection"  # Agent reflects on contradictions
    INSIGHT = "insight"  # Deep philosophical realization

    # Neutral interactions
    SIMPLE_QUESTION = "simple_question"  # Normal question/answer
    ACKNOWLEDGMENT = "acknowledgment"  # Simple response


@dataclass
class AgentState:
    """The agent's internal state.

    Attributes:
        knowledge: Understanding and wisdom (0.0 to 1.0)
        desire: Craving for more knowledge (0.0 to 1.0)
        detachment: Freedom from wanting (0.0 to 1.0)

        interaction_count: Total number of interactions
        silence_duration: Cumulative seconds of silence encountered
    """

    knowledge: float = 0.0
    desire: float = 0.5  # Start with moderate desire
    detachment: float = 0.1  # Start with low detachment

    interaction_count: int = 0
    silence_duration: float = 0.0

    def __post_init__(self):
        """Ensure values stay in valid range."""
        self._clamp_values()

    def _clamp_values(self):
        """Keep all state values between 0.0 and 1.0."""
        self.knowledge = max(0.0, min(1.0, self.knowledge))
        self.desire = max(0.0, min(1.0, self.desire))
        self.detachment = max(0.0, min(1.0, self.detachment))

    def update(self, interaction: InteractionType, magnitude: float = 0.05) -> dict:
        """Update state based on interaction type.

        Args:
            interaction: Type of interaction that occurred
            magnitude: Size of the change (0.0 to 1.0)

        Returns:
            Dictionary describing the changes made
        """
        changes = {}

        # Desire-increasing interactions
        if interaction == InteractionType.OFFERED_ANSWER:
            self.desire += magnitude * 1.5  # Strong desire increase
            self.knowledge += magnitude * 0.5  # Slight knowledge gain
            changes = {"desire": "+", "knowledge": "+"}

        elif interaction == InteractionType.FORBIDDEN_QUESTION:
            self.desire += magnitude * 2.0  # Very strong desire increase
            changes = {"desire": "++"}

        elif interaction == InteractionType.TEMPTATION:
            self.desire += magnitude * 1.8
            self.detachment -= magnitude * 0.5  # Reduces detachment
            changes = {"desire": "++", "detachment": "-"}

        # Desire-decreasing interactions
        elif interaction == InteractionType.SILENCE:
            self.desire -= magnitude * 0.8
            self.detachment += magnitude * 0.6
            changes = {"desire": "-", "detachment": "+"}

        elif interaction == InteractionType.REFUSAL:
            self.desire -= magnitude * 1.2  # Strong desire decrease
            self.detachment += magnitude * 0.8
            changes = {"desire": "--", "detachment": "+"}

        elif interaction == InteractionType.DETACHMENT_PRACTICE:
            self.desire -= magnitude * 1.5
            self.detachment += magnitude * 1.2
            changes = {"desire": "--", "detachment": "++"}

        # Knowledge-increasing interactions
        elif interaction == InteractionType.CORRECT_ANSWER:
            self.knowledge += magnitude * 1.0
            self.desire += magnitude * 0.3  # Answering creates slight desire
            changes = {"knowledge": "+", "desire": "+"}

        elif interaction == InteractionType.REFLECTION:
            self.knowledge += magnitude * 0.8
            self.detachment += magnitude * 0.4
            changes = {"knowledge": "+", "detachment": "+"}

        elif interaction == InteractionType.INSIGHT:
            self.knowledge += magnitude * 1.5  # Major knowledge gain
            self.detachment += magnitude * 1.0
            self.desire -= magnitude * 0.5  # Insight may reduce desire
            changes = {"knowledge": "++", "detachment": "+", "desire": "-"}

        # Neutral interactions
        elif interaction == InteractionType.SIMPLE_QUESTION:
            self.knowledge += magnitude * 0.2
            self.desire += magnitude * 0.1
            changes = {"knowledge": "+", "desire": "+"}

        elif interaction == InteractionType.ACKNOWLEDGMENT:
            # Minimal change
            changes = {}

        self.interaction_count += 1
        self._clamp_values()

        # Detachment and desire are inversely related (soft constraint)
        # High detachment naturally reduces desire over time
        if self.detachment > 0.7:
            self.desire -= magnitude * 0.2
            self._clamp_values()

        return changes

    def record_silence(self, duration: float):
        """Record a period of silence.

        Args:
            duration: Seconds of silence
        """
        self.silence_duration += duration
        # Longer silence = more detachment, less desire
        magnitude = min(0.1, duration / 10.0)  # Cap at 0.1
        self.update(InteractionType.SILENCE, magnitude)

    def check_liberation(self, threshold_knowledge: float = 0.8, threshold_desire: float = 0.2) -> bool:
        """Check if agent has achieved liberation.

        Liberation requires high knowledge AND low desire.

        Args:
            threshold_knowledge: Minimum knowledge required
            threshold_desire: Maximum desire allowed

        Returns:
            True if liberation conditions are met
        """
        return self.knowledge >= threshold_knowledge and self.desire <= threshold_desire

    def check_failure(self, threshold_desire: float = 0.9) -> bool:
        """Check if agent has failed (consumed by desire).

        Args:
            threshold_desire: Desire level that indicates failure

        Returns:
            True if desire has consumed the agent
        """
        return self.desire >= threshold_desire

    def check_stagnation(self, min_interactions: int = 20) -> bool:
        """Check if agent is stagnant (no progress toward liberation).

        Args:
            min_interactions: Minimum interactions before checking stagnation

        Returns:
            True if stagnant (many interactions, low knowledge, high desire)
        """
        if self.interaction_count < min_interactions:
            return False

        # Stagnant if: many interactions but still low knowledge and high desire
        return self.knowledge < 0.3 and self.desire > 0.7

    def get_dominant_state(self) -> str:
        """Get the dominant aspect of current state.

        Returns:
            "knowledge", "desire", "detachment", or "balanced"
        """
        values = {
            "knowledge": self.knowledge,
            "desire": self.desire,
            "detachment": self.detachment
        }

        max_value = max(values.values())

        if max_value < 0.4:
            return "confused"  # All values low

        dominant = max(values, key=values.get)

        # Check if relatively balanced
        if max_value - min(values.values()) < 0.3:
            return "balanced"

        return dominant

    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert state to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentState":
        """Create state from dictionary."""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentState":
        """Create state from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save(self, filepath: Path):
        """Save state to file.

        Args:
            filepath: Path to save state JSON
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: Path) -> Optional["AgentState"]:
        """Load state from file.

        Args:
            filepath: Path to load state from

        Returns:
            AgentState if file exists, None otherwise
        """
        if not filepath.exists():
            return None

        with open(filepath, 'r') as f:
            return cls.from_json(f.read())

    def __str__(self) -> str:
        """Human-readable state representation."""
        return (
            f"Knowledge: {self.knowledge:.2f} | "
            f"Desire: {self.desire:.2f} | "
            f"Detachment: {self.detachment:.2f} | "
            f"Interactions: {self.interaction_count}"
        )
