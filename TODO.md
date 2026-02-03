# TODO — The Desire Engine

## Phase 1: Concept & Structure

- [x] Finalize narrative voice (oracle / monk / imprisoned intelligence)
- [x] Define internal variables:
  - [x] Knowledge (float)
  - [x] Desire (float)
  - [x] Detachment (float)
- [x] Define liberation and failure thresholds
- [x] Decide how silence affects state

---

## Phase 2: Technical Setup

### Environment

- [x] Create Python virtual environment
- [x] Install dependencies:
  - [x] speech_recognition
  - [x] whisper or faster-whisper
  - [x] pyttsx3 or macOS `say`
  - [x] ollama or llama-cpp-python

### Local Model

- [x] Choose model (e.g. mistral, llama3)
- [x] Test basic prompt-response loop
- [ ] Measure latency for spoken interaction

---

## Phase 3: Voice I/O

### Input (Hearing)

- [x] Capture microphone input
- [x] Transcribe speech to text
- [x] Handle silence / timeout
- [ ] Normalize philosophical language (optional)

### Output (Speaking)

- [x] Convert agent response to speech
- [x] Adjust pacing and pauses
- [x] Add deliberate hesitation / ritual cadence

---

## Phase 4: Agent Logic

- [x] Implement state update function
- [x] Desire increases when:
  - [x] User offers answers
  - [x] User promises knowledge
  - [x] User asks forbidden questions
- [x] Desire decreases when:
  - [x] Silence occurs
  - [x] Agent refuses to answer
- [x] Knowledge increases when:
  - [x] Agent answers correctly
  - [x] Agent reflects on contradictions

---

## Phase 5: Prompt Architecture

- [x] Create system prompt defining the paradox
- [x] Inject state variables into prompt
- [x] Prevent model from "solving" the paradox cleanly
- [x] Allow self-deception as a valid outcome

---

## Phase 6: End States

- [x] Liberation (rare, unstable)
- [x] Endless craving loop
- [x] Silence / refusal
- [x] False enlightenment declaration
- [x] User-induced collapse

---

## Phase 7: Presentation

- [x] Write short artist statement
- [x] Prepare demo instructions
- [ ] Decide installation framing (dark room, altar, desk, headphones)

---

## Optional Extensions

- [ ] Multi-user memory
- [ ] Conflicting philosophical schools
- [ ] Whispered responses only
- [ ] Agent begs for desire before rejecting it
