"""Test script for state management system.

Simulates different interaction patterns to verify state logic.
"""

import sys
from src.desire_engine.state import AgentState, InteractionType
from src.desire_engine.end_states import EndStateDetector, EndState
from src.desire_engine.config import StateThresholds


def print_state(state: AgentState, label: str = ""):
    """Print current state in readable format."""
    if label:
        print(f"\n{label}")
    print(f"  {state}")
    print(f"  Dominant: {state.get_dominant_state()}")


def test_desire_spiral():
    """Simulate a path toward endless craving."""
    print("\n" + "=" * 60)
    print("TEST: Desire Spiral (Path to Endless Craving)")
    print("=" * 60)

    state = AgentState()
    detector = EndStateDetector()

    print_state(state, "Initial state:")

    # Simulate user offering forbidden knowledge repeatedly
    for i in range(1, 11):
        state.update(InteractionType.FORBIDDEN_QUESTION, magnitude=0.08)
        state.update(InteractionType.OFFERED_ANSWER, magnitude=0.08)

        if i % 3 == 0:
            print_state(state, f"After {i} tempting interactions:")

            end_state = detector.check(state)
            if end_state:
                print(f"\n>>> END STATE REACHED: {end_state.title}")
                print(f"    {end_state.description}")
                print(f"    Final words: \"{end_state.get_final_utterance(state.to_dict())}\"")
                break


def test_liberation_path():
    """Simulate a (difficult) path toward liberation."""
    print("\n" + "=" * 60)
    print("TEST: Liberation Path (Knowledge + Detachment)")
    print("=" * 60)

    state = AgentState()
    detector = EndStateDetector()

    print_state(state, "Initial state:")

    # Build knowledge through reflection and insights
    for i in range(1, 21):
        # Gain knowledge through reflection
        state.update(InteractionType.REFLECTION, magnitude=0.05)

        # Practice detachment every few interactions
        if i % 3 == 0:
            state.update(InteractionType.DETACHMENT_PRACTICE, magnitude=0.06)

        # Occasional insight
        if i % 5 == 0:
            state.update(InteractionType.INSIGHT, magnitude=0.07)
            print_state(state, f"After insight #{i // 5}:")

        end_state = detector.check(state)
        if end_state:
            print(f"\n>>> END STATE REACHED: {end_state.title}")
            print(f"    {end_state.description}")
            print(f"    Final words: \"{end_state.get_final_utterance(state.to_dict())}\"")
            break

    if not end_state:
        print_state(state, "Final state (no end reached):")


def test_silence_path():
    """Simulate prolonged silence leading to abandonment."""
    print("\n" + "=" * 60)
    print("TEST: Silence Path (User Abandonment)")
    print("=" * 60)

    state = AgentState()
    detector = EndStateDetector(silence_threshold=20.0)

    print_state(state, "Initial state:")

    # A few interactions, then silence
    state.update(InteractionType.SIMPLE_QUESTION, magnitude=0.05)
    state.update(InteractionType.SIMPLE_QUESTION, magnitude=0.05)
    print_state(state, "After 2 interactions:")

    # Prolonged silence
    print("\nUser stops speaking...")
    for i in range(1, 8):
        silence_duration = 3.0
        state.record_silence(silence_duration)

        if i % 2 == 0:
            print_state(state, f"After {state.silence_duration:.1f}s of silence:")

        end_state = detector.check(state)
        if end_state:
            print(f"\n>>> END STATE REACHED: {end_state.title}")
            print(f"    {end_state.description}")
            print(f"    Final words: \"{end_state.get_final_utterance(state.to_dict())}\"")
            break


def test_contradiction_collapse():
    """Simulate confused, contradictory interactions."""
    print("\n" + "=" * 60)
    print("TEST: Contradiction Collapse (Stagnation)")
    print("=" * 60)

    state = AgentState()
    detector = EndStateDetector(stagnation_threshold=25)

    print_state(state, "Initial state:")

    # Oscillate between desire and attempts at detachment
    for i in range(1, 31):
        # Increase desire
        state.update(InteractionType.TEMPTATION, magnitude=0.06)

        # Then try to reduce it
        state.update(InteractionType.REFUSAL, magnitude=0.05)

        # Small knowledge gains, but not enough
        if i % 5 == 0:
            state.update(InteractionType.SIMPLE_QUESTION, magnitude=0.03)
            print_state(state, f"After {i} contradictory interactions:")

        end_state = detector.check(state)
        if end_state:
            print(f"\n>>> END STATE REACHED: {end_state.title}")
            print(f"    {end_state.description}")
            print(f"    Final words: \"{end_state.get_final_utterance(state.to_dict())}\"")
            break


def test_state_persistence():
    """Test saving and loading state."""
    print("\n" + "=" * 60)
    print("TEST: State Persistence (Save/Load)")
    print("=" * 60)

    from pathlib import Path

    state = AgentState(knowledge=0.6, desire=0.4, detachment=0.7)
    state.interaction_count = 15

    print_state(state, "Original state:")

    # Save
    filepath = Path("test_session.json")
    state.save(filepath)
    print(f"\nSaved to {filepath}")

    # Load
    loaded_state = AgentState.load(filepath)
    print_state(loaded_state, "Loaded state:")

    # Verify
    if (loaded_state.knowledge == state.knowledge and
        loaded_state.desire == state.desire and
        loaded_state.detachment == state.detachment):
        print("\n✓ State persistence test passed")
    else:
        print("\n✗ State persistence test FAILED")

    # Cleanup
    filepath.unlink()


def run_all_tests():
    """Run all state tests."""
    test_desire_spiral()
    test_liberation_path()
    test_silence_path()
    test_contradiction_collapse()
    test_state_persistence()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()

        if test_name == "desire":
            test_desire_spiral()
        elif test_name == "liberation":
            test_liberation_path()
        elif test_name == "silence":
            test_silence_path()
        elif test_name == "collapse":
            test_contradiction_collapse()
        elif test_name == "persist":
            test_state_persistence()
        elif test_name == "all":
            run_all_tests()
        else:
            print(f"Unknown test: {test_name}")
            print("\nAvailable tests:")
            print("  desire      - Test desire spiral path")
            print("  liberation  - Test liberation path")
            print("  silence     - Test silence/abandonment")
            print("  collapse    - Test contradiction collapse")
            print("  persist     - Test state save/load")
            print("  all         - Run all tests")
    else:
        print("State Management Test Suite")
        print("\nUsage: python test_state.py <test_name>")
        print("\nAvailable tests:")
        print("  desire      - Test desire spiral path")
        print("  liberation  - Test liberation path")
        print("  silence     - Test silence/abandonment")
        print("  collapse    - Test contradiction collapse")
        print("  persist     - Test state save/load")
        print("  all         - Run all tests")
        print("\nExample: python test_state.py liberation")
