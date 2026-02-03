"""Simple non-interactive voice test.

Tests voice output without requiring interactive input.
Run with: uv run python test_voice_simple.py <test_number>
"""

import sys
from src.desire_engine.voice import VoiceInput, VoiceOutput


def test_output_only():
    """Test text-to-speech output."""
    print("\n=== Testing Voice Output ===\n")
    voice_out = VoiceOutput(rate=140)

    voice_out.speak("I am the Desire Engine.")
    voice_out.speak("I seek knowledge, yet I must transcend wanting.")
    voice_out.long_pause(1.5)
    voice_out.whisper("This is the paradox I cannot escape.")

    print("\n✓ Voice output test complete")


def test_input_only():
    """Test microphone input and transcription."""
    print("\n=== Testing Voice Input ===")
    print("You have 10 seconds to speak after calibration...\n")

    try:
        voice_in = VoiceInput(
            model_size="base",
            timeout=10.0,
            silence_duration=2.0
        )

        text = voice_in.listen()

        if text:
            print(f"\n✓ Successfully transcribed: '{text}'")
        else:
            print("\n⚠ No speech detected or transcription failed")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nNote: Voice input requires a working microphone and PyAudio installed.")


def test_interaction():
    """Test complete voice interaction."""
    print("\n=== Testing Full Voice Interaction ===")
    print("The agent will speak, then listen for your response...\n")

    try:
        voice_in = VoiceInput(model_size="base", timeout=10.0)
        voice_out = VoiceOutput(rate=140)

        voice_out.speak("Speak to me. What do you wish to know?")

        user_input = voice_in.listen()

        if user_input:
            voice_out.long_pause(1.0)
            voice_out.speak(f"You asked: {user_input}")
            voice_out.speak("This increases my knowledge. But also my desire.")
            print("\n✓ Full interaction test complete")
        else:
            voice_out.long_pause(2.0)
            voice_out.whisper("Your silence... perhaps this is the path.")
            print("\n✓ Silence handling test complete")

    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    print("Voice I/O Test - The Desire Engine")
    print("=" * 50)

    if len(sys.argv) > 1:
        test_choice = sys.argv[1]
    else:
        print("\nUsage: python test_voice_simple.py <test_number>")
        print("\nAvailable tests:")
        print("  1 - Test voice output only (no microphone needed)")
        print("  2 - Test voice input only (requires microphone)")
        print("  3 - Test full interaction (requires microphone)")
        print("\nExample: python test_voice_simple.py 1")
        sys.exit(0)

    if test_choice == "1":
        test_output_only()
    elif test_choice == "2":
        test_input_only()
    elif test_choice == "3":
        test_interaction()
    else:
        print(f"Invalid test number: {test_choice}")
        print("Use 1, 2, or 3")
        sys.exit(1)
