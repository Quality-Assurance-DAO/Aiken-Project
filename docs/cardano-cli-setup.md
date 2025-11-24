# Cardano CLI Setup

**Last updated:** 2025-11-24

This guide explains how to install `cardano-cli`, configure it for the testnet and mainnet networks used by this project, and verify that your environment works end to end.

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
ghcup install ghc 9.6.3
ghcup set ghc 9.6.3
ghcup install cabal 3.10.2.1
ghcup set cabal 3.10.2.1
```

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

## 4. Network configuration

Create a working directory for Cardano network artifacts:

```bash
mkdir -p ~/cardano/config/{testnet,mainnet}
mkdir -p ~/cardano/db/{testnet,mainnet}
```

Download the latest configuration files. Replace the URLs with the current ones from the [official environment docs](https://book.world.dev.cardano.org/environments.html):

```bash
# Testnet (preprod magic 1097911063)
cd ~/cardano/config/testnet
curl -O https://book.world.dev.cardano.org/testnet-configs/preprod/config.json
curl -O https://book.world.dev.cardano.org/testnet-configs/preprod/topology.json
curl -O https://book.world.dev.cardano.org/testnet-configs/preprod/byron-genesis.json
curl -O https://book.world.dev.cardano.org/testnet-configs/preprod/shelley-genesis.json
curl -O https://book.world.dev.cardano.org/testnet-configs/preprod/alonzo-genesis.json

# Mainnet
cd ~/cardano/config/mainnet
curl -O https://book.world.dev.cardano.org/mainnet-configs/mainnet-config.json
curl -O https://book.world.dev.cardano.org/mainnet-configs/mainnet-topology.json
curl -O https://book.world.dev.cardano.org/mainnet-configs/mainnet-byron-genesis.json
curl -O https://book.world.dev.cardano.org/mainnet-configs/mainnet-shelley-genesis.json
curl -O https://book.world.dev.cardano.org/mainnet-configs/mainnet-alonzo-genesis.json
```

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
- **`Failed reading: not a valid json value`** — ensure the downloaded config files are not HTML error pages; re-download and verify checksums if available.
- **Slow synchronization** — use community relays (preprod, preview) or connect to a remote service instead of running your own node for quick testing.

With `cardano-cli` installed and configured, you can complete the steps in `docs/testnet-deployment.md` and `docs/mainnet-migration.md` without additional setup.

