# Minecraft Bedrock Builder Bot

A command-line bot that connects to any Minecraft Bedrock Edition server and automatically builds structures from **.litematic** schematic files (created by the Litematica mod for Java Edition).

The bot must be **opped** on the server (`/op BuildBot`) to run `/setblock` commands. Creative mode is recommended.

---

## Requirements

- **Node.js v18 or newer**
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

The bot connects to any Bedrock server reachable over a network.

| Situation | What to provide |
|---|---|
| Bedrock Dedicated Server (BDS) | The server's IP and port (default `19132`) |
| PC with "Open to LAN" — bot on the same PC | `127.0.0.1` |
| PC with "Open to LAN" — bot on another device (same Wi-Fi) | Your PC's local IP, e.g. `192.168.1.50` |
| Console (Switch / PlayStation / Xbox) | Requires a dedicated server — consoles cannot expose a local port |
| Realm | Not supported — Realms require Xbox Live authentication |

> The bot connects in **offline mode** (no Xbox Live account needed). Servers that enforce Xbox auth will kick the bot on join.

---

## Usage

Once running you will see:

```
mc-bot>
```

### Commands

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

---

## Example Session

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

---

## Notes

- The bot must be opped on the server: `/op BuildBot`
- Java Edition block types with no Bedrock equivalent are skipped and listed after `/upload`
- Builds run at 50 blocks/second — adjust `BLOCKS_PER_TICK` and `TICK_INTERVAL_MS` in `bot.mjs` if needed
- Tested against Bedrock Dedicated Server 1.20+
