# Minecraft Bedrock Builder Bot

A command-line bot that connects to any Minecraft Bedrock Edition server and automatically builds structures from **.litematic** schematic files (created by the Litematica mod for Java Edition).

The bot must be **opped** on the server (`/op BuildBot`) to run `/setblock` commands. Creative mode is recommended.

---

## Requirements

- **Node.js v18 or newer** — the only dependency you need to install yourself
- A Minecraft Bedrock server reachable over a network (see [Connecting](#connecting-to-your-world))
- A `.litematic` file exported from [Litematica](https://www.curseforge.com/minecraft/mc-mods/litematica) (Java Edition mod)

---

## Installation

### macOS — Terminal

```sh
# Install Node.js with Homebrew (skip if already installed)
brew install node

# Clone the repo and install bot dependencies
git clone https://github.com/batthepig-two/mc-builder-bot.git
cd mc-builder-bot
npm install

# Start the bot
node bot.mjs
```

---

### Linux — bash / zsh

```sh
# Ubuntu / Debian
sudo apt update && sudo apt install -y nodejs npm

# Fedora / RHEL
sudo dnf install nodejs npm

# Then clone and run
git clone https://github.com/batthepig-two/mc-builder-bot.git
cd mc-builder-bot
npm install
node bot.mjs
```

---

### Windows — PowerShell

```powershell
# Install Node.js with winget (or download from https://nodejs.org)
winget install OpenJS.NodeJS.LTS

# Clone and run (in PowerShell or Command Prompt)
git clone https://github.com/batthepig-two/mc-builder-bot.git
cd mc-builder-bot
npm install
node bot.mjs
```

> No git? Download the repo as a ZIP from GitHub, extract it, then run `npm install` and `node bot.mjs` inside the folder.

---

### iOS — a-shell

[a-shell](https://apps.apple.com/app/a-shell/id1473805438) is a free terminal app for iPhone and iPad with built-in Node.js support.

```sh
# In a-shell on your iPhone or iPad:
git clone https://github.com/batthepig-two/mc-builder-bot.git
cd mc-builder-bot
npm install
node bot.mjs
```

> To use a `.litematic` file on iOS: share it into a-shell via the Files app (tap Share → a-shell), then reference it with `/upload ~/Documents/myfile.litematic`.

---

### Android — Termux

[Termux](https://f-droid.org/en/packages/com.termux/) is a free Linux terminal for Android.

```sh
# In Termux:
pkg update && pkg install nodejs git
git clone https://github.com/batthepig-two/mc-builder-bot.git
cd mc-builder-bot
npm install
node bot.mjs
```

---

### Any POSIX terminal — no git required

```sh
mkdir mc-builder-bot && cd mc-builder-bot
curl -O https://raw.githubusercontent.com/batthepig-two/mc-builder-bot/main/bot.mjs
curl -O https://raw.githubusercontent.com/batthepig-two/mc-builder-bot/main/package.json
npm install
node bot.mjs
```

---

## Connecting to Your World

The bot connects to any Bedrock server reachable over a network.

| Situation | What to provide |
|---|---|
| Bedrock Dedicated Server (BDS) | The server's IP address and port (default `19132`) |
| PC with "Open to LAN" — bot on the same PC | `127.0.0.1` |
| PC with "Open to LAN" — bot on another device (same Wi-Fi) | Your PC's local IP, e.g. `192.168.1.50` |
| Console (Switch / PlayStation / Xbox) | Requires a dedicated server — consoles cannot expose a local port |
| Realm | Not supported — Realms require Xbox Live authentication |

> The bot connects in **offline mode** (no Xbox Live account needed). Servers that require Xbox auth will kick the bot on join.

---

## Usage

Once running you will see:

```
mc-bot>
```

Type any command and press Enter.

### Commands

| Command | What it does |
|---|---|
| `/connect <host> [port] [username]` | Connect the bot to a Bedrock server |
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
  Connecting to play.myserver.net:19132 as "BuildBot"...
  Bot joined! Type /upload <file> to load a schematic.

mc-bot> /upload ~/Downloads/my_house.litematic
  Parsing my_house.litematic...
  Loaded 3,412 blocks.
  Build origin: (0, 64, 0). Change with /origin x y z

mc-bot> /origin 150 64 -200
  Build origin set to (150, 64, -200).

mc-bot> /build
  Starting build at (150, 64, -200). 3412 blocks to place.
  Building... 3412/3412 (100%)
  Build complete! 3412 blocks placed.
```

---

## Notes

- The bot must be opped on the server: `/op BuildBot`
- Java Edition block types with no Bedrock equivalent are skipped and listed after `/upload`
- Builds run at 50 blocks/second — adjust `BLOCKS_PER_TICK` and `TICK_INTERVAL_MS` in `bot.mjs` if needed
- Tested against Bedrock Dedicated Server 1.20+
