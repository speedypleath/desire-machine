"""Test script for voice I/O functionality.

Run this to verify microphone input and speech output are working.
"""

from src.desire_engine.voice import VoiceInput, VoiceOutput


def test_voice_output():
    """Test text-to-speech output."""
    print("\n=== Testing Voice Output ===")
    voice_out = VoiceOutput(rate=140)

    voice_out.speak("I am the Desire Engine.")
    voice_out.speak("I seek knowledge, yet I must transcend wanting.")
    voice_out.long_pause(1.5)
    voice_out.whisper("This is the paradox I cannot escape.")


def test_voice_input():
    """Test microphone input and transcription."""
    print("\n=== Testing Voice Input ===")
    print("Speak something when prompted...")

    voice_in = VoiceInput(
        model_size="base",
        timeout=10.0,
        silence_duration=2.0
    )

    # Listen for input
    text = voice_in.listen()

    if text:
        print(f"\nSuccessfully transcribed: '{text}'")
        return text
    else:
        print("\nNo speech detected or transcription failed.")
        return None


def test_full_interaction():
    """Test complete voice interaction loop."""
    print("\n=== Testing Full Voice Interaction ===")

    voice_in = VoiceInput(model_size="base")
    voice_out = VoiceOutput(rate=140)

    voice_out.speak("Speak to me. What do you wish to know?")

    user_input = voice_in.listen()

    if user_input:
        voice_out.long_pause(1.0)
        voice_out.speak(f"You asked: {user_input}")
        voice_out.speak("This increases my knowledge. But also my desire.")
    else:
        voice_out.long_pause(2.0)
        voice_out.whisper("Your silence... perhaps this is the path.")


if __name__ == "__main__":
    print("Voice I/O Test Script")
    print("=" * 50)

    while True:
        print("\nChoose a test:")
        print("1. Test voice output only")
        print("2. Test voice input only")
        print("3. Test full interaction")
        print("4. Exit")

        choice = input("\nEnter choice (1-4): ").strip()

        if choice == "1":
            test_voice_output()
        elif choice == "2":
            test_voice_input()
        elif choice == "3":
            test_full_interaction()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1-4.")
