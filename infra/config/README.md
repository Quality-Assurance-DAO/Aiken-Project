# Infrastructure Configuration

This directory contains configuration files for Cardano infrastructure services.

## Files

- `config.json` - Cardano node configuration (network-specific)
- `topology.json` - Cardano node topology configuration

## Setup

Copy network-specific configuration files from the `share/` directory:

```bash
# For testnet
cp ../share/preview/config.json config/
cp ../share/preview/topology.json config/

# For mainnet
cp ../share/mainnet/config.json config/
cp ../share/mainnet/topology.json config/
```

## Docker Compose

Start all services:

```bash
docker-compose up -d
```

Check service status:

```bash
docker-compose ps
```

View logs:

```bash
docker-compose logs -f
```

Stop services:

```bash
docker-compose down
```

