#!/usr/bin/env python3
"""
Minecraft Bedrock Builder Bot — Python / a-shell edition

Uses Minecraft's built-in WebSocket protocol so it works on any device
with Python 3.10+ and a network connection (including a-shell on iOS).

Workflow
--------
1.  Run this script:  python3 bot.py
2.  In Minecraft (Bedrock), open chat and type:
        /wsserver ws://<this-device-ip>:<port>
3.  Use /upload, /origin, /build commands in the bot CLI.
"""

from __future__ import annotations

import asyncio
import gzip
import hashlib
import io
import json
import math
import os
import re
import signal
import socket
import struct
import sys
import threading
import time
import uuid as _uuid

# ─── Java → Bedrock block map ─────────────────────────────────────────────────
BLOCK_MAP: dict[str, str] = {
    "minecraft:air":"minecraft:air","minecraft:cave_air":"minecraft:air",
    "minecraft:stone":"minecraft:stone","minecraft:granite":"minecraft:stone",
    "minecraft:polished_granite":"minecraft:stone","minecraft:diorite":"minecraft:stone",
    "minecraft:polished_diorite":"minecraft:stone","minecraft:andesite":"minecraft:stone",
    "minecraft:polished_andesite":"minecraft:stone","minecraft:cobblestone":"minecraft:cobblestone",
    "minecraft:stone_bricks":"minecraft:stonebrick","minecraft:mossy_stone_bricks":"minecraft:stonebrick",
    "minecraft:cracked_stone_bricks":"minecraft:stonebrick","minecraft:chiseled_stone_bricks":"minecraft:stonebrick",
    "minecraft:cobblestone_stairs":"minecraft:stone_stairs","minecraft:stone_brick_stairs":"minecraft:stone_brick_stairs",
    "minecraft:cobblestone_wall":"minecraft:cobblestone_wall","minecraft:smooth_stone":"minecraft:smooth_stone",
    "minecraft:deepslate":"minecraft:deepslate","minecraft:cobbled_deepslate":"minecraft:cobbled_deepslate",
    "minecraft:polished_deepslate":"minecraft:polished_deepslate","minecraft:deepslate_bricks":"minecraft:deepslate_bricks",
    "minecraft:deepslate_tiles":"minecraft:deepslate_tiles","minecraft:chiseled_deepslate":"minecraft:chiseled_deepslate",
    "minecraft:grass_block":"minecraft:grass","minecraft:dirt":"minecraft:dirt",
    "minecraft:coarse_dirt":"minecraft:dirt","minecraft:podzol":"minecraft:podzol",
    "minecraft:mycelium":"minecraft:mycelium","minecraft:farmland":"minecraft:farmland",
    "minecraft:dirt_path":"minecraft:grass_path","minecraft:sand":"minecraft:sand",
    "minecraft:gravel":"minecraft:gravel","minecraft:sandstone":"minecraft:sandstone",
    "minecraft:smooth_sandstone":"minecraft:smooth_sandstone","minecraft:red_sandstone":"minecraft:red_sandstone",
    "minecraft:oak_log":"minecraft:log","minecraft:oak_planks":"minecraft:planks",
    "minecraft:oak_slab":"minecraft:wooden_slab","minecraft:oak_stairs":"minecraft:oak_stairs",
    "minecraft:oak_fence":"minecraft:fence","minecraft:oak_door":"minecraft:wooden_door",
    "minecraft:oak_trapdoor":"minecraft:trapdoor","minecraft:oak_leaves":"minecraft:leaves",
    "minecraft:spruce_log":"minecraft:log","minecraft:spruce_planks":"minecraft:planks",
    "minecraft:spruce_stairs":"minecraft:spruce_stairs","minecraft:spruce_door":"minecraft:spruce_door",
    "minecraft:spruce_trapdoor":"minecraft:spruce_trapdoor","minecraft:spruce_leaves":"minecraft:leaves",
    "minecraft:birch_log":"minecraft:log","minecraft:birch_planks":"minecraft:planks",
    "minecraft:birch_stairs":"minecraft:birch_stairs","minecraft:birch_door":"minecraft:birch_door",
    "minecraft:birch_trapdoor":"minecraft:birch_trapdoor","minecraft:birch_leaves":"minecraft:leaves",
    "minecraft:jungle_log":"minecraft:log","minecraft:jungle_planks":"minecraft:planks",
    "minecraft:jungle_stairs":"minecraft:jungle_stairs","minecraft:jungle_door":"minecraft:jungle_door",
    "minecraft:jungle_leaves":"minecraft:leaves","minecraft:acacia_log":"minecraft:log",
    "minecraft:acacia_planks":"minecraft:planks","minecraft:acacia_stairs":"minecraft:acacia_stairs",
    "minecraft:acacia_door":"minecraft:acacia_door","minecraft:acacia_leaves":"minecraft:leaves",
    "minecraft:dark_oak_log":"minecraft:log","minecraft:dark_oak_planks":"minecraft:planks",
    "minecraft:dark_oak_stairs":"minecraft:dark_oak_stairs","minecraft:dark_oak_door":"minecraft:dark_oak_door",
    "minecraft:dark_oak_leaves":"minecraft:leaves","minecraft:mangrove_log":"minecraft:mangrove_log",
    "minecraft:mangrove_planks":"minecraft:mangrove_planks","minecraft:cherry_log":"minecraft:cherry_log",
    "minecraft:cherry_planks":"minecraft:cherry_planks","minecraft:crimson_stem":"minecraft:crimson_stem",
    "minecraft:warped_stem":"minecraft:warped_stem","minecraft:crimson_planks":"minecraft:crimson_planks",
    "minecraft:warped_planks":"minecraft:warped_planks","minecraft:coal_ore":"minecraft:coal_ore",
    "minecraft:iron_ore":"minecraft:iron_ore","minecraft:gold_ore":"minecraft:gold_ore",
    "minecraft:diamond_ore":"minecraft:diamond_ore","minecraft:emerald_ore":"minecraft:emerald_ore",
    "minecraft:lapis_ore":"minecraft:lapis_ore","minecraft:redstone_ore":"minecraft:redstone_ore",
    "minecraft:copper_ore":"minecraft:copper_ore","minecraft:ancient_debris":"minecraft:ancient_debris",
    "minecraft:coal_block":"minecraft:coal_block","minecraft:iron_block":"minecraft:iron_block",
    "minecraft:gold_block":"minecraft:gold_block","minecraft:diamond_block":"minecraft:diamond_block",
    "minecraft:emerald_block":"minecraft:emerald_block","minecraft:lapis_block":"minecraft:lapis_block",
    "minecraft:redstone_block":"minecraft:redstone_block","minecraft:copper_block":"minecraft:copper_block",
    "minecraft:netherite_block":"minecraft:netherite_block","minecraft:quartz_block":"minecraft:quartz_block",
    "minecraft:glass":"minecraft:glass","minecraft:glass_pane":"minecraft:glass_pane",
    "minecraft:tinted_glass":"minecraft:tinted_glass",
    "minecraft:white_wool":"minecraft:wool","minecraft:orange_wool":"minecraft:wool",
    "minecraft:magenta_wool":"minecraft:wool","minecraft:light_blue_wool":"minecraft:wool",
    "minecraft:yellow_wool":"minecraft:wool","minecraft:lime_wool":"minecraft:wool",
    "minecraft:pink_wool":"minecraft:wool","minecraft:gray_wool":"minecraft:wool",
    "minecraft:light_gray_wool":"minecraft:wool","minecraft:cyan_wool":"minecraft:wool",
    "minecraft:purple_wool":"minecraft:wool","minecraft:blue_wool":"minecraft:wool",
    "minecraft:brown_wool":"minecraft:wool","minecraft:green_wool":"minecraft:wool",
    "minecraft:red_wool":"minecraft:wool","minecraft:black_wool":"minecraft:wool",
    "minecraft:white_concrete":"minecraft:concrete","minecraft:orange_concrete":"minecraft:concrete",
    "minecraft:magenta_concrete":"minecraft:concrete","minecraft:light_blue_concrete":"minecraft:concrete",
    "minecraft:yellow_concrete":"minecraft:concrete","minecraft:lime_concrete":"minecraft:concrete",
    "minecraft:pink_concrete":"minecraft:concrete","minecraft:gray_concrete":"minecraft:concrete",
    "minecraft:light_gray_concrete":"minecraft:concrete","minecraft:cyan_concrete":"minecraft:concrete",
    "minecraft:purple_concrete":"minecraft:concrete","minecraft:blue_concrete":"minecraft:concrete",
    "minecraft:brown_concrete":"minecraft:concrete","minecraft:green_concrete":"minecraft:concrete",
    "minecraft:red_concrete":"minecraft:concrete","minecraft:black_concrete":"minecraft:concrete",
    "minecraft:white_concrete_powder":"minecraft:concrete_powder","minecraft:yellow_concrete_powder":"minecraft:concrete_powder",
    "minecraft:gray_concrete_powder":"minecraft:concrete_powder","minecraft:black_concrete_powder":"minecraft:concrete_powder",
    "minecraft:terracotta":"minecraft:hardened_clay","minecraft:white_terracotta":"minecraft:hardened_clay",
    "minecraft:orange_terracotta":"minecraft:stained_hardened_clay","minecraft:yellow_terracotta":"minecraft:stained_hardened_clay",
    "minecraft:gray_terracotta":"minecraft:stained_hardened_clay","minecraft:blue_terracotta":"minecraft:stained_hardened_clay",
    "minecraft:red_terracotta":"minecraft:stained_hardened_clay","minecraft:brown_terracotta":"minecraft:stained_hardened_clay",
    "minecraft:black_terracotta":"minecraft:stained_hardened_clay","minecraft:green_terracotta":"minecraft:stained_hardened_clay",
    "minecraft:white_glazed_terracotta":"minecraft:white_glazed_terracotta",
    "minecraft:orange_glazed_terracotta":"minecraft:orange_glazed_terracotta",
    "minecraft:bricks":"minecraft:brick_block","minecraft:brick_stairs":"minecraft:brick_stairs",
    "minecraft:brick_wall":"minecraft:brick_wall","minecraft:nether_bricks":"minecraft:nether_brick",
    "minecraft:red_nether_bricks":"minecraft:red_nether_brick","minecraft:nether_brick_fence":"minecraft:nether_brick_fence",
    "minecraft:nether_brick_stairs":"minecraft:nether_brick_stairs",
    "minecraft:prismarine":"minecraft:prismarine","minecraft:sea_lantern":"minecraft:sea_lantern",
    "minecraft:end_stone":"minecraft:end_stone","minecraft:end_stone_bricks":"minecraft:end_bricks",
    "minecraft:purpur_block":"minecraft:purpur_block","minecraft:purpur_pillar":"minecraft:purpur_block",
    "minecraft:purpur_stairs":"minecraft:purpur_stairs","minecraft:netherrack":"minecraft:netherrack",
    "minecraft:soul_sand":"minecraft:soul_sand","minecraft:soul_soil":"minecraft:soul_soil",
    "minecraft:magma_block":"minecraft:magma","minecraft:blackstone":"minecraft:blackstone",
    "minecraft:polished_blackstone":"minecraft:polished_blackstone",
    "minecraft:polished_blackstone_bricks":"minecraft:polished_blackstone_bricks",
    "minecraft:basalt":"minecraft:basalt","minecraft:polished_basalt":"minecraft:polished_basalt",
    "minecraft:obsidian":"minecraft:obsidian","minecraft:crying_obsidian":"minecraft:crying_obsidian",
    "minecraft:bedrock":"minecraft:bedrock","minecraft:clay":"minecraft:clay",
    "minecraft:ice":"minecraft:ice","minecraft:packed_ice":"minecraft:packed_ice",
    "minecraft:blue_ice":"minecraft:blue_ice","minecraft:snow_block":"minecraft:snow",
    "minecraft:moss_block":"minecraft:moss_block","minecraft:amethyst_block":"minecraft:amethyst_block",
    "minecraft:calcite":"minecraft:calcite","minecraft:tuff":"minecraft:tuff",
    "minecraft:dripstone_block":"minecraft:dripstone_block","minecraft:sculk":"minecraft:sculk",
    "minecraft:glowstone":"minecraft:glowstone","minecraft:torch":"minecraft:torch",
    "minecraft:soul_torch":"minecraft:soul_torch","minecraft:lantern":"minecraft:lantern",
    "minecraft:soul_lantern":"minecraft:soul_lantern","minecraft:shroomlight":"minecraft:shroomlight",
    "minecraft:jack_o_lantern":"minecraft:lit_pumpkin",
    "minecraft:crafting_table":"minecraft:crafting_table","minecraft:furnace":"minecraft:furnace",
    "minecraft:blast_furnace":"minecraft:blast_furnace","minecraft:smoker":"minecraft:smoker",
    "minecraft:chest":"minecraft:chest","minecraft:trapped_chest":"minecraft:trapped_chest",
    "minecraft:ender_chest":"minecraft:ender_chest","minecraft:barrel":"minecraft:barrel",
    "minecraft:bookshelf":"minecraft:bookshelf","minecraft:enchanting_table":"minecraft:enchanting_table",
    "minecraft:anvil":"minecraft:anvil","minecraft:brewing_stand":"minecraft:brewing_stand",
    "minecraft:beacon":"minecraft:beacon","minecraft:jukebox":"minecraft:jukebox",
    "minecraft:note_block":"minecraft:noteblock","minecraft:tnt":"minecraft:tnt",
    "minecraft:dispenser":"minecraft:dispenser","minecraft:dropper":"minecraft:dropper",
    "minecraft:hopper":"minecraft:hopper","minecraft:observer":"minecraft:observer",
    "minecraft:piston":"minecraft:piston","minecraft:sticky_piston":"minecraft:sticky_piston",
    "minecraft:redstone_lamp":"minecraft:redstone_lamp","minecraft:ladder":"minecraft:ladder",
    "minecraft:iron_bars":"minecraft:iron_bars","minecraft:chain":"minecraft:chain",
    "minecraft:hay_block":"minecraft:hay_block","minecraft:pumpkin":"minecraft:pumpkin",
    "minecraft:carved_pumpkin":"minecraft:carved_pumpkin","minecraft:melon":"minecraft:melon_block",
    "minecraft:cactus":"minecraft:cactus","minecraft:bamboo":"minecraft:bamboo",
    "minecraft:dried_kelp_block":"minecraft:dried_kelp_block","minecraft:cut_copper":"minecraft:cut_copper",
    "minecraft:waxed_cut_copper":"minecraft:waxed_cut_copper","minecraft:target":"minecraft:target",
    "minecraft:bell":"minecraft:bell","minecraft:loom":"minecraft:loom",
    "minecraft:cartography_table":"minecraft:cartography_table","minecraft:fletching_table":"minecraft:fletching_table",
    "minecraft:smithing_table":"minecraft:smithing_table","minecraft:stonecutter":"minecraft:stonecutter_block",
    "minecraft:grindstone":"minecraft:grindstone","minecraft:lectern":"minecraft:lectern",
    "minecraft:composter":"minecraft:composter","minecraft:respawn_anchor":"minecraft:respawn_anchor",
    "minecraft:mud":"minecraft:mud","minecraft:packed_mud":"minecraft:packed_mud",
    "minecraft:mud_bricks":"minecraft:mud_bricks",
}

def to_bedrock_block(java: str) -> str | None:
    return BLOCK_MAP.get(java)


# ─── Pure-Python NBT parser (minimal, for .litematic files) ────────────────────
TAG_END       = 0
TAG_BYTE      = 1
TAG_SHORT     = 2
TAG_INT       = 3
TAG_LONG      = 4
TAG_FLOAT     = 5
TAG_DOUBLE    = 6
TAG_BYTE_ARR  = 7
TAG_STRING    = 8
TAG_LIST      = 9
TAG_COMPOUND  = 10
TAG_INT_ARR   = 11
TAG_LONG_ARR  = 12

def _read_nbt_tag(buf: io.BytesIO, tag_type: int):
    if tag_type == TAG_BYTE:
        return struct.unpack(">b", buf.read(1))[0]
    if tag_type == TAG_SHORT:
        return struct.unpack(">h", buf.read(2))[0]
    if tag_type == TAG_INT:
        return struct.unpack(">i", buf.read(4))[0]
    if tag_type == TAG_LONG:
        return struct.unpack(">q", buf.read(8))[0]
    if tag_type == TAG_FLOAT:
        return struct.unpack(">f", buf.read(4))[0]
    if tag_type == TAG_DOUBLE:
        return struct.unpack(">d", buf.read(8))[0]
    if tag_type == TAG_BYTE_ARR:
        length = struct.unpack(">i", buf.read(4))[0]
        return buf.read(length)
    if tag_type == TAG_STRING:
        length = struct.unpack(">H", buf.read(2))[0]
        return buf.read(length).decode("utf-8", errors="replace")
    if tag_type == TAG_LIST:
        item_type = struct.unpack(">b", buf.read(1))[0]
        count = struct.unpack(">i", buf.read(4))[0]
        return [_read_nbt_tag(buf, item_type) for _ in range(count)]
    if tag_type == TAG_COMPOUND:
        result: dict = {}
        while True:
            child_type = struct.unpack(">b", buf.read(1))[0]
            if child_type == TAG_END:
                break
            name_len = struct.unpack(">H", buf.read(2))[0]
            name = buf.read(name_len).decode("utf-8", errors="replace")
            result[name] = (child_type, _read_nbt_tag(buf, child_type))
        return result
    if tag_type == TAG_INT_ARR:
        length = struct.unpack(">i", buf.read(4))[0]
        return list(struct.unpack(f">{length}i", buf.read(4 * length)))
    if tag_type == TAG_LONG_ARR:
        length = struct.unpack(">i", buf.read(4))[0]
        return list(struct.unpack(f">{length}q", buf.read(8 * length)))
    raise ValueError(f"Unknown NBT tag type: {tag_type}")


def parse_nbt(data: bytes) -> dict:
    buf = io.BytesIO(data)
    root_type = struct.unpack(">b", buf.read(1))[0]
    if root_type != TAG_COMPOUND:
        raise ValueError("Expected root compound tag")
    name_len = struct.unpack(">H", buf.read(2))[0]
    buf.read(name_len)  # root name (usually empty)
    return _read_nbt_tag(buf, TAG_COMPOUND)


def _nbt_val(node, *path):
    """Walk into an NBT compound tree following dotted path components."""
    cur = node
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
        if isinstance(cur, tuple):
            cur = cur[1]  # (tag_type, value) pair
    return cur


# ─── Litematic parser ──────────────────────────────────────────────────────────
def parse_litematic(file_path: str):
    with open(file_path, "rb") as f:
        raw = f.read()

    # litematic files are gzip-compressed NBT
    try:
        data = gzip.decompress(raw)
    except Exception:
        data = raw  # maybe not compressed

    root = parse_nbt(data)

    regions = _nbt_val(root, "Regions")
    if regions is None:
        raise ValueError("No Regions tag found. Is this a valid .litematic file?")

    blocks: list[dict] = []
    unmapped: set[str] = set()

    for _region_name, region_data in regions.items():
        if isinstance(region_data, tuple):
            region_data = region_data[1]

        pos = _nbt_val(region_data, "Position")
        size = _nbt_val(region_data, "Size")
        palette = _nbt_val(region_data, "BlockStatePalette")
        states_entry = region_data.get("BlockStates")

        if pos is None or size is None or palette is None or states_entry is None:
            continue

        states_data = states_entry[1] if isinstance(states_entry, tuple) else states_entry

        px = _nbt_val(pos, "x") or 0
        py = _nbt_val(pos, "y") or 0
        pz = _nbt_val(pos, "z") or 0
        sx = abs(_nbt_val(size, "x") or 0)
        sy = abs(_nbt_val(size, "y") or 0)
        sz = abs(_nbt_val(size, "z") or 0)

        # Extract block names from palette
        names: list[str] = []
        for entry in palette:
            if isinstance(entry, dict):
                name_val = _nbt_val(entry, "Name")
                names.append(str(name_val) if name_val else "minecraft:air")
            else:
                names.append("minecraft:air")

        pal_size = len(names)
        bpb = max(math.ceil(math.log2(pal_size)) if pal_size > 1 else 1, 2)
        bpl = 64 // bpb
        mask = (1 << bpb) - 1
        total = sx * sy * sz

        for i in range(total):
            li = i // bpl
            bit = (i % bpl) * bpb
            lv = states_data[li] if li < len(states_data) else 0
            # Handle signed longs
            if lv < 0:
                lv += (1 << 64)
            pi = (lv >> bit) & mask
            java = names[pi] if pi < len(names) else "minecraft:air"
            if java == "minecraft:air":
                continue
            bed = to_bedrock_block(java)
            if not bed or bed == "minecraft:air":
                unmapped.add(java)
                continue
            bx = i % sx
            bz = (i // sx) % sz
            by = i // (sx * sz)
            blocks.append({"x": px + bx, "y": py + by, "z": pz + bz, "block": bed})

    return blocks, list(unmapped)


# ─── Minimal WebSocket server (RFC 6455, no external deps) ─────────────────────
WS_MAGIC = b"258EAFA5-E914-47DA-95CA-5AB0D141E3E2"


def _ws_accept_key(key: str) -> str:
    h = hashlib.sha1(key.encode() + WS_MAGIC).digest()
    import base64
    return base64.b64encode(h).decode()


def _ws_encode_frame(payload: bytes, opcode: int = 0x1) -> bytes:
    frame = bytearray()
    frame.append(0x80 | opcode)  # FIN + opcode
    length = len(payload)
    if length < 126:
        frame.append(length)
    elif length < 65536:
        frame.append(126)
        frame.extend(struct.pack(">H", length))
    else:
        frame.append(127)
        frame.extend(struct.pack(">Q", length))
    frame.extend(payload)
    return bytes(frame)


async def _ws_read_frame(reader: asyncio.StreamReader) -> tuple[int, bytes] | None:
    try:
        hdr = await reader.readexactly(2)
    except (asyncio.IncompleteReadError, ConnectionError):
        return None
    opcode = hdr[0] & 0x0F
    masked = bool(hdr[1] & 0x80)
    length = hdr[1] & 0x7F
    if length == 126:
        length = struct.unpack(">H", await reader.readexactly(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", await reader.readexactly(8))[0]
    mask_key = await reader.readexactly(4) if masked else None
    data = await reader.readexactly(length)
    if mask_key:
        data = bytes(b ^ mask_key[i % 4] for i, b in enumerate(data))
    return opcode, data


# ─── Minecraft WebSocket protocol ─────────────────────────────────────────────
class MinecraftWS:
    """Manages one Minecraft WebSocket connection."""

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.connected = True
        self._pending: dict[str, asyncio.Future] = {}

    async def send_json(self, obj: dict):
        payload = json.dumps(obj).encode()
        self.writer.write(_ws_encode_frame(payload))
        await self.writer.drain()

    async def send_command(self, cmd: str) -> dict | None:
        rid = str(_uuid.uuid4())
        msg = {
            "header": {
                "version": 1,
                "requestId": rid,
                "messagePurpose": "commandRequest",
                "messageType": "commandRequest",
            },
            "body": {
                "commandLine": cmd,
            },
        }
        fut: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[rid] = fut
        await self.send_json(msg)
        try:
            return await asyncio.wait_for(fut, timeout=5.0)
        except asyncio.TimeoutError:
            self._pending.pop(rid, None)
            return None

    async def subscribe(self, event_name: str):
        msg = {
            "header": {
                "version": 1,
                "requestId": str(_uuid.uuid4()),
                "messagePurpose": "subscribe",
                "messageType": "commandRequest",
            },
            "body": {
                "eventName": event_name,
            },
        }
        await self.send_json(msg)

    async def recv_loop(self):
        while self.connected:
            result = await _ws_read_frame(self.reader)
            if result is None:
                self.connected = False
                break
            opcode, data = result
            if opcode == 0x8:  # close
                self.connected = False
                break
            if opcode == 0x9:  # ping
                self.writer.write(_ws_encode_frame(data, opcode=0xA))
                await self.writer.drain()
                continue
            if opcode in (0x1, 0x2):  # text / binary
                try:
                    msg = json.loads(data)
                except Exception:
                    continue
                purpose = msg.get("header", {}).get("messagePurpose", "")
                rid = msg.get("header", {}).get("requestId", "")
                if purpose == "commandResponse" and rid in self._pending:
                    self._pending.pop(rid).set_result(msg.get("body"))
                elif purpose == "event":
                    pass  # events can be handled later if needed

    def close(self):
        self.connected = False
        try:
            self.writer.write(_ws_encode_frame(b"", opcode=0x8))
            self.writer.close()
        except Exception:
            pass


# ─── Bot state ─────────────────────────────────────────────────────────────────
class BotState:
    def __init__(self):
        self.ws: MinecraftWS | None = None
        self.blocks: list[dict] = []
        self.queue: list[dict] = []
        self.unmapped: list[str] = []
        self.placed = 0
        self.total = 0
        self.ox = 0
        self.oy = 64
        self.oz = 0
        self.building = False
        self.build_task: asyncio.Task | None = None
        self.schematic_path: str | None = None
        self.server: asyncio.AbstractServer | None = None
        self.port = 19131
        self.loop: asyncio.AbstractEventLoop | None = None

state = BotState()


# ─── Build loop ────────────────────────────────────────────────────────────────
async def build_loop():
    BLOCKS_PER_BATCH = 5
    TICK_MS = 100
    while state.building and state.ws and state.ws.connected and state.queue:
        for _ in range(BLOCKS_PER_BATCH):
            if not state.queue or not state.building:
                break
            b = state.queue.pop(0)
            bare = b["block"].replace("minecraft:", "")
            x = state.ox + b["x"]
            y = state.oy + b["y"]
            z = state.oz + b["z"]
            await state.ws.send_command(f"setblock {x} {y} {z} {bare}")
            state.placed += 1
            if state.placed % 50 == 0:
                pct = round(state.placed / state.total * 100)
                sys.stdout.write(f"\r  Building... {state.placed}/{state.total} ({pct}%)")
                sys.stdout.flush()
        await asyncio.sleep(TICK_MS / 1000)

    if not state.queue and state.building:
        state.building = False
        print(f"\nBuild complete! {state.placed} blocks placed.")


# ─── WebSocket server handler ─────────────────────────────────────────────────
async def handle_ws_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # Read HTTP upgrade request
    request_line = b""
    headers: dict[str, str] = {}
    while True:
        line = await reader.readline()
        if line == b"\r\n" or line == b"\n":
            break
        if not request_line:
            request_line = line
        else:
            if b":" in line:
                k, v = line.decode().split(":", 1)
                headers[k.strip().lower()] = v.strip()

    ws_key = headers.get("sec-websocket-key", "")
    if not ws_key:
        writer.close()
        return

    accept = _ws_accept_key(ws_key)
    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n"
        "\r\n"
    )
    writer.write(response.encode())
    await writer.drain()

    ws = MinecraftWS(reader, writer)

    if state.ws and state.ws.connected:
        state.ws.close()

    state.ws = ws
    print("\nMinecraft client connected!")
    print("mc-bot> ", end="", flush=True)

    try:
        await ws.recv_loop()
    except Exception:
        pass
    finally:
        if state.ws is ws:
            print("\nMinecraft client disconnected.")
            state.ws = None
            print("mc-bot> ", end="", flush=True)


# ─── CLI commands ──────────────────────────────────────────────────────────────
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


async def cmd_listen(args: list[str]):
    port = int(args[0]) if args else 19131
    state.port = port

    if state.server:
        state.server.close()
        await state.server.wait_closed()

    state.server = await asyncio.start_server(handle_ws_client, "0.0.0.0", port)
    ip = get_local_ip()
    print(f"WebSocket server listening on port {port}")
    print(f"In Minecraft, open chat and type:")
    print(f"    /wsserver ws://{ip}:{port}")
    print(f"    (or /connect ws://{ip}:{port})")


async def cmd_upload(args: list[str]):
    file_path = " ".join(args)
    if not file_path:
        print("Usage: /upload <path/to/file.litematic>")
        return
    resolved = os.path.abspath(os.path.expanduser(file_path))
    if not os.path.exists(resolved):
        print(f"File not found: {resolved}")
        return

    print(f"Parsing {os.path.basename(resolved)}...")
    try:
        blocks, unmapped = parse_litematic(resolved)
        state.blocks = blocks
        state.queue = list(blocks)
        state.total = len(blocks)
        state.placed = 0
        state.schematic_path = resolved
        state.unmapped = unmapped

        print(f"Loaded {len(blocks)} blocks.")
        if unmapped:
            shown = unmapped[:5]
            extra = f"..." if len(unmapped) > 5 else ""
            print(f"  ({len(unmapped)} Java-only block type(s) skipped: {', '.join(shown)}{extra})")
        print(f"Build origin: ({state.ox}, {state.oy}, {state.oz}). Change with /origin x y z")
        print("Use /build to start.")
    except Exception as e:
        print(f"Failed to parse file: {e}")


def cmd_origin(args: list[str]):
    try:
        x, y, z = int(args[0]), int(args[1]), int(args[2])
    except (IndexError, ValueError):
        print("Usage: /origin <x> <y> <z>")
        return
    state.ox, state.oy, state.oz = x, y, z
    print(f"Build origin set to ({x}, {y}, {z}).")


async def cmd_build():
    if not state.ws or not state.ws.connected:
        print("No Minecraft client connected. Use /listen first, then /wsserver in-game.")
        return
    if not state.blocks:
        print("No schematic loaded. Use /upload first.")
        return
    if state.building:
        print("Already building. Use /pause to pause.")
        return
    if not state.queue:
        state.queue = list(state.blocks)
        state.placed = 0
    print(f"Starting build at ({state.ox}, {state.oy}, {state.oz}). {len(state.queue)} blocks to place.")
    state.building = True
    state.build_task = asyncio.create_task(build_loop())


def cmd_status():
    connected = state.ws is not None and state.ws.connected
    print(f"  Connected : {'yes' if connected else 'no'}")
    sch = os.path.basename(state.schematic_path) if state.schematic_path else "none"
    print(f"  Schematic : {sch}" + (f" ({state.total} blocks)" if state.schematic_path else ""))
    print(f"  Origin    : ({state.ox}, {state.oy}, {state.oz})")
    if state.building:
        print(f"  Building  : yes — {state.placed}/{state.total}")
    elif state.placed > 0:
        print(f"  Building  : paused at {state.placed}/{state.total}")
    else:
        print(f"  Building  : no")
    print(f"  Server    : {'listening on port ' + str(state.port) if state.server else 'not started'}")


def cmd_pause():
    if not state.building:
        print("Not currently building.")
        return
    state.building = False
    print(f"Paused at {state.placed}/{state.total}. Use /resume to continue.")


async def cmd_resume():
    if state.building:
        print("Already building.")
        return
    if not state.queue:
        print("Nothing to resume.")
        return
    if not state.ws or not state.ws.connected:
        print("No Minecraft client connected.")
        return
    print(f"Resuming from {state.placed}/{state.total}...")
    state.building = True
    state.build_task = asyncio.create_task(build_loop())


def cmd_stop():
    state.building = False
    if state.build_task:
        state.build_task.cancel()
        state.build_task = None
    state.queue = list(state.blocks)
    state.placed = 0
    print("Build stopped and reset. Use /build to start over.")


def print_help():
    print("""
  Commands:
    /listen [port]                      Start WebSocket server (default 19131)
    /status                             Show connection and build info
    /upload <file>                      Load a .litematic schematic file
    /origin <x> <y> <z>                Set world coordinates to build at
    /build                              Start placing blocks
    /pause                              Pause the current build
    /resume                             Resume a paused build
    /stop                               Stop and reset the build
    /help                               Show this list
    /quit                               Disconnect and exit

  To connect Minecraft to this bot:
    1. Run /listen in this terminal
    2. In Minecraft chat, type:  /wsserver ws://<your-ip>:<port>
""")


async def handle_line(line: str):
    parts = line.strip().split()
    if not parts:
        return
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd == "/listen":
        await cmd_listen(args)
    elif cmd == "/upload":
        await cmd_upload(args)
    elif cmd == "/origin":
        cmd_origin(args)
    elif cmd == "/build":
        await cmd_build()
    elif cmd == "/status":
        cmd_status()
    elif cmd == "/pause":
        cmd_pause()
    elif cmd == "/resume":
        await cmd_resume()
    elif cmd == "/stop":
        cmd_stop()
    elif cmd == "/help":
        print_help()
    elif cmd == "/quit":
        if state.ws:
            state.ws.close()
        if state.server:
            state.server.close()
        print("Goodbye.")
        sys.exit(0)
    else:
        print(f"Unknown command: {cmd}. Type /help for the list.")


# ─── Async stdin reader ───────────────────────────────────────────────────────
async def stdin_reader():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    print()
    print("  Minecraft Bedrock Builder Bot (Python)")
    print("  ----------------------------------------")
    print_help()

    # Auto-start the WebSocket server
    await cmd_listen([])

    # Read stdin asynchronously
    try:
        reader = await stdin_reader()
    except Exception:
        # Fallback for environments where async stdin doesn't work
        reader = None

    if reader:
        while True:
            sys.stdout.write("mc-bot> ")
            sys.stdout.flush()
            try:
                line_bytes = await reader.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode(errors="replace").strip()
                if line:
                    await handle_line(line)
            except (EOFError, KeyboardInterrupt):
                break
    else:
        # Sync fallback
        while True:
            try:
                line = input("mc-bot> ")
                if line.strip():
                    await handle_line(line.strip())
            except (EOFError, KeyboardInterrupt):
                break

    print("\nGoodbye.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye.")
