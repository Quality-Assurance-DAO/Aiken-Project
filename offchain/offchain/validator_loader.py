"""Validator loading for compiled Aiken validators."""

import json
from pathlib import Path
from typing import Optional, Dict, Any


class ValidatorLoader:
    """Load compiled Aiken validators from plutus.json format."""

    def __init__(self, validator_path: Optional[str] = None):
        """Initialize validator loader."""
        if validator_path:
            self.validator_path = Path(validator_path)
        else:
            # Default to project root plutus.json
            self.validator_path = Path(__file__).parent.parent.parent / "plutus.json"

    def load_validator(self, validator_name: Optional[str] = None) -> Dict[str, Any]:
        """Load validator from plutus.json file."""
        if not self.validator_path.exists():
            raise FileNotFoundError(
                f"Validator file not found: {self.validator_path}"
            )

        with open(self.validator_path, "r") as f:
            plutus_data = json.load(f)

        # If validator_name is specified, look for it in the validators dict
        if validator_name:
            if "validators" in plutus_data:
                if validator_name not in plutus_data["validators"]:
                    raise ValueError(
                        f"Validator '{validator_name}' not found in plutus.json"
                    )
                return plutus_data["validators"][validator_name]
            else:
                raise ValueError("No 'validators' key found in plutus.json")

        # Otherwise, return the first validator or the whole structure
        if "validators" in plutus_data and plutus_data["validators"]:
            # Return first validator
            first_key = next(iter(plutus_data["validators"]))
            return plutus_data["validators"][first_key]

        return plutus_data

    def get_compiled_code(self, validator_name: Optional[str] = None) -> str:
        """Extract compiled code (hex string) from validator."""
        validator = self.load_validator(validator_name)
        if "compiledCode" in validator:
            return validator["compiledCode"]
        raise ValueError("No 'compiledCode' found in validator")

    def get_validator_hash(self, validator_name: Optional[str] = None) -> str:
        """Extract validator hash from validator."""
        validator = self.load_validator(validator_name)
        if "hash" in validator:
            return validator["hash"]
        raise ValueError("No 'hash' found in validator")

    def get_datum_schema(self, validator_name: Optional[str] = None) -> Optional[Dict]:
        """Extract datum schema from validator."""
        validator = self.load_validator(validator_name)
        return validator.get("datumSchema")

    def get_redeemer_schema(self, validator_name: Optional[str] = None) -> Optional[Dict]:
        """Extract redeemer schema from validator."""
        validator = self.load_validator(validator_name)
        return validator.get("redeemerSchema")

