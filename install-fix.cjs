#!/usr/bin/env node
/**
 * Patches bedrock-protocol so that the RakNet backend falls back to the pure-JS
 * implementation (jsp-raknet) when the native binary (raknet-native) is not
 * available for the current platform.
 *
 * bedrock-protocol's createClient.js hard-codes:
 *
 *     require('./rak')('raknet-native')
 *
 * which skips the built-in fallback in rak.js.  Changing the call to
 *
 *     require('./rak')()
 *
 * lets rak.js try raknet-native first and silently fall back to jsp-raknet.
 *
 * This is needed on iOS (a-shell), Android (Termux), and any other platform
 * where no pre-built raknet-native binary is shipped.
 */

const fs = require("fs");
const path = require("path");

const target = path.join(
  __dirname,
  "node_modules",
  "bedrock-protocol",
  "src",
  "createClient.js"
);

if (!fs.existsSync(target)) {
  // bedrock-protocol not installed yet — nothing to patch
  process.exit(0);
}

const src = fs.readFileSync(target, "utf8");
const needle = "require('./rak')('raknet-native')";
const replacement = "require('./rak')()";

if (src.includes(needle)) {
  fs.writeFileSync(target, src.replace(needle, replacement), "utf8");
  console.log("[install-fix] Patched bedrock-protocol to allow RakNet fallback.");
} else if (src.includes(replacement)) {
  console.log("[install-fix] Already patched — nothing to do.");
} else {
  console.log("[install-fix] createClient.js has unexpected content; skipping patch.");
}
