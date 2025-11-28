"""Configuration management for Python off-chain backend."""

import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field
import yaml


class NetworkConfiguration(BaseModel):
    """Network and service configuration."""

    network: Literal["testnet", "mainnet", "preview", "preprod"] = Field(
        ..., description="Network name"
    )
    ogmios_url: str = Field(
        default="ws://localhost:1337", description="Ogmios WebSocket URL"
    )
    kupo_url: str = Field(
        default="http://localhost:1442", description="Kupo HTTP URL"
    )
    cardano_node_socket: Optional[str] = Field(
        None, description="Path to cardano-node socket (if needed)"
    )
    protocol_magic: Optional[int] = Field(
        None, description="Protocol magic number (network-specific)"
    )

    def validate_connectivity(self) -> dict:
        """Validate connectivity to all services."""
        results = {
            "ogmios": False,
            "kupo": False,
            "cardano_node": False,
        }
        # Implementation: test connections
        return results


class DataStorageConfiguration(BaseModel):
    """Configuration for local data storage."""

    data_directory: Path = Field(
        default=Path("offchain/data"),
        description="Base directory for data storage",
    )
    milestones_directory: Path = Field(
        default=Path("offchain/data/milestones"),
        description="Directory for milestone completion data",
    )
    cache_directory: Path = Field(
        default=Path("offchain/data/cache"),
        description="Directory for cached contract states",
    )

    def ensure_directories(self):
        """Create directories if they don't exist."""
        self.milestones_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)


def load_config(config_path: Optional[str] = None) -> tuple[NetworkConfiguration, DataStorageConfiguration]:
    """Load configuration from YAML file or environment variables."""
    network_config = NetworkConfiguration(
        network=os.getenv("CARDANO_NETWORK", "testnet"),
        ogmios_url=os.getenv("OGMIOS_URL", "ws://localhost:1337"),
        kupo_url=os.getenv("KUPO_URL", "http://localhost:1442"),
        cardano_node_socket=os.getenv("CARDANO_NODE_SOCKET"),
        protocol_magic=int(os.getenv("PROTOCOL_MAGIC")) if os.getenv("PROTOCOL_MAGIC") else None,
    )

    data_dir = Path(os.getenv("DATA_DIRECTORY", "offchain/data"))
    storage_config = DataStorageConfiguration(
        data_directory=data_dir,
        milestones_directory=data_dir / "milestones",
        cache_directory=data_dir / "cache",
    )

    # Load from YAML file if provided
    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
            if "network" in config_data:
                network_config = NetworkConfiguration(**config_data.get("network", {}))
            if "storage" in config_data:
                storage_config = DataStorageConfiguration(**config_data.get("storage", {}))

    return network_config, storage_config


def check_cardano_node_connectivity(socket_path: Optional[str]) -> bool:
    """Check if cardano-node socket is accessible."""
    if not socket_path:
        return False
    socket_file = Path(socket_path)
    return socket_file.exists() and socket_file.is_socket()


