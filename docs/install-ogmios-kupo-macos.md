# Installing Ogmios and Kupo on macOS

**Navigation**: [Home](../README.md) > [Documentation](./README.md) > Install Ogmios/Kupo on macOS

**Last updated:** 2025-11-27

This guide explains how to install Ogmios and Kupo natively on macOS to avoid Docker socket issues.

## Problem

On macOS, Docker Desktop cannot properly access Unix domain sockets mounted from the host filesystem. This causes Ogmios and Kupo containers to fail with errors like:

```
Network.Socket.connect: unsupported operation (Not supported)
ServerNodeSocketNotFound
```

## Solution: Install Native Binaries

You have three options for installing Ogmios and Kupo natively on macOS:

### Option 1: Build from Source (Recommended - Most Reliable)

This is the most reliable method and ensures you get the latest versions:

1. **Install dependencies:**

```bash
brew install ghc cabal-install pkg-config libtool autoconf automake
```

2. **Create a build directory (recommended):**

Choose a location for building these tools. You can use:
- `~/src` - for keeping source code projects
- `~/projects` - alternative projects directory
- `/tmp` - temporary location (will be cleaned on reboot)

```bash
# Create build directory (if it doesn't exist)
mkdir -p ~/src
cd ~/src
```

3. **Build Ogmios:**

```bash
git clone https://github.com/CardanoSolutions/ogmios.git
cd ogmios
git submodule update --init --recursive
cd server
cabal build
cabal install --installdir=$HOME/.local/bin
cd ../..
```

**Important notes:**
- The cabal project is located in the `server` subdirectory, so you must `cd` into `ogmios/server` before running `cabal build`.
- Ogmios requires git submodules to be initialized. Run `git submodule update --init --recursive` from the ogmios root directory.
- Ogmios requires GHC 9.x (not 8.10.7). If you have GHC 8.10.7 installed (for cardano-node), you can install GHC 9.6.3 using:
  ```bash
  ghcup install ghc 9.6.3
  ghcup set ghc 9.6.3
  ```
  After building ogmios, you can switch back to GHC 8.10.7 if needed:
  ```bash
  ghcup set ghc 8.10.7
  ```

4. **Build Kupo:**

```bash
git clone https://github.com/CardanoSolutions/kupo.git
cd kupo
cabal build
cabal install --installdir=$HOME/.local/bin
cd ..
```

**Note:** After installation, you can optionally remove the cloned directories if you want to save space:
```bash
cd ~/src
rm -rf ogmios kupo
```

5. **Add to PATH:**

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: Install via Homebrew (if available)

Check if Homebrew formulas are available:

```bash
brew tap cardanosolutions/cardano-services
brew install ogmios kupo
```

**Note:** This may not be available. If it fails, use Option 1 (Build from Source).

### Option 3: Install via Nix (Experimental)

If you have Nix installed and want to try Nix-based installation:

```bash
# Install Nix (if not already installed)
sh <(curl -L https://nixos.org/nix/install)

# Try installing via nixpkgs (may not have ogmios/kupo packages)
nix-env -iA ogmios kupo -f https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz

# Alternative: Use nix flakes if you have flakes enabled
# nix profile install github:CardanoSolutions/ogmios github:CardanoSolutions/kupo
```

**Note:** The `cardano-services-nix` repository is not available (404 error). Nix packages for ogmios/kupo may not be in nixpkgs. If this doesn't work, use Option 1 (Build from Source).

## Verify Installation

After installation, verify the binaries are available:

```bash
which ogmios
which kupo

ogmios --version
kupo --version
```

## Usage

Once installed, the `start_services.sh` script will automatically detect and use native binaries instead of Docker:

```bash
./scripts/start_services.sh preprod
```

The script will:
- Detect native binaries automatically
- Start Ogmios and Kupo as native processes
- Log to `ogmios.log` and `kupo.log` in the project root

## Troubleshooting

### Binaries not found

If the script doesn't detect your binaries, ensure they're in your PATH:

```bash
echo $PATH
which ogmios
which kupo
```

### Permission errors

Ensure the socket file is readable:

```bash
ls -l preprod-socket/node.socket
```

### Port already in use

If ports 1337 or 1442 are already in use:

```bash
lsof -i :1337
lsof -i :1442
```

Stop any existing processes or change the ports in the script.

## References

- [Ogmios GitHub](https://github.com/CardanoSolutions/ogmios)
- [Kupo GitHub](https://github.com/CardanoSolutions/kupo)

