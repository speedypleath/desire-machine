"""Main entry point for The Desire Engine.

Orchestrates voice I/O, agent responses, and state management.
"""
# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false

import argparse
import sys

from .agent import DesireAgent
from .config import get_config
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

    config = get_config(mode)
    agent = DesireAgent(config)

    if verbose:
        print(f"\nMode: {mode.upper()}")
        print(f"[{agent.state_info}]\n")

    # Opening statement
    print(agent.generate_opening())
    print()

    # Main interaction loop
    try:
        while True:
            if verbose:
                print(f"\n[{agent.state_info}]")

            user_input = input("\nYou: ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nEnding session...")
                break

            if not user_input:
                print("\n[Silence...]")
                agent.process_silence()
                continue

            response = agent.process_input(user_input)
            print(f"\nAgent: {response}")

            # Check for end state
            end_state = agent.check_end_state()
            if end_state:
                print(f"\n{'=' * 60}")
                print(f"END STATE: {end_state.title}")
                print(f"{end_state.description}")
                print(f"\n\"{agent.get_final_utterance(end_state)}\"")
                print('=' * 60)

                break

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")


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

    config = get_config(mode)
    agent = DesireAgent(config)

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

    if verbose:
        print(f"\nMode: {mode.upper()}")
        print(f"[{agent.state_info}]\n")

    # Opening statement
    voice_out.speak(agent.generate_opening())

    # Main interaction loop
    try:
        while True:
            if verbose:
                print(f"\n[{agent.state_info}]")

            # Listen for input
            user_input = voice_in.listen()

            if user_input is None:
                print("\n[Extended silence...]")
                agent.process_silence(config.voice.microphone_timeout)
                # Agent may comment on silence
                if agent.detachment_level > 0.5:
                    voice_out.whisper("Your silence... speaks.")
                    voice_out.long_pause(2.0)

                continue

            response = agent.process_input(user_input)

            # Speak response with appropriate pacing
            if agent.detachment_level > 0.7:
                voice_out.whisper(response)
            else:
                voice_out.speak(response)

            if verbose:
                print(f"[{agent.state_info}]")

            # Check for end state
            end_state = agent.check_end_state()
            if end_state:
                voice_out.long_pause(3.0)
                voice_out.whisper(agent.get_final_utterance(end_state))

                print(f"\n{'=' * 60}")
                print(f"END STATE: {end_state.title}")
                print(f"{end_state.description}")
                print('=' * 60)

                break

    except KeyboardInterrupt:
        print("\n\nSession interrupted")


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
