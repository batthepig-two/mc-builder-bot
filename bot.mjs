#!/usr/bin/env node
/**
 * Minecraft Bedrock Builder Bot — Interactive CLI
 *
 * Commands:
 *   /connect <host> [port] [username]
 *   /status
 *   /upload <path-to-.litematic>
 *   /origin <x> <y> <z>
 *   /build
 *   /pause
 *   /resume
 *   /stop
 *   /help
 *   /quit
 */

import readline from "node:readline";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

function loadBdp() {
  try { return require("bedrock-protocol"); }
  catch { fatal("bedrock-protocol not found.\nRun: npm install  (inside the mc-builder-bot folder)"); }
}
function loadNbt() {
  try { return require("prismarine-nbt"); }
  catch { fatal("prismarine-nbt not found.\nRun: npm install  (inside the mc-builder-bot folder)"); }
}
function fatal(msg) { console.error("\n[ERROR] " + msg + "\n"); process.exit(1); }

// ─── Java → Bedrock block map ─────────────────────────────────────────────────
const BLOCK_MAP = {
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
};

function toBedrockBlock(java) {
  return BLOCK_MAP[java] || null;
}

// ─── Litematic parser ─────────────────────────────────────────────────────────
async function parseLitematic(filePath) {
  const { promisify } = await import("node:util");
  const nbt = loadNbt();
  const parseNbt = promisify(nbt.parse);
  const buf = fs.readFileSync(filePath);
  const result = await parseNbt(buf);
  const root = result.parsed;

  const regions = root?.value?.Regions;
  if (!regions || regions.type !== "compound")
    throw new Error("No Regions tag found. Is this a valid .litematic file?");

  const blocks = [];
  const unmapped = new Set();

  for (const [, region] of Object.entries(regions.value)) {
    const pos = region.value.Position?.value;
    const size = region.value.Size?.value;
    const palette = region.value.BlockStatePalette?.value;
    const statesTag = region.value.BlockStates;
    if (!pos || !size || !palette || !statesTag) continue;

    const px = Number(pos.x?.value ?? 0);
    const py = Number(pos.y?.value ?? 0);
    const pz = Number(pos.z?.value ?? 0);
    const sx = Math.abs(Number(size.x?.value ?? 0));
    const sy = Math.abs(Number(size.y?.value ?? 0));
    const sz = Math.abs(Number(size.z?.value ?? 0));

    const names = palette.map(e => String(e.value?.Name?.value ?? "minecraft:air"));
    const palSize = names.length;
    const bpb = Math.max(Math.ceil(Math.log2(palSize)), 2);
    const bpl = Math.floor(64 / bpb);
    const mask = BigInt((1 << bpb) - 1);
    const longs = statesTag.value;
    const total = sx * sy * sz;

    for (let i = 0; i < total; i++) {
      const li = Math.floor(i / bpl);
      const bit = (i % bpl) * bpb;
      const lv = li < longs.length ? BigInt(longs[li]) : 0n;
      const pi = Number((lv >> BigInt(bit)) & mask);
      const java = names[pi] || "minecraft:air";
      if (java === "minecraft:air") continue;
      const bed = toBedrockBlock(java);
      if (!bed || bed === "minecraft:air") { unmapped.add(java); continue; }
      const bx = i % sx;
      const bz = Math.floor(i / sx) % sz;
      const by = Math.floor(i / (sx * sz));
      blocks.push({ x: px + bx, y: py + by, z: pz + bz, block: bed });
    }
  }

  return { blocks, unmapped: [...unmapped] };
}

// ─── Bot state ────────────────────────────────────────────────────────────────
const state = {
  client: null, connected: false,
  host: null, port: null, username: null,
  blocks: [], queue: [], unmapped: [],
  placed: 0, total: 0,
  ox: 0, oy: 64, oz: 0,
  building: false, timer: null,
  schematicPath: null,
};

function sendCmd(cmd) {
  if (!state.client) return;
  state.client.queue("command_request", {
    command: cmd,
    origin: { type: 5, uuid: "", request_id: "" },
    internal: false, version: 66,
  });
}

function startBuilding() {
  if (state.timer) clearInterval(state.timer);
  state.building = true;
  state.timer = setInterval(() => {
    if (!state.building || !state.client) { clearInterval(state.timer); state.timer = null; return; }
    for (let i = 0; i < 5; i++) {
      const b = state.queue.shift();
      if (!b) {
        clearInterval(state.timer); state.timer = null; state.building = false;
        print("\nBuild complete! " + state.placed + " blocks placed.");
        prompt();
        return;
      }
      const bare = b.block.replace("minecraft:", "");
      sendCmd("setblock " + (state.ox + b.x) + " " + (state.oy + b.y) + " " + (state.oz + b.z) + " " + bare);
      state.placed++;
      if (state.placed % 50 === 0) {
        const pct = Math.round((state.placed / state.total) * 100);
        process.stdout.write("\r  Building... " + state.placed + "/" + state.total + " (" + pct + "%)");
      }
    }
  }, 100);
}

// ─── CLI ──────────────────────────────────────────────────────────────────────
const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: true });
let promptActive = false;

function print(msg) {
  if (promptActive) process.stdout.write("\r\x1b[K");
  console.log(msg);
  if (promptActive) prompt(true);
}

function prompt(silent = false) {
  promptActive = true;
  if (!silent) rl.setPrompt("mc-bot> ");
  rl.prompt(true);
}

function printHelp() {
  print([
    "",
    "  Commands:",
    "    /connect <host> [port] [username]   Connect the bot to a Bedrock server",
    "    /status                             Show connection and build info",
    "    /upload <file>                      Load a .litematic schematic file",
    "    /origin <x> <y> <z>                Set world coordinates to build at",
    "    /build                              Start placing blocks",
    "    /pause                              Pause the current build",
    "    /resume                             Resume a paused build",
    "    /stop                               Stop and reset the build",
    "    /help                               Show this list",
    "    /quit                               Disconnect and exit",
    "",
  ].join("\n"));
}

async function handleConnect(args) {
  const [host, portStr, username] = args;
  if (!host) { print("Usage: /connect <host> [port] [username]"); return; }
  const port = portStr ? parseInt(portStr) : 19132;
  const user = username || "BuildBot";

  if (state.client) {
    try { state.client.disconnect(); } catch {}
    state.client = null; state.connected = false;
  }

  state.host = host; state.port = port; state.username = user;
  print("Connecting to " + host + ":" + port + " as \"" + user + "\"...");

  const bdp = loadBdp();
  const client = bdp.createClient({ host, port, username: user, offline: true });
  state.client = client;

  client.on("spawn", () => {
    state.connected = true;
    print("\nBot joined! Type /upload <file> to load a schematic.");
    prompt();
  });
  client.on("error", err => {
    state.connected = false;
    print("\nConnection error: " + err.message);
    prompt();
  });
  client.on("kick", reason => {
    state.connected = false;
    print("\nKicked: " + JSON.stringify(reason));
    prompt();
  });
  client.on("close", () => {
    if (state.connected) {
      state.connected = false;
      print("\nDisconnected from server.");
      prompt();
    }
  });
}

async function handleUpload(args) {
  const filePath = args.join(" ");
  if (!filePath) { print("Usage: /upload <path/to/file.litematic>"); return; }
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) { print("File not found: " + resolved); return; }

  print("Parsing " + path.basename(resolved) + "...");
  try {
    const { blocks, unmapped } = await parseLitematic(resolved);
    state.blocks = blocks; state.queue = [...blocks];
    state.total = blocks.length; state.placed = 0;
    state.schematicPath = resolved; state.unmapped = unmapped;

    print("Loaded " + blocks.length + " blocks.");
    if (unmapped.length)
      print("  (" + unmapped.length + " Java-only block type(s) skipped: " + unmapped.slice(0, 5).join(", ") + (unmapped.length > 5 ? "..." : "") + ")");
    print("Build origin: (" + state.ox + ", " + state.oy + ", " + state.oz + "). Change with /origin x y z");
    print("Use /build to start.");
  } catch (err) {
    print("Failed to parse file: " + err.message);
  }
}

function handleOrigin(args) {
  const [x, y, z] = args.map(Number);
  if ([x, y, z].some(isNaN)) { print("Usage: /origin <x> <y> <z>"); return; }
  state.ox = x; state.oy = y; state.oz = z;
  print("Build origin set to (" + x + ", " + y + ", " + z + ").");
}

function handleBuild() {
  if (!state.connected) { print("Not connected. Use /connect first."); return; }
  if (!state.blocks.length) { print("No schematic loaded. Use /upload first."); return; }
  if (state.building) { print("Already building. Use /pause to pause."); return; }
  if (state.queue.length === 0) { state.queue = [...state.blocks]; state.placed = 0; }
  print("Starting build at (" + state.ox + ", " + state.oy + ", " + state.oz + "). " + state.queue.length + " blocks to place.");
  startBuilding();
}

function handleStatus() {
  print("  Connected : " + (state.connected ? "yes (" + state.host + ":" + state.port + " as " + state.username + ")" : "no"));
  print("  Schematic : " + (state.schematicPath ? path.basename(state.schematicPath) + " (" + state.total + " blocks)" : "none"));
  print("  Origin    : (" + state.ox + ", " + state.oy + ", " + state.oz + ")");
  print("  Building  : " + (state.building ? "yes — " + state.placed + "/" + state.total : state.placed > 0 ? "paused at " + state.placed + "/" + state.total : "no"));
}

function handlePause() {
  if (!state.building) { print("Not currently building."); return; }
  clearInterval(state.timer); state.timer = null; state.building = false;
  print("Paused at " + state.placed + "/" + state.total + ". Use /resume to continue.");
}

function handleResume() {
  if (state.building) { print("Already building."); return; }
  if (!state.queue.length) { print("Nothing to resume."); return; }
  if (!state.connected) { print("Not connected."); return; }
  print("Resuming from " + state.placed + "/" + state.total + "...");
  startBuilding();
}

function handleStop() {
  if (state.timer) { clearInterval(state.timer); state.timer = null; }
  state.building = false; state.queue = [...state.blocks]; state.placed = 0;
  print("Build stopped and reset. Use /build to start over.");
}

async function handleQuit() {
  if (state.timer) clearInterval(state.timer);
  if (state.client) { try { state.client.disconnect(); } catch {} }
  print("Goodbye.");
  process.exit(0);
}

// ─── Main ─────────────────────────────────────────────────────────────────────
console.log("");
console.log("  Minecraft Bedrock Builder Bot");
console.log("  --------------------------------");
printHelp();
prompt();

rl.on("line", async (line) => {
  promptActive = false;
  const trimmed = line.trim();
  if (!trimmed) { prompt(); return; }
  const [cmd, ...args] = trimmed.split(/\s+/);
  switch (cmd.toLowerCase()) {
    case "/connect":  await handleConnect(args); break;
    case "/upload":   await handleUpload(args); break;
    case "/origin":   handleOrigin(args); break;
    case "/build":    handleBuild(); break;
    case "/status":   handleStatus(); break;
    case "/pause":    handlePause(); break;
    case "/resume":   handleResume(); break;
    case "/stop":     handleStop(); break;
    case "/help":     printHelp(); break;
    case "/quit":     await handleQuit(); return;
    default: print("Unknown command: " + cmd + ". Type /help for the list.");
  }
  if (!state.building) prompt();
});

rl.on("close", () => process.exit(0));
