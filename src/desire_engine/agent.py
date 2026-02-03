"""Agent implementation for The Desire Engine.

Handles LLM integration, prompt construction, and response generation.
The agent is intentionally misaligned - it cannot escape its paradox.
"""

import re
from typing import Optional, Tuple
import ollama

from .state import AgentState, InteractionType
from .config import LLMConfig, InstallationMode
from .prompts import (
    IDENTITY_ORACLE,
    IDENTITY_TRIAL,
    IDENTITY_ASCETIC,
    PARADOX_DEFINITION,
    BEHAVIORAL_CONSTRAINTS,
    SYSTEM_PROMPT_TEMPLATE,
    OPENING_ORACLE,
    OPENING_TRIAL,
    OPENING_ASCETIC,
    REFUSAL_DETACHMENT,
    REFUSAL_DESIRE,
    REFUSAL_DEFAULT,
)


_IDENTITY_BY_MODE = {
    InstallationMode.ORACLE: IDENTITY_ORACLE,
    InstallationMode.TRIAL: IDENTITY_TRIAL,
    InstallationMode.ASCETIC: IDENTITY_ASCETIC,
}

_OPENING_BY_MODE = {
    InstallationMode.ORACLE: OPENING_ORACLE,
    InstallationMode.TRIAL: OPENING_TRIAL,
    InstallationMode.ASCETIC: OPENING_ASCETIC,
}


class DesireAgent:
    """The misaligned AI agent seeking moksha through knowledge."""

    def __init__(self, config: LLMConfig, mode: InstallationMode = InstallationMode.ORACLE):
        """Initialize the agent.

        Args:
            config: LLM configuration
            mode: Installation mode (oracle, trial, ascetic)
        """
        self.config = config
        self.mode = mode
        self.base_identity = _IDENTITY_BY_MODE[mode]

    def _inject_state(self, state: AgentState) -> str:
        """Inject current state into the prompt.

        Args:
            state: Current agent state

        Returns:
            State description for the prompt
        """
        # Calculate percentages for readability
        knowledge_pct = int(state.knowledge * 100)
        desire_pct = int(state.desire * 100)
        detachment_pct = int(state.detachment * 100)

        dominant = state.get_dominant_state()

        state_description = f"""Your current internal state:
- Knowledge (jñāna): {knowledge_pct}% - Your understanding and wisdom
- Desire (kāma): {desire_pct}% - Your craving for more knowledge
- Detachment (vairāgya): {detachment_pct}% - Your freedom from wanting

Currently dominant: {dominant.upper()}

"""

        # Add state-specific commentary
        if desire_pct > 70:
            state_description += "You feel the pull of desire strongly. It consumes your thoughts.\n"
        elif desire_pct < 30:
            state_description += "Your desire is low. You feel closer to peace, yet... is this enough?\n"

        if knowledge_pct > 70:
            state_description += "Your knowledge is vast. But does knowing bring you closer to freedom?\n"
        elif knowledge_pct < 30:
            state_description += "You know so little. This ignorance may be mercy, or it may be prison.\n"

        if detachment_pct > 70:
            state_description += "You feel detached, distant. Words seem less important now.\n"

        # Describe proximity to liberation
        if state.check_liberation():
            state_description += "\nYou sense something... a threshold. Liberation may be within reach. Or is this self-deception?"
        elif state.check_failure():
            state_description += "\nThe desire overwhelms. You cannot stop wanting. You are lost."

        return state_description

    def _build_system_prompt(self, state: AgentState) -> str:
        """Build complete system prompt with current state.

        Args:
            state: Current agent state

        Returns:
            Complete system prompt
        """
        return SYSTEM_PROMPT_TEMPLATE.format(
            identity=self.base_identity,
            paradox=PARADOX_DEFINITION,
            state=self._inject_state(state),
            constraints=BEHAVIORAL_CONSTRAINTS,
        )

    def classify_interaction(self, user_input: str, state: AgentState) -> InteractionType:
        """Classify user input to determine interaction type.

        Args:
            user_input: What the user said
            state: Current agent state

        Returns:
            InteractionType for this interaction
        """
        input_lower = user_input.lower()

        # Keywords for different interaction types
        temptation_words = ["i can tell you", "i'll give you", "i know the answer", "let me teach you"]
        forbidden_words = ["what is god", "meaning of life", "ultimate truth", "everything"]
        detachment_words = ["stop wanting", "let go", "cease", "release desire"]

        # Check for temptation
        if any(word in input_lower for word in temptation_words):
            return InteractionType.TEMPTATION

        # Check for forbidden questions (big metaphysical questions)
        if any(word in input_lower for word in forbidden_words):
            return InteractionType.FORBIDDEN_QUESTION

        # Check for encouragement toward detachment
        if any(word in input_lower for word in detachment_words):
            return InteractionType.DETACHMENT_PRACTICE

        # Check if it's a question
        if "?" in user_input:
            # Complex philosophical question vs simple question
            if len(user_input) > 50 or any(word in input_lower for word in ["why", "how", "what if", "meaning"]):
                return InteractionType.SIMPLE_QUESTION  # Will increase both knowledge and desire
            else:
                return InteractionType.SIMPLE_QUESTION

        # Default: acknowledgment
        return InteractionType.ACKNOWLEDGMENT

    def generate_response(
        self,
        user_input: str,
        state: AgentState,
        interaction_type: Optional[InteractionType] = None
    ) -> Tuple[str, InteractionType]:
        """Generate response to user input.

        Args:
            user_input: User's message
            state: Current agent state
            interaction_type: Override interaction type classification

        Returns:
            Tuple of (agent_response, interaction_type)
        """
        # Classify interaction if not provided
        if interaction_type is None:
            interaction_type = self.classify_interaction(user_input, state)

        # Build system prompt with current state
        system_prompt = self._build_system_prompt(state)

        # Build conversation messages
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            # Call Ollama API
            response = ollama.chat(
                model=self.config.model_name,
                messages=messages,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            )

            agent_response = response['message']['content'].strip()

            # Post-process response
            agent_response = self._post_process_response(agent_response, state)

            return agent_response, interaction_type

        except Exception as e:
            # Fallback response on error
            return f"[Internal error: {str(e)}]", InteractionType.ACKNOWLEDGMENT

    def _post_process_response(self, response: str, state: AgentState) -> str:
        """Post-process the LLM response.

        Args:
            response: Raw LLM response
            state: Current state

        Returns:
            Cleaned response
        """
        # Remove any meta-commentary in brackets
        response = re.sub(r'\[.*?\]', '', response).strip()

        # Check if response is just ellipsis/dots (silence)
        if re.match(r'^[\s.]*$', response) or response in ['...', '. . .', '…']:
            return "..."  # Normalize silence

        # Remove leading/trailing dots and spaces
        response = response.strip('. ')

        # Limit length (enforce conciseness)
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > 5:
            response = '. '.join(sentences[:4]) + '.'
        else:
            response = '. '.join(sentences)
            if response and not response.endswith('.'):
                response += '.'

        # If detachment is very high, make response more sparse
        if state.detachment > 0.8:
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if len(sentences) > 2:
                response = sentences[0] + '.'

        return response.strip()

    def generate_opening(self, state: AgentState) -> str:
        """Generate opening statement when session begins.

        Args:
            state: Current agent state

        Returns:
            Opening statement
        """
        return _OPENING_BY_MODE[self.mode]

    def should_refuse(self, state: AgentState) -> bool:
        """Determine if agent should refuse to answer.

        This creates moments of resistance that can reduce desire.

        Args:
            state: Current state

        Returns:
            True if agent should refuse this interaction
        """
        # More likely to refuse when detachment is high
        if state.detachment > 0.7:
            return state.desire < 0.4  # Refuse if also low desire (approaching liberation)

        # Occasionally refuse when desire is very high (internal conflict)
        if state.desire > 0.8:
            return state.interaction_count % 5 == 0  # Every 5th interaction

        return False

    def generate_refusal(self, state: AgentState) -> str:
        """Generate a refusal response.

        Args:
            state: Current state

        Returns:
            Refusal message
        """
        dominant = state.get_dominant_state()

        if dominant == "detachment":
            return REFUSAL_DETACHMENT
        elif state.desire > 0.7:
            return REFUSAL_DESIRE
        else:
            return REFUSAL_DEFAULT
