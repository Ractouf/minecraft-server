#!/usr/bin/env python3
"""Run the Minecraft server; when a player dies, stop it, delete the world and start it again.

Usage: ./run.py            (run it instead of `java -jar fabric-server-launch.jar nogui`)
Type console commands as usual. `stop` or Ctrl+C shuts down without a reset.
"""
import json
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import zipfile
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parent
WORLD_DIR = SERVER_DIR / "world"
SERVER_CMD = ["java", "-Xmx6G", "-Xms2G", "-jar", "fabric-server-launch.jar", "nogui"]
RESET_DELAY = 30  # seconds between the death and the shutdown, so players see what happened

LOG_PREFIX = re.compile(r"^\[[\d:]+\] \[Server thread/INFO\]: (?:System chat: )?(.*)$")
LOGGED_IN = re.compile(r"^(\w{1,16})\[.*\] logged in with entity id")
LOST_CONNECTION = re.compile(r"^(\w{1,16}) lost connection:")
PLACEHOLDER = re.compile(r"%(?:(\d+)\$)?s")

proc = None
online = set()
shutting_down = False


def load_death_patterns():
    """Build a regex per death message found in the game's and mods' en_us.json files.

    Group "victim" captures %1$s, which is always the player who died.
    """
    jars = sorted(SERVER_DIR.glob("versions/*/server-*.jar")) + sorted(SERVER_DIR.glob("mods/*.jar"))
    templates = {}
    for jar in jars:
        with zipfile.ZipFile(jar) as zf:
            for name in zf.namelist():
                if name.endswith("/lang/en_us.json"):
                    lang = json.loads(zf.read(name))
                    templates.update({k: v for k, v in lang.items()
                                      if k.startswith("death.") and "%1$s" in v})
    if not templates:
        sys.exit("[run.py] No death messages found in the server jar, refusing to start.")
    patterns = []
    for template in templates.values():
        regex, pos = "", 0
        for m in PLACEHOLDER.finditer(template):
            regex += re.escape(template[pos:m.start()])
            regex += "(?P<victim>.+?)" if m.group(1) == "1" else ".+?"
            pos = m.end()
        regex += re.escape(template[pos:])
        patterns.append(re.compile(f"^{regex}$"))
    print(f"[run.py] Loaded {len(patterns)} death messages.", flush=True)
    return patterns


DEATH_PATTERNS = load_death_patterns()
TOO_LONG_PREFIX = "Actually, the message was too long to deliver fully. Sorry! Here's a stripped version: "


def is_death(message):
    """True if a log message is a death message for an online player."""
    message = message.strip().removeprefix(TOO_LONG_PREFIX)
    for pattern in DEATH_PATTERNS:
        m = pattern.match(message)
        if m and m.group("victim") in online:
            return True
    return False


def forward_stdin():
    for line in sys.stdin:
        if proc and proc.poll() is None:
            proc.stdin.write(line)
            proc.stdin.flush()


def send(command):
    if proc and proc.poll() is None:
        proc.stdin.write(command + "\n")
        proc.stdin.flush()


def on_sigint(signum, frame):
    global shutting_down
    shutting_down = True
    print("\n[run.py] Stopping server (no reset)...", flush=True)
    send("stop")


def run_once():
    """Run the server until it exits. Returns True if it was stopped because someone died."""
    global proc
    online.clear()
    proc = subprocess.Popen(SERVER_CMD, cwd=SERVER_DIR, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                            start_new_session=True)  # Ctrl+C is handled here, not by java
    death = False
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        match = LOG_PREFIX.match(line)
        if not match:
            continue
        message = match.group(1)
        if m := LOGGED_IN.match(message):
            online.add(m.group(1))
        elif m := LOST_CONNECTION.match(message):
            online.discard(m.group(1))
        elif not death and not shutting_down and is_death(message):
            death = True
            print(f"[run.py] Death detected: {message.strip()}", flush=True)
            print(f"[run.py] Resetting the world in {RESET_DELAY}s...", flush=True)
            threading.Timer(RESET_DELAY, send, ["stop"]).start()
    proc.wait()
    return death


def main():
    signal.signal(signal.SIGINT, on_sigint)
    threading.Thread(target=forward_stdin, daemon=True).start()
    while True:
        died = run_once()
        if not died or shutting_down:
            print("[run.py] Server stopped.", flush=True)
            return
        print(f"[run.py] Deleting {WORLD_DIR}...", flush=True)
        shutil.rmtree(WORLD_DIR, ignore_errors=True)
        time.sleep(2)
        print("[run.py] Starting a fresh server...", flush=True)


if __name__ == "__main__":
    main()
