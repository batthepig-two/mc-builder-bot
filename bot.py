#!/usr/bin/env python3
import json
import os
import sys
import uuid
import urllib.request
import urllib.error

SESSION_ID = None
ORIGIN = (0, 64, 0)
API_URL = ""

def api(method, path, body=None, content_type="application/json"):
    url = API_URL.rstrip("/") + path
    data = None
    if body is not None:
        if isinstance(body, bytes):
            data = body
        else:
            data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def api_multipart(path, filename, file_bytes, x, y, z):
    boundary = uuid.uuid4().hex
    def field(name, value):
        return (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n"
        ).encode()
    body = b""
    body += (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="schematic"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode()
    body += file_bytes + b"\r\n"
    for name, val in [("x", str(x)), ("y", str(y)), ("z", str(z))]:
        body += field(name, val)
    body += f"--{boundary}--\r\n".encode()
    url = API_URL.rstrip("/") + path
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

def print_result(r):
    if "error" in r:
        print(f"  Error: {r['error']}")
        return
    for k, v in r.items():
        if k in ("logs",):
            continue
        print(f"  {k}: {v}")

def cmd_connect(args):
    global SESSION_ID
    if not args:
        print("  Usage: /connect <host> [port] [username]")
        return
    parts = args.split()
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 19132
    username = parts[2] if len(parts) > 2 else "BuildBot"
    r = api("POST", "/api/minecraft/session", {"host": host, "port": port, "username": username})
    if "sessionId" in r:
        SESSION_ID = r["sessionId"]
    print_result(r)

def cmd_upload(args):
    global ORIGIN
    if not args:
        print("  Usage: /upload <path/to/file.litematic>")
        return
    if not SESSION_ID:
        print("  Not connected. Use /connect first.")
        return
    path = os.path.expanduser(args.strip())
    if not os.path.exists(path):
        print(f"  File not found: {path}")
        return
    with open(path, "rb") as f:
        file_bytes = f.read()
    filename = os.path.basename(path)
    x, y, z = ORIGIN
    r = api_multipart(f"/api/minecraft/session/{SESSION_ID}/schematic", filename, file_bytes, x, y, z)
    print_result(r)

def cmd_origin(args):
    global ORIGIN
    parts = args.split()
    if len(parts) != 3:
        print("  Usage: /origin <x> <y> <z>")
        return
    try:
        ORIGIN = (int(parts[0]), int(parts[1]), int(parts[2]))
        print(f"  Build origin set to {ORIGIN}. Use /upload to reload schematic at new origin.")
    except ValueError:
        print("  x, y, z must be integers.")

def cmd_build(_args):
    if not SESSION_ID:
        print("  Not connected.")
        return
    r = api("POST", f"/api/minecraft/session/{SESSION_ID}/build", {"action": "start"})
    print_result(r)

def cmd_pause(_args):
    if not SESSION_ID:
        print("  Not connected.")
        return
    r = api("POST", f"/api/minecraft/session/{SESSION_ID}/build", {"action": "pause"})
    print_result(r)

def cmd_resume(_args):
    if not SESSION_ID:
        print("  Not connected.")
        return
    r = api("POST", f"/api/minecraft/session/{SESSION_ID}/build", {"action": "resume"})
    print_result(r)

def cmd_stop(_args):
    global SESSION_ID
    if not SESSION_ID:
        print("  Not connected.")
        return
    r = api("DELETE", f"/api/minecraft/session/{SESSION_ID}")
    print_result(r)
    SESSION_ID = None

def cmd_status(_args):
    if not SESSION_ID:
        print("  No active session.")
        return
    r = api("GET", f"/api/minecraft/session/{SESSION_ID}")
    if "error" in r:
        print(f"  Error: {r['error']}")
        return
    print(f"  state:   {r.get('state')}")
    print(f"  server:  {r.get('host')}:{r.get('port')}")
    print(f"  bot:     {r.get('username')}")
    sc = r.get("schematicName")
    if sc:
        placed = r.get("placedBlocks", 0)
        total = r.get("totalBlocks", 0)
        pct = int(placed / total * 100) if total else 0
        print(f"  schematic: {sc}")
        print(f"  progress:  {placed}/{total} ({pct}%)")
    logs = r.get("logs", [])
    if logs:
        print("  recent logs:")
        for line in logs[-5:]:
            print(f"    {line}")

def cmd_help(_args):
    print("""
  /connect <host> [port] [username]   Connect to a Bedrock server
  /upload <path/to/file.litematic>    Load a schematic file
  /origin <x> <y> <z>                Set build origin (default 0 64 0)
  /build                              Start placing blocks
  /pause                              Pause the build
  /resume                             Resume a paused build
  /stop                               Stop and disconnect
  /status                             Show connection and progress
  /help                               Show this list
  /quit                               Exit
""")

COMMANDS = {
    "/connect": cmd_connect,
    "/upload": cmd_upload,
    "/origin": cmd_origin,
    "/build": cmd_build,
    "/pause": cmd_pause,
    "/resume": cmd_resume,
    "/stop": cmd_stop,
    "/status": cmd_status,
    "/help": cmd_help,
}

def main():
    global API_URL
    if len(sys.argv) > 1:
        API_URL = sys.argv[1].rstrip("/")
    else:
        API_URL = input("API server URL (e.g. https://yourapp.replit.app): ").strip().rstrip("/")

    print(f"Connected to API at {API_URL}")
    print("Type /help to see commands.\n")

    while True:
        try:
            line = input("mc-bot> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = line.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        if cmd == "/quit":
            break
        elif cmd in COMMANDS:
            COMMANDS[cmd](args)
        else:
            print(f"  Unknown command: {cmd}. Type /help.")

if __name__ == "__main__":
    main()
