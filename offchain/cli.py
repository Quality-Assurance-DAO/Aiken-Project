#!/usr/bin/env python3
"""CLI entry point for Python off-chain backend."""

import asyncio
import json
import typer
from offchain.ogmios_client import OgmiosClient
from offchain.kupo_client import KupoClient
from offchain.config import check_cardano_node_connectivity, NetworkConfiguration

app = typer.Typer(
    name="offchain",
    help="Python off-chain backend for milestone-based token distribution on Cardano",
    add_completion=False,
)


@app.command()
def init(
    network: str = typer.Option("testnet", "--network", "-n", help="Network name (testnet/mainnet/preview/preprod)"),
    ogmios_url: str = typer.Option("ws://localhost:1337", "--ogmios-url", help="Ogmios WebSocket URL"),
    kupo_url: str = typer.Option("http://localhost:1442", "--kupo-url", help="Kupo HTTP URL"),
    cardano_node_socket: str = typer.Option(None, "--cardano-node-socket", help="Path to cardano-node socket"),
    output_format: str = typer.Option("json", "--output", "-o", help="Output format (json/text)"),
):
    """Initialize and verify connectivity to Cardano services."""
    async def check_services():
        """Check all services asynchronously."""
        ogmios_client = OgmiosClient(ogmios_url)
        kupo_client = KupoClient(kupo_url)
        
        # Check Ogmios
        ogmios_result = await ogmios_client.check_connectivity()
        
        # Check Kupo
        kupo_result = kupo_client.check_connectivity()
        
        # Check cardano-node socket
        node_connected = False
        node_network = None
        if cardano_node_socket:
            node_connected = check_cardano_node_connectivity(cardano_node_socket)
            node_network = network if node_connected else None
        
        return {
            "status": "success" if (ogmios_result.get("connected") and kupo_result.get("connected") and node_connected) else "partial",
            "services": {
                "ogmios": ogmios_result,
                "kupo": kupo_result,
                "cardano_node": {
                    "connected": node_connected,
                    "network": node_network,
                },
            },
        }
    
    try:
        result = asyncio.run(check_services())
        
        if output_format == "json":
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"Initializing environment for {network}...")
            typer.echo(f"\nService Status:")
            typer.echo(f"  Ogmios: {'✓ Connected' if result['services']['ogmios'].get('connected') else '✗ Not connected'}")
            typer.echo(f"  Kupo: {'✓ Connected' if result['services']['kupo'].get('connected') else '✗ Not connected'}")
            typer.echo(f"  Cardano Node: {'✓ Connected' if result['services']['cardano_node'].get('connected') else '✗ Not connected'}")
            
            if result["status"] != "success":
                typer.echo("\n⚠ Warning: Some services are unavailable.")
                typer.echo("Please ensure all services are running:")
                typer.echo("  - Ogmios: Check WebSocket connection")
                typer.echo("  - Kupo: Check HTTP connection")
                typer.echo("  - Cardano Node: Check socket path")
                raise typer.Exit(code=1)
        
    except Exception as e:
        error_result = {
            "status": "failed",
            "error": str(e),
            "services": {
                "ogmios": {"connected": False},
                "kupo": {"connected": False},
                "cardano_node": {"connected": False},
            },
        }
        if output_format == "json":
            typer.echo(json.dumps(error_result, indent=2))
        else:
            typer.echo(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def register_milestone(
    token_policy_id: str = typer.Option(..., "--token-policy-id", help="Token policy ID (hex)"),
    beneficiary_allocations: str = typer.Option(..., "--beneficiary-allocations", help="Path to allocations JSON file"),
    oracle_addresses: str = typer.Option(..., "--oracle-addresses", help="Comma-separated oracle addresses"),
    quorum_threshold: int = typer.Option(..., "--quorum-threshold", help="Minimum oracle signatures required"),
    network: str = typer.Option("testnet", "--network", "-n", help="Network name"),
    output_format: str = typer.Option("json", "--output", "-o", help="Output format (json/text)"),
):
    """Register a new milestone schedule."""
    import json
    from pathlib import Path
    from offchain.models import MilestoneSchedule, BeneficiaryAllocationInput
    from offchain.milestone_manager import MilestoneManager
    from offchain.validator_loader import ValidatorLoader
    from offchain.config import DataStorageConfiguration
    
    try:
        # Load beneficiary allocations from file
        allocations_path = Path(beneficiary_allocations)
        if not allocations_path.exists():
            typer.echo(f"Error: Allocations file not found: {beneficiary_allocations}", err=True)
            raise typer.Exit(code=1)
        
        with open(allocations_path, "r") as f:
            allocations_data = json.load(f)
        
        # Parse allocations
        allocations = [
            BeneficiaryAllocationInput(**alloc) for alloc in allocations_data
        ]
        
        # Parse oracle addresses
        oracle_addrs = [addr.strip() for addr in oracle_addresses.split(",")]
        
        # Create milestone schedule
        schedule = MilestoneSchedule(
            token_policy_id=token_policy_id,
            beneficiary_allocations=allocations,
            oracle_addresses=oracle_addrs,
            quorum_threshold=quorum_threshold,
        )
        
        # Validate schedule
        storage_config = DataStorageConfiguration()
        manager = MilestoneManager(storage_config.data_directory)
        errors = manager.validate_milestone_schedule(schedule)
        
        if errors:
            if output_format == "json":
                typer.echo(json.dumps({"error": "Validation failed", "errors": errors}, indent=2))
            else:
                typer.echo("Validation errors:", err=True)
                for error in errors:
                    typer.echo(f"  - {error}", err=True)
            raise typer.Exit(code=1)
        
        # Generate datum
        datum = manager.generate_datum(schedule)
        
        # Calculate contract address
        validator_loader = ValidatorLoader()
        try:
            validator_hash = validator_loader.get_validator_hash()
            contract_address = manager.calculate_contract_address(validator_hash, network)
        except Exception as e:
            contract_address = None
            if output_format == "text":
                typer.echo(f"Warning: Could not calculate contract address: {e}", err=True)
        
        # Output result
        result = {
            "datum": datum,
            "contract_address": contract_address,
            "total_token_amount": schedule.total_token_amount,
        }
        
        if output_format == "json":
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"Milestone schedule registered successfully!")
            typer.echo(f"Contract address: {contract_address or 'N/A'}")
            typer.echo(f"Total token amount: {schedule.total_token_amount}")
            typer.echo(f"Datum generated: {len(json.dumps(datum))} bytes")
        
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON in allocations file: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def commit_milestone(
    milestone_identifier: str = typer.Option(..., "--milestone-identifier", help="Milestone identifier"),
    oracle_signatures: str = typer.Option(..., "--oracle-signatures", help="Path to signatures JSON file"),
    quorum_threshold: int = typer.Option(None, "--quorum-threshold", help="Quorum threshold (if not in existing data)"),
    total_oracles: int = typer.Option(None, "--total-oracles", help="Total authorized oracles (if not in existing data)"),
    output_format: str = typer.Option("json", "--output", "-o", help="Output format (json/text)"),
):
    """Commit milestone completion data."""
    import json
    from pathlib import Path
    from offchain.models import OracleSignatureData
    from offchain.milestone_manager import MilestoneManager
    from offchain.config import DataStorageConfiguration
    
    try:
        # Load oracle signatures from file
        signatures_path = Path(oracle_signatures)
        if not signatures_path.exists():
            typer.echo(f"Error: Signatures file not found: {oracle_signatures}", err=True)
            raise typer.Exit(code=1)
        
        with open(signatures_path, "r") as f:
            signatures_data = json.load(f)
        
        # Parse signatures - support both list and single signature
        if isinstance(signatures_data, dict):
            signatures_data = [signatures_data]
        
        signatures = []
        for sig_data in signatures_data:
            try:
                signatures.append(OracleSignatureData(**sig_data))
            except Exception as e:
                typer.echo(f"Error: Invalid signature format: {e}", err=True)
                raise typer.Exit(code=1)
        
        if not signatures:
            typer.echo("Error: No valid signatures provided", err=True)
            raise typer.Exit(code=1)
        
        # Initialize milestone manager
        storage_config = DataStorageConfiguration()
        manager = MilestoneManager(storage_config.data_directory)
        
        # Check if milestone data already exists
        existing_data = manager.load_milestone_completion_data(milestone_identifier)
        
        # Use existing quorum_threshold and total_oracles if available
        if existing_data:
            if quorum_threshold is None:
                quorum_threshold = existing_data.quorum_threshold
            if total_oracles is None:
                total_oracles = existing_data.total_oracles
        
        # Validate required parameters for new milestone data
        if quorum_threshold is None or total_oracles is None:
            typer.echo(
                "Error: quorum_threshold and total_oracles are required when creating new milestone data",
                err=True
            )
            raise typer.Exit(code=1)
        
        # Commit milestone completion data
        try:
            milestone_data = manager.commit_milestone_completion_data(
                milestone_identifier=milestone_identifier,
                oracle_signatures=signatures,
                quorum_threshold=quorum_threshold,
                total_oracles=total_oracles,
            )
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
        
        # Output result
        result = {
            "milestone_identifier": milestone_data.milestone_identifier,
            "signature_count": milestone_data.signature_count,
            "quorum_threshold": milestone_data.quorum_threshold,
            "quorum_status": milestone_data.quorum_status,
            "quorum_met": milestone_data.quorum_met,
            "verification_timestamp": milestone_data.verification_timestamp,
            "total_signatures": len(milestone_data.oracle_signatures),
        }
        
        if output_format == "json":
            typer.echo(json.dumps(result, indent=2))
        else:
            typer.echo(f"Milestone completion data committed successfully!")
            typer.echo(f"Milestone: {milestone_data.milestone_identifier}")
            typer.echo(f"Signatures: {milestone_data.signature_count}/{milestone_data.quorum_threshold}")
            typer.echo(f"Quorum status: {milestone_data.quorum_status}")
            if milestone_data.quorum_met:
                typer.echo(f"✓ Quorum met - milestone verified!")
            else:
                typer.echo(f"⚠ Quorum not met - {milestone_data.quorum_threshold - milestone_data.signature_count} more signatures needed")
        
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON in signatures file: {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@app.command()
def check_status(
    contract_address: str = typer.Option(..., "--contract-address", help="Distribution contract address"),
    milestone_identifier: str = typer.Option(None, "--milestone-identifier", help="Specific milestone identifier (optional)"),
):
    """Check milestone completion status."""
    # TODO: Implement status checking
    typer.echo("Status checking not yet implemented")


@app.command()
def calculate_distribution(
    contract_address: str = typer.Option(..., "--contract-address", help="Distribution contract address"),
    beneficiary_address: str = typer.Option(..., "--beneficiary-address", help="Beneficiary address"),
    milestone_identifier: str = typer.Option(None, "--milestone-identifier", help="Specific milestone (optional)"),
):
    """Calculate token distribution amounts."""
    # TODO: Implement distribution calculation
    typer.echo("Distribution calculation not yet implemented")


@app.command()
def submit_release(
    contract_address: str = typer.Option(..., "--contract-address", help="Distribution contract address"),
    beneficiary_address: str = typer.Option(..., "--beneficiary-address", help="Beneficiary address"),
    beneficiary_index: int = typer.Option(..., "--beneficiary-index", help="Index in allocations list"),
    milestone_identifier: str = typer.Option(..., "--milestone-identifier", help="Milestone being claimed"),
    signing_key_path: str = typer.Option(..., "--signing-key-path", help="Path to signing key file"),
):
    """Submit token release transaction."""
    # TODO: Implement transaction submission
    typer.echo("Transaction submission not yet implemented")


if __name__ == "__main__":
    app()

