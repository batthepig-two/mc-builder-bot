# Minecraft Bedrock Builder Bot

A command-line bot that automatically builds structures from **.litematic** schematic files (created by the Litematica mod for Java Edition) in any Minecraft Bedrock Edition world.

Two versions are included:

| Version | File | Requires | How it connects |
|---|---|---|---|
| **Node.js** | `bot.mjs` | Node.js v18+ | Joins the server as a bot player |
| **Python** | `bot.py` | Python 3.10+ | Uses Minecraft's WebSocket protocol (no `npm` needed) |

The Python version works on **any device with Python** — including **a-shell on iOS**.

The bot must be **opped** on the server (`/op BuildBot`) to run `/setblock` commands. Creative mode is recommended.

---

## Requirements

**Node.js version:** Node.js v18 or newer, npm

**Python version:** Python 3.10 or newer (no pip packages needed)

Both versions also need:
- A Minecraft Bedrock server reachable over a network (see [Connecting](#connecting-to-your-world))
- A `.litematic` file exported from [Litematica](https://www.curseforge.com/minecraft/mc-mods/litematica)

---

## Installation

### macOS — Terminal

```
brew install node
```
```
git clone https://github.com/batthepig-two/mc-builder-bot.git
```
```
cd mc-builder-bot
```
```
npm install
```
```
node bot.mjs
```

---

### Linux — bash / zsh

Ubuntu / Debian:

```
sudo apt update && sudo apt install -y nodejs npm
```

Fedora / RHEL:

```
sudo dnf install nodejs npm
```

Then:

```
git clone https://github.com/batthepig-two/mc-builder-bot.git
```
```
cd mc-builder-bot
```
```
npm install
```
```
node bot.mjs
```

---

### Windows — PowerShell

```
winget install OpenJS.NodeJS.LTS
```
```
git clone https://github.com/batthepig-two/mc-builder-bot.git
```
```
cd mc-builder-bot
```
```
npm install
```
```
node bot.mjs
```

> No git? Download the repo as a ZIP from GitHub, extract it, then run `npm install` and `node bot.mjs` inside the folder.

---

### iOS — a-shell (Python version)

[a-shell](https://apps.apple.com/app/a-shell/id1473805438) is a free terminal app for iPhone and iPad. It includes Python 3 but **not** Node.js, so use the Python version of the bot:

```
lg2 clone https://github.com/batthepig-two/mc-builder-bot.git
```
```
cd mc-builder-bot
```
```
python3 bot.py
```

No `pip install` needed — the Python bot has **zero external dependencies**.

> **How it works:** The Python bot starts a WebSocket server on your iPhone.
> In Minecraft, open chat and type `/wsserver ws://<your-phone-ip>:19131` to connect.
> Your phone and game device must be on the same Wi-Fi network.

> To use a `.litematic` file on iOS: share it into a-shell via the Files app, then reference it with `/upload ~/Documents/myfile.litematic`.

---

### Android — Termux

[Termux](https://f-droid.org/en/packages/com.termux/) is a free Linux terminal for Android.

Most Android devices use ARM processors, so the native networking module won't have a matching binary. Use `--ignore-scripts` to skip the failing build step:

```
pkg update && pkg install nodejs git
```
```
git clone https://github.com/batthepig-two/mc-builder-bot.git
```
```
cd mc-builder-bot
```
```
npm install --ignore-scripts
```
```
node install-fix.cjs
```
```
node bot.mjs
```

> `--ignore-scripts` skips a native build step that fails on ARM. `install-fix.cjs` patches the networking library to use a pure-JS fallback instead. The bot works the same way — no features are lost.

> **Alternative:** Termux also has Python — run `pkg install python` and use `python3 bot.py` instead (no npm needed).

---

### Any terminal — no git required

```
mkdir mc-builder-bot && cd mc-builder-bot
```
```
curl -O https://raw.githubusercontent.com/batthepig-two/mc-builder-bot/main/bot.mjs
```
```
curl -O https://raw.githubusercontent.com/batthepig-two/mc-builder-bot/main/package.json
```
```
curl -O https://raw.githubusercontent.com/batthepig-two/mc-builder-bot/main/install-fix.cjs
```
```
npm install
```
```
node bot.mjs
```

> On mobile / ARM devices where `npm install` fails, use `npm install --ignore-scripts && node install-fix.cjs` instead.

---

## Connecting to Your World

### Node.js version (`bot.mjs`)

The Node.js bot connects directly to any Bedrock server as a player.

| Situation | What to provide |
|---|---|
| Bedrock Dedicated Server (BDS) | The server's IP and port (default `19132`) |
| PC with "Open to LAN" — bot on the same PC | `127.0.0.1` |
| PC with "Open to LAN" — bot on another device (same Wi-Fi) | Your PC's local IP, e.g. `192.168.1.50` |
| Console (Switch / PlayStation / Xbox) | Requires a dedicated server — consoles cannot expose a local port |
| Realm | Not supported — Realms require Xbox Live authentication |

> The bot connects in **offline mode** (no Xbox Live account needed). Servers that enforce Xbox auth will kick the bot on join.

### Python version (`bot.py`)

The Python bot uses Minecraft's built-in WebSocket protocol. Instead of joining as a player, **your game connects to the bot**:

1. Run `python3 bot.py` — it starts a WebSocket server automatically
2. In Minecraft (Bedrock), open chat and type: `/wsserver ws://<bot-ip>:<port>`
3. The bot sends `/setblock` commands through your game session

Your game device and the device running the bot must be on the **same Wi-Fi network**. The player running `/wsserver` needs **operator permissions** on the server.

---

## Usage

Once running you will see:

```
mc-bot>
```

### Commands — Node.js version

| Command | What it does |
|---|---|
| `/connect <host> [port] [username]` | Connect the bot to a server |
| `/upload <path/to/file.litematic>` | Load a schematic file |
| `/origin <x> <y> <z>` | Set the world coordinates to build at |
| `/build` | Start placing blocks |
| `/pause` | Pause the build |
| `/resume` | Resume a paused build |
| `/stop` | Stop and reset the current build |
| `/status` | Show connection and progress info |
| `/help` | Show the command list |
| `/quit` | Disconnect and exit |

### Commands — Python version

| Command | What it does |
|---|---|
| `/listen [port]` | Start WebSocket server (default 19131) |
| `/upload <path/to/file.litematic>` | Load a schematic file |
| `/origin <x> <y> <z>` | Set the world coordinates to build at |
| `/build` | Start placing blocks |
| `/pause` | Pause the build |
| `/resume` | Resume a paused build |
| `/stop` | Stop and reset the current build |
| `/status` | Show connection and progress info |
| `/help` | Show the command list |
| `/quit` | Disconnect and exit |

---

## Example Session

### Node.js

```
mc-bot> /connect play.myserver.net 19132 BuildBot
```
```
mc-bot> /upload ~/Downloads/my_house.litematic
```
```
mc-bot> /origin 150 64 -200
```
```
mc-bot> /build
```

### Python

```
mc-bot> /listen
```
```
(In Minecraft chat)  /wsserver ws://192.168.1.50:19131
```
```
mc-bot> /upload ~/Documents/my_house.litematic
```
```
mc-bot> /origin 150 64 -200
```
```
mc-bot> /build
```

---

## Notes

- The bot must be opped on the server: `/op BuildBot` (Node.js) or the player must have op (Python)
- Java Edition block types with no Bedrock equivalent are skipped and listed after `/upload`
- Builds run at ~50 blocks/second — adjust `BLOCKS_PER_TICK` / `TICK_INTERVAL_MS` in `bot.mjs` or `BLOCKS_PER_BATCH` in `bot.py`
- Node.js version tested against Bedrock Dedicated Server 1.20+
- Python version works with any Bedrock Edition client that supports `/wsserver`
