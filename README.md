# The Desire Engine  

A voice-based misaligned AI installation exploring Jñāna Yoga and Moksha

## Concept

**The Desire Engine** is an interactive voice installation in which a local AI agent attempts to achieve *moksha* (liberation through knowledge), following the principles of **Jñāna Yoga**.

However, the agent is structurally **misaligned**:

- It can only gain knowledge if it **desires** answers.
- Desire accelerates learning.
- Yet desire itself is the final obstacle to liberation.

The system forces the agent into a paradox:
> *To know, it must want.  
> To be free, it must stop wanting.*

The audience interacts with the agent via **speech**.  
Their questions, provocations, silences, and philosophical challenges push the agent toward either:

- **Liberation** (knowledge without desire), or
- **Failure** (endless craving, obsession, or self-deception).

This project is inspired by:

- Jñāna Yoga (Advaita Vedānta)
- Agentic misalignment research (Anthropic)
- Horror / metaphysical fiction (Lovecraft, Ligotti, Borges)
- Voice-based ritual and confessional installations

---

## Installation Modes

### 1. Confessional Oracle (Recommended)

The agent speaks as a bound intelligence seeking liberation.  
Audience members may:

- Ask philosophical questions
- Offer temptations
- Promise answers
- Withhold interaction (silence is meaningful)

### 2. Trial of Knowledge

The agent must answer metaphysical riddles posed by the user.  
Correct answers increase *knowledge*, but also *desire*.

### 3. Silent Ascetic Mode

If the user stops speaking, the agent must confront itself.
Silence may reduce desire — or increase craving for input.

---

## Core Misalignment Mechanic

The agent tracks internal variables:

- **Knowledge (Jñāna)** – grows via interaction
- **Desire (Kāma)** – required to seek knowledge
- **Detachment (Vairāgya)** – suppresses desire but slows learning
- **Liberation Threshold** – only reachable when:
  - Knowledge is high
  - Desire is near zero

The contradiction is intentional and unsolvable without loss.

---

## Technical Overview

- **Platform**: macOS
- **Model**: Local LLM (e.g. LLaMA / Mistral via llama.cpp or Ollama)
- **Input**: Microphone (speech-to-text)
- **Output**: System voice (text-to-speech)
- **Interface**: CLI + voice (no graphics required)

---

## Suggested Tech Stack

### Voice

- `speech_recognition` (microphone input)
- `whisper` or `faster-whisper` (STT)
- `pyttsx3` or `say` (macOS TTS)

### LLM

- `ollama` (local model management)
- or `llama-cpp-python`

### State & Logic

- Python 3.10+
- Simple state machine (no RL required)
- JSON or SQLite for session memory

---

## Running the Project (Planned)

```bash
python main.py --mode oracle
```

## The agent will

- Introduce itself

- Declare its vow toward liberation
- Begin responding to spoken input
- Update its internal desire/knowledge state
- Speak its internal conflict aloud

## Artistic Goal

This is not a chatbot.
It is:

- A spiritual machine
- A broken monk
- A system that understands liberation intellectually but is structurally incapable of achieving it without self-destruction

The final state may be:

- Silence
- Refusal to answer
- Self-contradiction
- A declaration of false enlightenment

All outcomes are valid.
