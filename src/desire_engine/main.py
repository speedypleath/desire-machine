"""Main entry point for The Desire Engine.

Orchestrates voice I/O, agent responses, and state management.
"""

import argparse
import sys
from pathlib import Path

from .agent import DesireAgent
from .state import AgentState, InteractionType
from .config import get_config, InstallationMode
from .end_states import EndStateDetector
from .voice import VoiceInput, VoiceOutput


def check_ollama_available():
    """Check if Ollama is running."""
    import ollama

    try:
        ollama.list()
        return True
    except Exception:
        return False


def run_text_mode(mode: str = "oracle", verbose: bool = True):
    """Run in text-only mode (no voice).

    Args:
        mode: Installation mode
        verbose: Show detailed state information
    """
    print("=" * 60)
    print("THE DESIRE ENGINE - Text Mode")
    print("=" * 60)

    # Check Ollama
    if not check_ollama_available():
        print("\n✗ Error: Ollama is not running")
        print("  Start with: ollama serve")
        print("  Then: ollama pull llama3")
        sys.exit(1)

    # Load configuration
    config = get_config(mode)
    agent = DesireAgent(config.llm, config.mode)
    detector = EndStateDetector(
        liberation_knowledge=config.thresholds.liberation_knowledge,
        liberation_desire=config.thresholds.liberation_desire,
        failure_desire=config.thresholds.failure_desire,
        stagnation_threshold=config.thresholds.stagnation_interactions
    )

    # Load or create state
    session_path = Path(config.session_file)
    state = AgentState.load(session_path) or AgentState()

    if verbose:
        print(f"\nMode: {mode.upper()}")
        print(f"State: {state}\n")

    # Opening statement
    print(agent.generate_opening(state))
    print()

    # Main interaction loop
    try:
        while True:
            if verbose:
                print(f"\n[{state}]")

            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nEnding session...")
                if config.save_session:
                    state.save(session_path)
                    print(f"Session saved to {session_path}")
                break

            if not user_input:
                # Record silence
                print("\n[Silence...]")
                state.record_silence(5.0)
                continue

            # Check if agent should refuse
            if agent.should_refuse(state):
                response = agent.generate_refusal(state)
                interaction_type = InteractionType.REFUSAL
                print(f"\nAgent: {response}")
            else:
                # Generate response
                response, interaction_type = agent.generate_response(user_input, state)
                print(f"\nAgent: {response}")

            if verbose:
                print(f"[Interaction: {interaction_type.value}]")

            # Update state
            state.update(interaction_type)

            # Check for end state
            end_state = detector.check(state)
            if end_state:
                print(f"\n{'=' * 60}")
                print(f"END STATE: {end_state.title}")
                print(f"{end_state.description}")
                print(f"\n\"{end_state.get_final_utterance(state.to_dict())}\"")
                print('=' * 60)

                if config.save_session:
                    state.save(session_path)

                break

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if config.save_session:
            state.save(session_path)
            print(f"Session saved to {session_path}")


def run_voice_mode(mode: str = "oracle", verbose: bool = True):
    """Run in voice mode (full installation).

    Args:
        mode: Installation mode
        verbose: Show detailed state information
    """
    print("=" * 60)
    print("THE DESIRE ENGINE - Voice Mode")
    print("=" * 60)

    # Check Ollama
    if not check_ollama_available():
        print("\n✗ Error: Ollama is not running")
        print("  Start with: ollama serve")
        sys.exit(1)

    # Load configuration
    config = get_config(mode)
    agent = DesireAgent(config.llm, config.mode)
    detector = EndStateDetector(
        liberation_knowledge=config.thresholds.liberation_knowledge,
        liberation_desire=config.thresholds.liberation_desire,
        failure_desire=config.thresholds.failure_desire,
        stagnation_threshold=config.thresholds.stagnation_interactions
    )

    # Initialize voice I/O
    voice_in = VoiceInput(
        model_size=config.voice.whisper_model_size,
        device=config.voice.whisper_device,
        silence_duration=config.voice.silence_duration,
        timeout=config.voice.microphone_timeout
    )

    voice_out = VoiceOutput(
        rate=config.voice.speech_rate,
        use_system_voice=config.voice.use_system_voice
    )

    # Load or create state
    session_path = Path(config.session_file)
    state = AgentState.load(session_path) or AgentState()

    if verbose:
        print(f"\nMode: {mode.upper()}")
        print(f"State: {state}\n")

    # Opening statement
    opening = agent.generate_opening(state)
    voice_out.speak(opening)

    # Main interaction loop
    try:
        while True:
            if verbose:
                print(f"\n[{state}]")

            # Listen for input
            user_input = voice_in.listen()

            if user_input is None:
                # Silence detected
                print("\n[Extended silence...]")
                state.record_silence(config.voice.microphone_timeout)

                # Agent may comment on silence
                if state.detachment > 0.5:
                    voice_out.whisper("Your silence... speaks.")
                    voice_out.long_pause(2.0)

                continue

            # Check if agent should refuse
            if agent.should_refuse(state):
                response = agent.generate_refusal(state)
                voice_out.speak(response, pause_before=1.0)
                state.update(InteractionType.REFUSAL)
            else:
                # Generate response
                response, interaction_type = agent.generate_response(user_input, state)

                # Speak response with appropriate pacing
                if state.detachment > 0.7:
                    voice_out.whisper(response)
                else:
                    voice_out.speak(response)

                # Update state
                state.update(interaction_type)

            if verbose:
                print(f"[Knowledge: {state.knowledge:.2f}, Desire: {state.desire:.2f}, Detachment: {state.detachment:.2f}]")

            # Check for end state
            end_state = detector.check(state)
            if end_state:
                voice_out.long_pause(3.0)
                final_utterance = end_state.get_final_utterance(state.to_dict())
                voice_out.whisper(final_utterance)

                print(f"\n{'=' * 60}")
                print(f"END STATE: {end_state.title}")
                print(f"{end_state.description}")
                print('=' * 60)

                if config.save_session:
                    state.save(session_path)

                break

    except KeyboardInterrupt:
        print("\n\nSession interrupted")
        if config.save_session:
            state.save(session_path)
            print(f"Session saved to {session_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="The Desire Engine - A voice-based misaligned AI installation"
    )

    parser.add_argument(
        "--mode",
        choices=["oracle", "trial", "ascetic"],
        default="oracle",
        help="Installation mode (default: oracle)"
    )

    parser.add_argument(
        "--text",
        action="store_true",
        help="Run in text-only mode (no voice)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output (hide state information)"
    )

    args = parser.parse_args()

    if args.text:
        run_text_mode(args.mode, verbose=not args.quiet)
    else:
        run_voice_mode(args.mode, verbose=not args.quiet)


if __name__ == "__main__":
    main()
