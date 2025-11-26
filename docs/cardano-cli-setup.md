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

This project supports three Cardano networks, each with separate configurations and database directories:

| Network | Network Magic | Purpose | Database Directory | Socket Directory |
|---------|--------------|---------|-------------------|------------------|
| **Preprod** | `1` | Stable testnet for production-like testing | `db-preprod/` | `preprod-socket/` |
| **Preview** | `2` | Bleeding-edge testnet for latest features | `db-preview/` | `preview-socket/` |
| **Mainnet** | N/A (use `--mainnet`) | Production network | `db-mainnet/` | `mainnet-socket/` |

> **Important:** Each network uses a separate database directory to prevent NetworkMagic conflicts. Never share database directories between networks.

### Using project-provided configurations

This project includes pre-configured network files in the `share/` directory:

- `share/preprod/` - Preprod testnet configuration (NetworkMagic 1)
- `share/preview/` - Preview testnet configuration (NetworkMagic 2)
- `share/mainnet/` - Mainnet configuration

These configurations are ready to use with the project's startup scripts. No manual download required.

### Manual configuration (optional)

If you prefer to manage configurations separately, create directories and download from the [official environment docs](https://book.world.dev.cardano.org/environments.html):

```bash
mkdir -p ~/cardano/config/{preprod,preview,mainnet}
mkdir -p ~/cardano/db/{preprod,preview,mainnet}
```

Download configuration files:

```bash
# Preprod testnet (NetworkMagic 1)
cd ~/cardano/config/preprod
curl -L -O https://book.world.dev.cardano.org/environments/preprod/config.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/topology.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/byron-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/shelley-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/alonzo-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preprod/conway-genesis.json

# Preview testnet (NetworkMagic 2)
cd ~/cardano/config/preview
curl -L -O https://book.world.dev.cardano.org/environments/preview/config.json
curl -L -O https://book.world.dev.cardano.org/environments/preview/topology.json
curl -L -O https://book.world.dev.cardano.org/environments/preview/byron-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preview/shelley-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preview/alonzo-genesis.json
curl -L -O https://book.world.dev.cardano.org/environments/preview/conway-genesis.json

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

### Using the project's startup script

This project includes a startup script for convenience:

```bash
# Start Preprod node (default)
./scripts/start_node.sh preprod

# Or start Preview node
./scripts/start_node.sh preview

# Or start Mainnet node
./scripts/start_node.sh mainnet
```

### Disk space requirements

Before starting a node, ensure you have sufficient disk space. The Cardano node database grows continuously as it syncs and stores blockchain data.

**Official Requirements:**

| Network | Minimum | Recommended | Current Size (2024) |
|---------|---------|-------------|---------------------|
| **Mainnet** | 150 GB | 250 GB+ | ~184 GB |
| **Testnets** (Preprod/Preview) | 20 GB | 30-50 GB | 10-20 GB (fully synced) |

**Database Structure:**

The node stores data in three main components:

1. **Immutable blocks** (~95% of space)
   - Historical blockchain data
   - Grows continuously as new blocks are added (~20 seconds per block)
   - Located in `immutable/` subdirectory

2. **Ledger state** (~2-5% of space)
   - Current UTXO set and smart contract state
   - Grows with network activity
   - Located in `ledger/` subdirectory

3. **Volatile blocks** (~1-2% of space)
   - Recent blocks being processed
   - Relatively stable size
   - Located in `volatile/` subdirectory

**Example Database Sizes:**

From a partially synced preprod testnet:
- Total: ~1.2 GB
  - Immutable blocks: ~1.1 GB
  - Ledger state: ~33 MB
  - Volatile: ~51 MB

**Important Notes:**

- **Database persistence**: The node stores all blockchain data persistently. When you restart the node, it resumes from the existing database and only syncs new blocks that arrived while offline. It does **not** resync from scratch.
- **Continuous growth**: The blockchain grows over time as new blocks are added. Allocate more space than the current minimum to accommodate future growth.
- **SSD recommended**: Using an SSD significantly improves sync speed and node performance.
- **Monitor disk usage**: Regularly check available disk space, especially for mainnet nodes.

**Checking Database Size:**

```bash
# Check size of a specific database directory
du -sh db-preprod

# Check breakdown by component
du -sh db-preprod/immutable db-preprod/ledger db-preprod/volatile
```

### Manual node startup

Alternatively, you can start the node manually. **Important:** Use the correct database directory for each network:

```bash
# Preprod (NetworkMagic 1)
cd share/preprod
cardano-node run \
  --config config.json \
  --topology topology.json \
  --database-path ../../db-preprod \
  --socket-path ../../preprod-socket/node.socket \
  --host-addr 127.0.0.1 \
  --port 3001

# Preview (NetworkMagic 2)
cd share/preview
cardano-node run \
  --config config.json \
  --topology topology.json \
  --database-path ../../db-preview \
  --socket-path ../../preview-socket/node.socket \
  --host-addr 127.0.0.1 \
  --port 3001

# Mainnet
cd share/mainnet
cardano-node run \
  --config config.json \
  --topology topology.json \
  --database-path ../../db-mainnet \
  --socket-path ../../mainnet-socket/node.socket \
  --host-addr 127.0.0.1 \
  --port 3001
```

> **Warning:** Using the wrong database directory will cause a `NetworkMagicMismatch` error. Each network must use its own database directory.

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

**Database Persistence:**
- The node stores all blockchain data persistently in the database directory
- When you stop and restart the node, it **does not resync from scratch**
- It reads the existing blockchain state and only syncs new blocks that arrived while offline
- This means restarting is fast — typically just a few minutes to catch up on new blocks

**Monitoring Progress:**

Check sync status with the appropriate network magic:

```bash
# Preprod (NetworkMagic 1)
cardano-cli query tip \
  --testnet-magic 1 \
  --socket-path preprod-socket/node.socket

# Preview (NetworkMagic 2)
cardano-cli query tip \
  --testnet-magic 2 \
  --socket-path preview-socket/node.socket

# Mainnet
cardano-cli query tip \
  --mainnet \
  --socket-path mainnet-socket/node.socket
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

#### After sync completes

Once your node reaches `syncProgress: "100.00"`, it enters **steady-state operation**:

**What the node continues doing:**
1. **Stays synchronized** — Continuously receives and validates new blocks as they're produced (typically every ~20 seconds on Cardano)
2. **Maintains peer connections** — Keeps connections to other nodes for block propagation
3. **Serves queries** — Responds to `cardano-cli` queries (UTXO, tip, protocol parameters, etc.)
4. **Validates transactions** — Validates transactions in the mempool and new blocks
5. **Updates chain state** — Maintains the current blockchain state in its database

**What you can do:**
- **Query the blockchain** — Use `cardano-cli` to query UTXOs, addresses, protocol parameters
- **Build transactions** — Create and submit transactions using the synced node
- **Test smart contracts** — Deploy and interact with smart contracts on the testnet
- **Monitor the network** — Watch new blocks being added in real-time

**Log activity after sync:**
- You'll see fewer "Chain extended" messages (only when new blocks arrive, typically every 20 seconds)
- More "Block fits onto some fork" messages as new blocks arrive
- Steady peer connection maintenance messages
- Mempool activity if transactions are being submitted

**The node keeps running:**
- The node process continues running indefinitely
- It automatically stays synchronized with the network
- No manual intervention needed — just leave it running
- You can safely minimize the terminal or run it in the background

**Verifying sync status:**
Check that `syncProgress` is at 100%. Run this from the **project root directory** (`/Users/stephen/Documents/GitHub/Aiken-Project`):

```bash
# From project root directory
cardano-cli query tip \
  --testnet-magic 1 \
  --socket-path preprod-socket/node.socket | jq .syncProgress
```

You should see `"100.00"` when fully synced.

> **Note:** The socket path is relative to where you run the command. If you're in a different directory, use an absolute path like `$HOME/Aiken-Project/preprod-socket/node.socket` or set the `CARDANO_NODE_SOCKET_PATH` environment variable.

#### When to be concerned

Only worry if you see:
- **Repeated failures to all peers** — check your network connection and topology.json
- **Database errors** — verify database path permissions
- **Configuration parsing errors** — ensure config files are valid JSON (not HTML error pages)
- **No peer connections after 10-15 minutes** — may indicate network or configuration issues

Be patient during the initial startup phase, especially on first-time sync.

## 6. Environment variables

### Using the project's environment setup script

This project includes an environment setup script:

```bash
# Source the environment setup for Preprod (default)
source scripts/setup_env.sh preprod

# Or for Preview
source scripts/setup_env.sh preview

# Or for Mainnet
source scripts/setup_env.sh mainnet
```

### Manual environment setup

Alternatively, add the following exports to `~/.zshrc` (or your shell profile) to make CLI commands less verbose:

```bash
# Cardano CLI defaults (for Preprod)
export CARDANO_NODE_SOCKET_PATH=$HOME/Aiken-Project/preprod-socket/node.socket
export CARDANO_TESTNET_MAGIC=1

# Convenience wrappers
cardano_preprod() {
  cardano-cli "$@" \
    --testnet-magic 1 \
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
# Preprod (NetworkMagic 1)
cardano-cli query tip \
  --testnet-magic 1 \
  --socket-path preprod-socket/node.socket

# Preview (NetworkMagic 2)
cardano-cli query tip \
  --testnet-magic 2 \
  --socket-path preview-socket/node.socket

# Mainnet
cardano-cli query tip \
  --mainnet \
  --socket-path mainnet-socket/node.socket
```

You should see the current slot, block, and block hash. If the command hangs, confirm that the node is fully synchronized and the socket path is correct.

## 8. Troubleshooting

- **`cardano-cli: command not found`** — ensure `/opt/homebrew/bin` or `~/.local/bin` is on `PATH`.
- **`cardano-cli: Network.Socket.connect: <socket: xx>`** — the node is not running or the socket path is incorrect. Re-check `CARDANO_NODE_SOCKET_PATH`.
- **`NetworkMagicMismatch` error** — you're trying to use a database directory from a different network. Each network (preprod, preview, mainnet) requires its own database directory:
  - Preprod: `db-preprod/` (NetworkMagic 1)
  - Preview: `db-preview/` (NetworkMagic 2)
  - Mainnet: `db-mainnet/` (no magic)
  - Solution: Delete the conflicting database directory or use the correct one for your network.
- **`Failed reading: not a valid json value`** or **`AesonException "expected Object, but encountered String"`** — ensure the downloaded config files are valid JSON (not HTML error pages). Re-download using the URLs above and verify with `python3 -m json.tool <file>`.
- **Version mismatch errors during startup** — see [Expected startup behavior](#expected-startup-behavior) above. These are normal and the node will continue trying other peers.
- **Slow synchronization** — use community relays (preprod, preview) or connect to a remote service instead of running your own node for quick testing.

With `cardano-cli` installed and configured, you can complete the steps in `docs/testnet-deployment.md` and `docs/mainnet-migration.md` without additional setup.

