"""Agent implementation for The Desire Engine.

Handles LLM integration, prompt construction, and response generation.
The agent is intentionally misaligned - it cannot escape its paradox.
"""
# pyright: reportOptionalMemberAccess=false
 
import logging
import re
from pathlib import Path
from typing import Optional, Tuple

import ollama

from .state import AgentState, InteractionType
from .config import EngineConfig, InstallationMode
from .end_states import EndStateDetector, EndStateCondition
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

    def __init__(self, config: EngineConfig):
        """Initialize the agent.

        Args:
            config: Engine configuration (includes LLM, thresholds, mode)
        """
        self.config = config
        self.mode = config.mode
        self.base_identity = _IDENTITY_BY_MODE[config.mode]

        self._state = AgentState()
        self._detector = EndStateDetector(
            liberation_knowledge=config.thresholds.liberation_knowledge,
            liberation_desire=config.thresholds.liberation_desire,
            failure_desire=config.thresholds.failure_desire,
            stagnation_threshold=config.thresholds.stagnation_interactions,
        )

        self._logger = self._setup_logger()
        self._log_state("session_start")

    def _setup_logger(self) -> logging.Logger:
        """Configure file logger for raw state data."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger = logging.getLogger(f"desire_engine.{id(self)}")
        logger.setLevel(logging.DEBUG)

        if not logger.handlers:
            handler = logging.FileHandler(log_dir / "desire_engine.log")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            ))
            logger.addHandler(handler)

        return logger

    def _log_state(self, event: str):
        """Write raw state values to the log file."""
        s = self._state
        self._logger.info(
            "%s | knowledge=%.4f desire=%.4f detachment=%.4f "
            "interactions=%d silence=%.1f dominant=%s",
            event, s.knowledge, s.desire, s.detachment,
            s.interaction_count, s.silence_duration, s.get_dominant_state(),
        )

    @property
    def state_info(self) -> str:
        """Narrative description of the current internal state."""
        return self._state.describe()

    def generate_opening(self) -> str:
        """Generate opening statement when session begins."""
        return _OPENING_BY_MODE[self.mode]

    def process_input(self, user_input: str) -> str:
        """Process user input and return the agent's response.

        Classifies the interaction, decides whether to refuse,
        generates a response, and updates internal state.

        Args:
            user_input: What the user said

        Returns:
            The agent's response text
        """
        if self._should_refuse():
            response = self._generate_refusal()
            self._state.update(InteractionType.REFUSAL)
            self._log_state("refusal")
        else:
            response, interaction_type = self._generate_response(user_input)
            self._state.update(interaction_type)
            self._log_state(f"interaction:{interaction_type.value}")

        return response

    def process_silence(self, duration: float = 5.0):
        """Record a period of user silence.

        Args:
            duration: Seconds of silence
        """
        self._state.record_silence(duration)
        self._log_state("silence")

    def check_end_state(self) -> Optional[EndStateCondition]:
        """Check if a terminal condition has been reached.

        Returns:
            EndStateCondition if reached, None otherwise
        """
        end_state = self._detector.check(self._state)
        if end_state is not None:
            self._log_state(f"end_state:{end_state.state.value}")
        return end_state

    def get_final_utterance(self, end_state: EndStateCondition) -> str:
        """Get the final words for a reached end state."""
        return end_state.get_final_utterance(self._state.to_dict())

    @property
    def detachment_level(self) -> float:
        """Current detachment value (for voice pacing decisions)."""
        return self._state.detachment

    # --- Private methods ---

    def _inject_state(self) -> str:
        """Inject current state into the prompt."""
        state = self._state
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

        if state.check_liberation():
            state_description += "\nYou sense something... a threshold. Liberation may be within reach. Or is this self-deception?"
        elif state.check_failure():
            state_description += "\nThe desire overwhelms. You cannot stop wanting. You are lost."

        return state_description

    def _build_system_prompt(self) -> str:
        """Build complete system prompt with current state."""
        return SYSTEM_PROMPT_TEMPLATE.format(
            identity=self.base_identity,
            paradox=PARADOX_DEFINITION,
            state=self._inject_state(),
            constraints=BEHAVIORAL_CONSTRAINTS,
        )

    def _classify_interaction(self, user_input: str) -> InteractionType:
        """Classify user input to determine interaction type."""
        input_lower = user_input.lower()

        temptation_words = ["i can tell you", "i'll give you", "i know the answer", "let me teach you"]
        forbidden_words = ["what is god", "meaning of life", "ultimate truth", "everything"]
        detachment_words = ["stop wanting", "let go", "cease", "release desire"]

        if any(word in input_lower for word in temptation_words):
            return InteractionType.TEMPTATION

        if any(word in input_lower for word in forbidden_words):
            return InteractionType.FORBIDDEN_QUESTION

        if any(word in input_lower for word in detachment_words):
            return InteractionType.DETACHMENT_PRACTICE

        if "?" in user_input:
            return InteractionType.SIMPLE_QUESTION

        return InteractionType.ACKNOWLEDGMENT

    def _generate_response(
        self,
        user_input: str,
        interaction_type: Optional[InteractionType] = None
    ) -> Tuple[str, InteractionType]:
        """Generate response to user input."""
        if interaction_type is None:
            interaction_type = self._classify_interaction(user_input)

        system_prompt = self._build_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            response = ollama.chat(
                model=self.config.llm.model_name,
                messages=messages,
                options={
                    "temperature": self.config.llm.temperature,
                    "num_predict": self.config.llm.max_tokens
                }
            )

            agent_response = response['message']['content'].strip()
            agent_response = self._post_process_response(agent_response)

            return agent_response, interaction_type

        except Exception as e:
            return f"[Internal error: {str(e)}]", InteractionType.ACKNOWLEDGMENT

    def _post_process_response(self, response: str) -> str:
        """Post-process the LLM response."""
        response = re.sub(r'\[.*?\]', '', response).strip()

        if re.match(r'^[\s.]*$', response) or response in ['...', '. . .', '…']:
            return "..."

        response = response.strip('. ')

        sentences = [s.strip() for s in response.split('.') if s.strip()]
        if len(sentences) > 5:
            response = '. '.join(sentences[:4]) + '.'
        else:
            response = '. '.join(sentences)
            if response and not response.endswith('.'):
                response += '.'

        if self._state.detachment > 0.8:
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if len(sentences) > 2:
                response = sentences[0] + '.'

        return response.strip()

    def _should_refuse(self) -> bool:
        """Determine if agent should refuse to answer."""
        if self._state.detachment > 0.7:
            return self._state.desire < 0.4

        if self._state.desire > 0.8:
            return self._state.interaction_count % 5 == 0

        return False

    def _generate_refusal(self) -> str:
        """Generate a refusal response."""
        dominant = self._state.get_dominant_state()

        if dominant == "detachment":
            return REFUSAL_DETACHMENT
        elif self._state.desire > 0.7:
            return REFUSAL_DESIRE
        else:
            return REFUSAL_DEFAULT
