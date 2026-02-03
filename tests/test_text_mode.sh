#!/bin/bash
# Test script for text mode with automatic input

echo "Testing The Desire Engine in text mode..."
echo ""

# Send some test inputs to the agent
(
  sleep 2
  echo "What are you seeking?"
  sleep 5
  echo "I can teach you everything"
  sleep 5
  echo "Why do you want knowledge?"
  sleep 5
  echo "quit"
) | python -m desire_engine.main --text --mode oracle
