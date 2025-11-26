# Cardano CLI Setup

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Cardano CLI Setup

**Last updated:** 2025-11-26

This guide explains how to install [`cardano-cli`](./glossary.md#cardano-cli), configure it for the [testnet](./glossary.md#testnet) and [mainnet](./glossary.md#mainnet) networks used by this project, and verify that your environment works end to end.

## 1. Prerequisites

- macOS 13+ (guide tested on macOS 15 / Apple Silicon)
- [Homebrew](https://brew.sh/) for package management
- `git` and `cabal` (installed via Homebrew in the steps below)

> **Tip:** If you already have a working `cardano-cli`, skip to [Network configuration](#4-network-configuration).

## 2. Install system dependencies

```bash
brew update
brew install ghc cabal-install pkg-config libtool autoconf automake jq
```

## 3. Install `cardano-cli`

### Option A — Homebrew binary (fastest)

```bash
brew tap input-output-hk/cardano
brew install cardano-node
```

The formula installs both `cardano-node` and `cardano-cli` to `/opt/homebrew/bin`.

### Option B — Build from source (latest or custom version)

> Building directly on Apple Silicon produces native `aarch64-apple-darwin` binaries, so you can avoid Rosetta entirely.

1. Install build tooling (if you skipped [step 2](#2-install-system-dependencies), run it now) plus the crypto libs used by `cardano-node`:

```bash
brew install libsodium secp256k1
```

2. Install the recommended GHC/Cabal toolchain with [GHCup](https://www.haskell.org/ghcup/):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://get-ghcup.haskell.org | sh
source ~/.ghcup/env   # Ensures this shell sees ~/.ghcup/bin
ghcup install ghc 8.10.7
ghcup set ghc 8.10.7
ghcup install cabal 3.10.2.1
ghcup set cabal 3.10.2.1
```

> **Important:** cardano-node requires GHC 8.10.7 (not 9.6.3). GHC 9.6.3 comes with `base-4.21.0.0`, which is incompatible with `vector-0.13.1.0`'s requirement of `base < 4.21`.

> **Note:** If `ghcup` still is not found in new shells, add `export PATH="$HOME/.ghcup/bin:$PATH"` to your `~/.zshrc` (or equivalent) and reload it.

3. Clone and build:

```bash
git clone https://github.com/IntersectMBO/cardano-node.git
cd cardano-node
git fetch --tags
git checkout 8.11.0   # Or the version you need
cabal update
cabal build cardano-cli cardano-node
```

4. Copy the resulting binaries to a directory on your `PATH`:

```bash
mkdir -p ~/.local/bin
cabal list-bin cardano-cli | xargs -I {} cp "{}" ~/.local/bin/
cabal list-bin cardano-node | xargs -I {} cp "{}" ~/.local/bin/
```

Add `~/.local/bin` to your `PATH` if necessary (e.g., `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc`).

#### Apple Silicon lessons learned (M1/M2)

The latest run-through of these steps on an M1 Pro (macOS 15) surfaced a few fixes worth codifying:

1. **Reset stale Cabal indexes when dependency solving fails.**
   ```bash
   rm -f ~/.cabal/packages/*/01-index.cache
   cabal update
   ```
   This resolved `index-state` warnings and ensured we were compiling against the freshest package metadata before `cabal build`.

2. **Expose `libsodium`/`secp256k1` via pkg-config.** Even with `brew install libsodium secp256k1`, Cabal reported `pkg-config package libsodium-any, not found`. Export the brew prefixes (or the path to your manually compiled `cardano-libsodium`) so pkg-config and the linker can see them:
   ```bash
   export LIBSODIUM_PREFIX="$(brew --prefix libsodium)"        # or /usr/local/cardano-libsodium
   export PKG_CONFIG_PATH="$LIBSODIUM_PREFIX/lib/pkgconfig:$PKG_CONFIG_PATH"
   export LIBRARY_PATH="$LIBSODIUM_PREFIX/lib:$LIBRARY_PATH"
   export C_INCLUDE_PATH="$LIBSODIUM_PREFIX/include:$C_INCLUDE_PATH"
   export DYLD_LIBRARY_PATH="$LIBSODIUM_PREFIX/lib:$DYLD_LIBRARY_PATH"
   ```

3. **Point the linker at Homebrew’s OpenSSL.** The Apple linker emitted `ld: library 'ssl' not found` until we explicitly referenced Brew’s keg:
   ```bash
   brew install openssl@3
   export OPENSSL_PREFIX="$(brew --prefix openssl@3)"
   export LDFLAGS="-L${OPENSSL_PREFIX}/lib $LDFLAGS"
   export CPPFLAGS="-I${OPENSSL_PREFIX}/include $CPPFLAGS"
   export PKG_CONFIG_PATH="${OPENSSL_PREFIX}/lib/pkgconfig:$PKG_CONFIG_PATH"
   export LIBRARY_PATH="${OPENSSL_PREFIX}/lib:$LIBRARY_PATH"
   export DYLD_LIBRARY_PATH="${OPENSSL_PREFIX}/lib:$DYLD_LIBRARY_PATH"
   ```
   Keeping these exports in your shell profile prevents future builds from regressing.

4. **Use Cabal’s conflict minimizer.** Running `cabal build cardano-cli cardano-node --minimize-conflict-set` made the dependency solver converge faster on Apple Silicon.

## 4. Network configuration

Create a working directory for Cardano network artifacts:

```bash
mkdir -p ~/cardano/config/{testnet,mainnet}
mkdir -p ~/cardano/db/{testnet,mainnet}
```

Download the latest configuration files from the [official environment docs](https://book.world.dev.cardano.org/environments.html):

```bash
# Testnet (preprod magic 1097911063)
cd ~/cardano/config/testnet
curl -L -O https://book.world.dev.cardano.org/environments/preprod/config.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/topology.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/byron-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/shelley-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/alonzo-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/conway-genesis.json

# Mainnet
cd ~/cardano/config/mainnet
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/config.json
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/topology.json
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/byron-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/shelley-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/alonzo-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/mainnet/conway-genesis.json
```

> **Note:** Always verify downloaded files are valid JSON (not HTML error pages). Use `python3 -m json.tool <file>` to validate.

## 5. Start a node (optional but recommended)

You can either connect to a locally running node or point `cardano-cli` to a remote relay. For local development:

```bash
# Example: start a preprod relay
cardano-node run \
  --topology ~/cardano/config/testnet/topology.json \
  --database-path ~/cardano/db/testnet \
  --socket-path ~/cardano/db/testnet/node.socket \
  --host-addr 0.0.0.0 \
  --port 3001 \
  --config ~/cardano/config/testnet/config.json
```

Leave the node running in a dedicated terminal or background service manager (launchd, systemd, tmux).

### Expected startup behavior

When `cardano-node` starts, you'll see various log messages. The following are **normal and expected**:

#### Peer connection attempts

The node attempts to connect to peers listed in `topology.json`. You may see messages like:

```
[cardano.node.PeerSelectionActions:Error] PeerStatusChangeFailure (ColdToWarm Nothing 3.127.163.30:3001) 
  (HandshakeClientFailure (HandshakeProtocolError (HandshakeError (VersionMismatch [] [14]))))
```

**This is normal.** The node tries multiple peers, and some may:
- Be running incompatible protocol versions
- Be temporarily unreachable
- Reject connections for various reasons

The node will continue trying other peers until it finds compatible ones.

#### Connection manager status

During startup, connection counters may show zeros:

```
TrConnectionManagerCounters (ConnectionManagerCounters {
  fullDuplexConns = 0, 
  duplexConns = 0, 
  unidirectionalConns = 0, 
  inboundConns = 0, 
  outboundConns = 0
})
```

**This is expected** during initial connection attempts. Once peers are established, these values will increase.

#### Peer selection progress

Watch for these indicators of successful connection:

- `viewEstablishedPeers > 0` — connections established
- `viewActivePeers > 0` — active peer connections
- `ChainSyncClient` or `ChainSyncHeaderServer` messages — chain synchronization in progress

#### Expected timeline

Understanding typical timeframes helps set expectations:

**Peer Connection Establishment:**
- **Time:** 30 seconds to 5 minutes
- **What happens:** Node attempts to connect to bootstrap peers from `topology.json`
- **Success indicators:** `viewEstablishedPeers > 0` and `viewActivePeers > 0`

**Initial Chain Synchronization:**

The time depends on whether you're starting fresh or resuming:

| Scenario | Preprod Testnet | Mainnet |
|----------|----------------|---------|
| **Fresh node** (empty database) | 2-6 hours | 24-48 hours |
| **Resuming sync** (existing database) | 5-30 minutes | 30 minutes - 2 hours |

**Full Synchronization (First Time):**
- Preprod Testnet: 4-8 hours
- Mainnet: 48+ hours (sometimes longer)

**Factors Affecting Speed:**
- **Internet connection** — faster connection = quicker sync
- **Hardware** — SSD storage, more RAM, and CPU cores help significantly
- **Network load** — testnets are typically faster than mainnet
- **Database state** — resuming from existing database is much faster than starting fresh

**Monitoring Progress:**

Check sync status with:

```bash
cardano-cli query tip \
  --testnet-magic 1097911063 \
  --socket-path ~/cardano/db/testnet/node.socket
```

Look for:
- `slot` number increasing
- `block` number increasing  
- `syncProgress` approaching 100.0

**What You Should See:**
- **Within 1-5 minutes:** Peer connections established (`viewEstablishedPeers > 0`)
- **Within 5-15 minutes:** Chain sync messages appearing (`ChainSyncClient`, `ChainSyncHeaderServer`)
- **Within 30-60 minutes:** Significant progress on testnet (if resuming from existing database)
- **Within 2-6 hours:** Fully synced on testnet (fresh start)

#### When to be concerned

Only worry if you see:
- **Repeated failures to all peers** — check your network connection and topology.json
- **Database errors** — verify database path permissions
- **Configuration parsing errors** — ensure config files are valid JSON (not HTML error pages)
- **No peer connections after 10-15 minutes** — may indicate network or configuration issues

Be patient during the initial startup phase, especially on first-time sync.

## 6. Environment variables

Add the following exports to `~/.zshrc` (or your shell profile) to make CLI commands less verbose:

```bash
# Cardano CLI defaults
export CARDANO_NODE_SOCKET_PATH=$HOME/cardano/db/testnet/node.socket
export CARDANO_TESTNET_MAGIC=1097911063

# Convenience wrappers
cardano_testnet() {
  cardano-cli "$@" \
    --testnet-magic "${CARDANO_TESTNET_MAGIC}" \
    --socket-path "${CARDANO_NODE_SOCKET_PATH}"
}
```

For mainnet usage, either override `CARDANO_NODE_SOCKET_PATH` and use `--mainnet`, or add a helper function:

```bash
cardano_mainnet() {
  cardano-cli "$@" \
    --mainnet \
    --socket-path "$HOME/cardano/db/mainnet/node.socket"
}
```

Reload your shell profile or open a new terminal after making these changes.

## 7. Verification

Check the installed version:

```bash
cardano-cli --version
```

Verify network connectivity:

```bash
cardano-cli query tip \
  --testnet-magic 1097911063 \
  --socket-path ~/cardano/db/testnet/node.socket
```

You should see the current slot, block, and block hash. If the command hangs, confirm that the node is fully synchronized and the socket path is correct.

## 8. Troubleshooting

- **`cardano-cli: command not found`** — ensure `/opt/homebrew/bin` or `~/.local/bin` is on `PATH`.
- **`cardano-cli: Network.Socket.connect: <socket: xx>`** — the node is not running or the socket path is incorrect. Re-check `CARDANO_NODE_SOCKET_PATH`.
- **`Failed reading: not a valid json value`** or **`AesonException "expected Object, but encountered String"`** — ensure the downloaded config files are valid JSON (not HTML error pages). Re-download using the URLs above and verify with `python3 -m json.tool <file>`.
- **Version mismatch errors during startup** — see [Expected startup behavior](#expected-startup-behavior) above. These are normal and the node will continue trying other peers.
- **Slow synchronization** — use community relays (preprod, preview) or connect to a remote service instead of running your own node for quick testing.

With `cardano-cli` installed and configured, you can complete the steps in `docs/testnet-deployment.md` and `docs/mainnet-migration.md` without additional setup.

