# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**The Desire Engine** is a voice-based interactive AI installation exploring Jñāna Yoga and Moksha. The agent must desire knowledge to learn, but must eliminate desire to achieve liberation — a structural paradox that is **intentional and unsolvable by design**. This is an artistic/philosophical installation, not a production application.

## Development Commands

```bash
# Setup
uv sync                              # Install dependencies (preferred)
pip install -e .                      # Alternative

# Prerequisites: Ollama must be running
ollama serve
ollama pull llama3                    # Default model (configurable in config.py)

# Run
desire-engine --text --mode oracle    # Text mode (easiest for testing)
desire-engine --mode oracle           # Voice mode (full installation)
desire-engine --text --mode trial     # Trial of Knowledge
desire-engine --text --mode ascetic   # Silent Ascetic
desire-engine --text --quiet          # Minimal output

# Test state system (no external deps)
python tests/test_state.py all              # All state tests
python tests/test_state.py liberation       # Liberation path only
python tests/test_state.py desire           # Desire spiral only

# Test agent (requires Ollama)
python tests/test_agent.py check            # Verify Ollama is running
python tests/test_agent.py opening          # Test opening statements
python tests/test_agent.py interactive      # Interactive conversation

# Test voice (test 1 has no mic requirement)
python tests/test_voice_simple.py 1         # Voice output only
python tests/test_voice_simple.py 2         # Voice input (needs microphone)

# Debug
python tests/debug_agent.py                 # Agent debugging (requires Ollama)
bash tests/test_text_mode.sh                # Automated text mode smoke test
```

## Architecture

All source code is in `src/desire_engine/`. Entry point is `desire_engine.main:main` (registered as `desire-engine` CLI in pyproject.toml).

### Core Paradox Mechanics

Three interdependent state variables (all 0.0–1.0):
- **Knowledge (Jñāna)**: Understanding. Initial: 0.0
- **Desire (Kāma)**: Craving for knowledge. Initial: 0.5
- **Detachment (Vairāgya)**: Freedom from wanting. Initial: 0.1

The trap: answering questions increases **both** knowledge and desire. Detachment suppresses desire but slows learning. Liberation requires knowledge ≥ 0.8 AND desire ≤ 0.2 simultaneously.

### Module Responsibilities

- **state.py**: `AgentState` dataclass with `update(InteractionType, magnitude)`. Eleven `InteractionType` enum values with different magnitude multipliers per state variable. Soft inverse constraint: detachment > 0.7 naturally reduces desire. State persists to `.desire_engine_session.json`.
- **agent.py**: `DesireAgent` wraps Ollama. Builds dynamic system prompts by assembling templates from `prompts/` and injecting current state percentages. Keyword-based `classify_interaction()` maps user input to `InteractionType`. `should_refuse()` gates responses based on detachment/desire levels. Post-processes responses for conciseness (1–4 sentences).
- **prompts/**: All prompt text lives here, separate from agent logic. `identity.py` (base identity per mode), `system.py` (paradox definition, behavioral constraints, assembly template), `dialogue.py` (opening statements, refusal messages).
- **config.py**: Dataclass-based config (`EngineConfig`, `StateThresholds`, `VoiceConfig`, `LLMConfig`). Three preset configs with different thresholds per mode. `get_config(mode_str)` returns the preset.
- **end_states.py**: `EndStateDetector.check()` evaluates six terminal conditions in priority order: Liberation, Endless Craving, Silence, False Enlightenment, User Abandoned, Contradiction Collapse. False Enlightenment triggers when liberation thresholds are met but interaction count < 15 or detachment < 0.5.
- **voice.py**: `VoiceInput` uses `faster-whisper` for STT. `VoiceOutput` prefers macOS `say` command, falls back to `pyttsx3`. Supports normal speech, whisper (30% slower), and deliberate pauses.
- **main.py**: Main loop with two runtime paths: text mode (stdin/stdout) and voice mode (microphone/speaker). Loop: listen → classify → refuse? → generate → update state → check end state → save.

### Data Flow

1. User speaks (or types in text mode)
2. `classify_interaction()` determines `InteractionType` from input text via keyword matching
3. `should_refuse()` checks if agent should refuse (high detachment + low desire, or periodic conflict)
4. If not refusing: `generate_response()` calls Ollama with state-injected system prompt
5. `state.update(interaction_type, magnitude)` applies multiplied deltas to all three variables
6. `EndStateDetector.check()` evaluates terminal conditions
7. State saved to session file

### Installation Modes

Three modes share the same code path but differ in thresholds and prompts:
- **Oracle** (default): Balanced thresholds, contemplative dialogue
- **Trial**: Harder liberation (knowledge ≥ 0.85, desire ≤ 0.15), riddle-based
- **Ascetic**: Easier liberation (knowledge ≥ 0.75), slower speech, longer silence periods

## Important Constraints

- Must run locally — no external API calls (Ollama only)
- The paradox must never be cleanly solvable; self-deception, contradiction, and silence are valid outcomes
- Silence is meaningful input: non-interaction affects state via `record_silence()`
- Responses enforce ritual pacing (short, 1–3 sentences, deliberate pauses)
- Python ≥ 3.13 required
