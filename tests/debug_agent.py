"""Debug script to test agent response generation."""

import traceback
from src.desire_engine.agent import DesireAgent
from src.desire_engine.state import AgentState
from src.desire_engine.config import LLMConfig, InstallationMode

def test_basic_response():
    """Test a basic agent response with verbose output."""
    print("Creating agent...")
    config = LLMConfig(model_name="llama3", max_tokens=100, temperature=0.7)
    agent = DesireAgent(config, InstallationMode.ORACLE)

    print("Creating state...")
    state = AgentState(knowledge=0.4, desire=0.6, detachment=0.3)
    state.interaction_count = 5

    print(f"Current state: {state}\n")

    print("Building system prompt...")
    system_prompt = agent._build_system_prompt(state)
    print(f"System prompt length: {len(system_prompt)} chars")
    print("\n--- SYSTEM PROMPT ---")
    print(system_prompt)
    print("--- END SYSTEM PROMPT ---\n")

    user_input = "What are you?"
    print(f"User input: '{user_input}'")

    print("\nClassifying interaction...")
    interaction_type = agent.classify_interaction(user_input, state)
    print(f"Interaction type: {interaction_type.value}")

    print("\nCalling Ollama API...")
    print("(This may take a few seconds...)\n")

    try:
        response, interaction_type = agent.generate_response(user_input, state)
        print("✓ Response received:")
        print(f"  '{response}'")
        print(f"\nInteraction type: {interaction_type.value}")

    except Exception:
        print("✗ Error generating response:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_basic_response()
