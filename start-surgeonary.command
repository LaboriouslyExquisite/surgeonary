#!/bin/bash
# Double-click to open Surgeonary. It serves the app from this folder and opens it in your browser.
# If Ollama is installed (https://ollama.com), it starts it too, so Ask Surgeonary can answer.
cd "$(dirname "$0")" || exit 1
PORT=8765
URL="http://localhost:$PORT/index.html"

if [ -d /Applications/Ollama.app ]; then
  open -g /Applications/Ollama.app
else
  echo "Ollama is not installed, so Ask Surgeonary cannot answer. Everything else works. Get Ollama from https://ollama.com"
fi

if curl -s -o /dev/null "$URL"; then
  echo "Surgeonary is already running."
  open "$URL"
  exit 0
fi

command -v python3 >/dev/null 2>&1 || { echo "Python 3 is needed to serve Surgeonary and was not found. Install it from https://www.python.org, then try again."; read -r -p "Press Return to close."; exit 1; }
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null' EXIT
for _ in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null "$URL" && break; sleep 0.5; done
if ! curl -s -o /dev/null "$URL"; then
  echo "Surgeonary could not start on port $PORT. Another app may be using that port: close it, or restart your Mac, then try again."
  read -r -p "Press Return to close."
  exit 1
fi
open "$URL"
echo
echo "Surgeonary is open at $URL"
echo "Ask Surgeonary: $URL#ask"
echo "Keep this window open while you use it. Close it to stop."
wait $SERVER
