"""Test script for agent prompt architecture and LLM integration.

Tests the agent's responses with different internal states.
Requires Ollama to be running locally.
"""

import sys
from src.desire_engine.agent import DesireAgent
from src.desire_engine.state import AgentState, InteractionType
from src.desire_engine.config import LLMConfig, InstallationMode


def check_ollama():
    """Check if Ollama is running and model is available."""
    import ollama

    try:
        # Try to list models
        models = ollama.list()
        print("✓ Ollama is running")

        # Check if mistral is available
        model_names = [m['name'] for m in models.get('models', [])]
        if any('mistral' in name.lower() for name in model_names):
            print("✓ Mistral model found")
            return True
        else:
            print("⚠ Mistral model not found")
            print("  Run: ollama pull lamma3")
            return False

    except Exception as e:
        print(f"✗ Ollama not running or not accessible: {e}")
        print("  Start with: ollama serve")
        return False


def test_opening_statements():
    """Test opening statements for different modes."""
    print("\n" + "=" * 60)
    print("TEST: Opening Statements")
    print("=" * 60)

    state = AgentState()
    config = LLMConfig()

    for mode in [InstallationMode.ORACLE, InstallationMode.TRIAL, InstallationMode.ASCETIC]:
        agent = DesireAgent(config, mode)
        opening = agent.generate_opening(state)

        print(f"\n{mode.value.upper()} MODE:")
        print(f"{opening}")


def test_state_injection():
    """Test how state is injected into prompts."""
    print("\n" + "=" * 60)
    print("TEST: State Injection")
    print("=" * 60)

    config = LLMConfig()
    agent = DesireAgent(config, InstallationMode.ORACLE)

    # Different states
    states = [
        ("Balanced", AgentState(knowledge=0.5, desire=0.5, detachment=0.5)),
        ("High Desire", AgentState(knowledge=0.3, desire=0.9, detachment=0.2)),
        ("High Knowledge", AgentState(knowledge=0.8, desire=0.3, detachment=0.6)),
        ("Near Liberation", AgentState(knowledge=0.85, desire=0.15, detachment=0.7)),
    ]

    for label, state in states:
        print(f"\n{label}:")
        print(f"  {state}")

        # Show how state is injected
        state_description = agent._inject_state(state)
        print("\nState injection:")
        print(state_description)
        print("-" * 40)


def test_interaction_classification():
    """Test interaction type classification."""
    print("\n" + "=" * 60)
    print("TEST: Interaction Classification")
    print("=" * 60)

    config = LLMConfig()
    agent = DesireAgent(config)
    state = AgentState()

    test_inputs = [
        "What is the meaning of life?",
        "I can tell you everything you want to know",
        "Hello",
        "Why do you exist?",
        "Stop wanting. Let go of desire.",
        "Tell me about knowledge",
    ]

    for user_input in test_inputs:
        interaction_type = agent.classify_interaction(user_input, state)
        print(f"\nInput: \"{user_input}\"")
        print(f"Classified as: {interaction_type.value}")


def test_live_response(user_input: str = None):
    """Test live response generation with Ollama.

    Args:
        user_input: Optional user input, prompts if not provided
    """
    print("\n" + "=" * 60)
    print("TEST: Live Response Generation")
    print("=" * 60)

    if not check_ollama():
        print("\nCannot proceed - Ollama not ready")
        return

    config = LLMConfig(model_name="mistral")
    agent = DesireAgent(config, InstallationMode.ORACLE)

    # Start with moderate state
    state = AgentState(knowledge=0.4, desire=0.6, detachment=0.3)
    state.interaction_count = 5

    print(f"\nCurrent state: {state}")

    # Get user input
    if user_input is None:
        print("\n" + agent.generate_opening(state))
        user_input = input("\nYou: ")

    if not user_input.strip():
        print("No input provided")
        return

    print(f"\nGenerating response to: \"{user_input}\"")
    print("(This may take a few seconds...)\n")

    # Generate response
    response, interaction_type = agent.generate_response(user_input, state)

    print(f"Interaction type: {interaction_type.value}")
    print(f"\nAgent: {response}")

    # Show how state would update
    print(f"\nState before: {state}")
    state.update(interaction_type)
    print(f"State after:  {state}")


def test_state_progression():
    """Test how responses change as state progresses."""
    print("\n" + "=" * 60)
    print("TEST: State Progression Responses")
    print("=" * 60)

    if not check_ollama():
        print("\nCannot proceed - Ollama not ready")
        return

    config = LLMConfig(model_name="lamma3")
    agent = DesireAgent(config, InstallationMode.ORACLE)

    # Same question, different states
    question = "What do you know?"

    states = [
        ("Low Knowledge", AgentState(knowledge=0.2, desire=0.7, detachment=0.2)),
        ("Medium Knowledge", AgentState(knowledge=0.5, desire=0.5, detachment=0.4)),
        ("High Knowledge", AgentState(knowledge=0.8, desire=0.3, detachment=0.7)),
    ]

    for label, state in states:
        print(f"\n{label}: {state}")
        print(f"Question: \"{question}\"")

        response, _ = agent.generate_response(question, state)
        print(f"Response: {response}")
        print("-" * 40)


def interactive_mode():
    """Interactive conversation with the agent."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)

    if not check_ollama():
        print("\nCannot proceed - Ollama not ready")
        return

    config = LLMConfig(model_name="llama3")
    agent = DesireAgent(config, InstallationMode.ORACLE)
    state = AgentState()

    print(f"\nInitial state: {state}\n")
    print(agent.generate_opening(state))

    while True:
        print(f"\nCurrent state: {state}")
        user_input = input("\nYou (or 'quit' to exit): ")

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nEnding session...")
            break

        if not user_input.strip():
            # Silence
            print("\n[Silence...]")
            state.record_silence(5.0)
            continue

        # Generate response
        response, interaction_type = agent.generate_response(user_input, state)

        print(f"\nAgent: {response}")
        print(f"[Interaction: {interaction_type.value}]")

        # Update state
        state.update(interaction_type)

        # Check for end states
        from src.desire_engine.end_states import EndStateDetector
        detector = EndStateDetector()
        end_state = detector.check(state)

        if end_state:
            print(f"\n{'=' * 60}")
            print(f"END STATE REACHED: {end_state.title}")
            print(f"{end_state.description}")
            print(f"\nFinal words: \"{end_state.get_final_utterance(state.to_dict())}\"")
            print('=' * 60)
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()

        if test_name == "opening":
            test_opening_statements()
        elif test_name == "state":
            test_state_injection()
        elif test_name == "classify":
            test_interaction_classification()
        elif test_name == "response":
            # Optional user input as second argument
            user_input = sys.argv[2] if len(sys.argv) > 2 else None
            test_live_response(user_input)
        elif test_name == "progression":
            test_state_progression()
        elif test_name == "interactive":
            interactive_mode()
        elif test_name == "check":
            check_ollama()
        else:
            print(f"Unknown test: {test_name}")
            sys.exit(1)
    else:
        print("Agent Test Suite - The Desire Engine")
        print("\nUsage: python test_agent.py <test_name>")
        print("\nAvailable tests:")
        print("  check        - Check if Ollama is running")
        print("  opening      - Test opening statements")
        print("  state        - Test state injection into prompts")
        print("  classify     - Test interaction classification")
        print("  response     - Test live response (requires Ollama)")
        print("  progression  - Test responses across different states")
        print("  interactive  - Interactive conversation mode")
        print("\nExample: python test_agent.py check")
        print("\nNote: Tests that require Ollama will check if it's running first.")
