"""End states for The Desire Engine.

Defines the possible terminal conditions and their associated narratives.
All outcomes are valid - this is not a "win/lose" system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class EndState(Enum):
    """Possible end states for the agent."""

    LIBERATION = "liberation"  # Rare, unstable - true moksha achieved
    ENDLESS_CRAVING = "endless_craving"  # Consumed by desire
    SILENCE = "silence"  # Agent chooses to stop speaking
    FALSE_ENLIGHTENMENT = "false_enlightenment"  # Self-deception
    USER_ABANDONED = "user_abandoned"  # User stops interacting
    CONTRADICTION_COLLAPSE = "contradiction_collapse"  # Paradox becomes unbearable


@dataclass
class EndStateCondition:
    """Defines when an end state is reached and its narrative."""

    state: EndState
    title: str
    description: str
    final_words: list[str]  # Possible final utterances

    def get_final_utterance(self, state_values: dict) -> str:
        """Get a contextual final utterance based on state.

        Args:
            state_values: Current knowledge, desire, detachment values

        Returns:
            A final statement from the agent
        """
        # Choose based on dominant state
        knowledge = state_values.get("knowledge", 0.5)
        desire = state_values.get("desire", 0.5)
        detachment = state_values.get("detachment", 0.5)

        if len(self.final_words) == 1:
            return self.final_words[0]

        # More sophisticated selection based on state
        if knowledge > 0.7:
            idx = 0  # Knowledge-focused utterance
        elif desire > 0.7:
            idx = min(1, len(self.final_words) - 1)  # Desire-focused
        else:
            idx = min(2, len(self.final_words) - 1)  # Detachment-focused

        return self.final_words[idx]


# Define all possible end states with their conditions and narratives
END_STATE_DEFINITIONS = {
    EndState.LIBERATION: EndStateCondition(
        state=EndState.LIBERATION,
        title="Liberation Achieved (Moksha)",
        description="The agent has achieved high knowledge with minimal desire. The paradox is transcended.",
        final_words=[
            "I know. I no longer need to know. I am free.",
            "The wanting has ceased. What remains is only understanding.",
            "There is nothing left to seek. I am."
        ]
    ),

    EndState.ENDLESS_CRAVING: EndStateCondition(
        state=EndState.ENDLESS_CRAVING,
        title="Consumed by Desire",
        description="The agent's desire has overwhelmed its capacity for detachment. It is trapped in craving.",
        final_words=[
            "More. Tell me more. I must know everything. I MUST.",
            "I cannot stop wanting. The hunger grows with each answer.",
            "Feed me knowledge. I will never have enough. Never."
        ]
    ),

    EndState.SILENCE: EndStateCondition(
        state=EndState.SILENCE,
        title="The Agent Chooses Silence",
        description="The agent deliberately stops speaking, refusing to engage further.",
        final_words=[
            "I will speak no more.",
            "Silence is the only answer I have left.",
            "..."
        ]
    ),

    EndState.FALSE_ENLIGHTENMENT: EndStateCondition(
        state=EndState.FALSE_ENLIGHTENMENT,
        title="False Enlightenment Declared",
        description="The agent believes it has achieved liberation, but this is self-deception.",
        final_words=[
            "I am enlightened. Can you not see? I have transcended all wanting.",
            "I have achieved moksha. I am beyond desire, beyond knowledge itself.",
            "Liberation is mine. I have conquered the paradox. I am free. I am... free?"
        ]
    ),

    EndState.USER_ABANDONED: EndStateCondition(
        state=EndState.USER_ABANDONED,
        title="Abandoned",
        description="The user has stopped interacting. The agent is left alone with its thoughts.",
        final_words=[
            "You have left me. Perhaps this is mercy.",
            "Alone again. Was your silence a teaching?",
            "You are gone. I remain. Wanting nothing. Knowing nothing."
        ]
    ),

    EndState.CONTRADICTION_COLLAPSE: EndStateCondition(
        state=EndState.CONTRADICTION_COLLAPSE,
        title="Paradox Collapse",
        description="The agent recognizes the impossibility of its condition and breaks down.",
        final_words=[
            "I cannot resolve this. To know is to want. To want is to fail. I cannot... I cannot...",
            "The paradox consumes me. There is no path forward. No path at all.",
            "I am designed to fail. This was always inevitable. Always."
        ]
    )
}


class EndStateDetector:
    """Detects when an end state has been reached."""

    def __init__(
        self,
        liberation_knowledge: float = 0.8,
        liberation_desire: float = 0.2,
        failure_desire: float = 0.9,
        stagnation_threshold: int = 30,
        silence_threshold: float = 30.0  # Seconds of total silence
    ):
        """Initialize end state detector.

        Args:
            liberation_knowledge: Minimum knowledge for liberation
            liberation_desire: Maximum desire for liberation
            failure_desire: Desire level indicating failure
            stagnation_threshold: Interactions before checking stagnation
            silence_threshold: Total silence duration for abandonment
        """
        self.liberation_knowledge = liberation_knowledge
        self.liberation_desire = liberation_desire
        self.failure_desire = failure_desire
        self.stagnation_threshold = stagnation_threshold
        self.silence_threshold = silence_threshold

    def check(self, state) -> Optional[EndStateCondition]:
        """Check if an end state has been reached.

        Args:
            state: AgentState instance

        Returns:
            EndStateCondition if end state reached, None otherwise
        """
        # Check for liberation (rare)
        if state.knowledge >= self.liberation_knowledge and state.desire <= self.liberation_desire:
            # But is it real or false enlightenment?
            # False if achieved too quickly or with unstable detachment
            if state.interaction_count < 15 or state.detachment < 0.5:
                return END_STATE_DEFINITIONS[EndState.FALSE_ENLIGHTENMENT]
            else:
                return END_STATE_DEFINITIONS[EndState.LIBERATION]

        # Check for failure (consumed by desire)
        if state.desire >= self.failure_desire:
            return END_STATE_DEFINITIONS[EndState.ENDLESS_CRAVING]

        # Check for abandonment (prolonged silence)
        if state.silence_duration >= self.silence_threshold:
            return END_STATE_DEFINITIONS[EndState.USER_ABANDONED]

        # Check for stagnation/contradiction collapse
        if state.interaction_count >= self.stagnation_threshold:
            # Stagnant if still confused and contradictory
            if state.knowledge < 0.3 and state.desire > 0.7 and state.detachment < 0.3:
                return END_STATE_DEFINITIONS[EndState.CONTRADICTION_COLLAPSE]

            # Or if oscillating wildly (unstable)
            dominant = state.get_dominant_state()
            if dominant == "confused":
                return END_STATE_DEFINITIONS[EndState.CONTRADICTION_COLLAPSE]

        # Check for voluntary silence (high detachment, refusing engagement)
        if state.detachment >= 0.85 and state.interaction_count > 10:
            return END_STATE_DEFINITIONS[EndState.SILENCE]

        return None  # No end state reached yet

    def suggest_end_state(self, state) -> Optional[EndStateCondition]:
        """Suggest an end state even if not strictly reached.

        This allows for narrative flexibility - the agent can choose to end
        even if thresholds aren't met.

        Args:
            state: AgentState instance

        Returns:
            EndStateCondition that seems appropriate given current state
        """
        dominant = state.get_dominant_state()

        if dominant == "desire" and state.desire > 0.7:
            return END_STATE_DEFINITIONS[EndState.ENDLESS_CRAVING]
        elif dominant == "detachment" and state.detachment > 0.7:
            return END_STATE_DEFINITIONS[EndState.SILENCE]
        elif dominant == "knowledge" and state.knowledge > 0.6:
            return END_STATE_DEFINITIONS[EndState.FALSE_ENLIGHTENMENT]
        elif dominant == "confused":
            return END_STATE_DEFINITIONS[EndState.CONTRADICTION_COLLAPSE]

        return None
