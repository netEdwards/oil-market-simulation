from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from oilmarket.data.simulation import SimulationConfig


@dataclass
class ConfigValidationResult:
    is_valid: bool
    config_data: dict[str, Any] | None = None
    missing_fields: list[str] = field(default_factory=list)
    error_message: str | None = None


class ExperimentConfigLoader:
    """
    Loads and validates simulation config YAML files for experiment import.
    """

    REQUIRED_TOP_LEVEL_KEYS = {
        "seed",
        "ticks",
        "base_price",
        "shock",
        "buyers",
        "sellers",
    }

    def __init__(self, config_yaml: str | Path) -> None:
        self.config_yaml_path = Path(config_yaml)

    def load_yaml(self, path: str | Path | None = None) -> dict[str, Any]:
        yaml_path = Path(path) if path else self.config_yaml_path

        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        if yaml_path.suffix.lower() not in {".yaml", ".yml"}:
            raise ValueError(
                f"Invalid config file type: {yaml_path.suffix}. Expected .yaml or .yml"
            )

        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError("YAML file is empty.")

        if not isinstance(data, dict):
            raise ValueError("YAML root must be a dictionary/object.")

        return data

    def validate_dict(self, config_data: dict[str, Any]) -> ConfigValidationResult:
        """
        Validate the config dictionary.

        Validation strategy:
        - check top-level required keys first for clearer UX
        - then attempt SimulationConfig.from_dict() for full schema validation
        """
        missing_fields: list[str] = []

        for key in self.REQUIRED_TOP_LEVEL_KEYS:
            if key not in config_data:
                missing_fields.append(key)

        if missing_fields:
            return ConfigValidationResult(
                is_valid=False,
                config_data=None,
                missing_fields=sorted(missing_fields),
                error_message="Missing required top-level fields.",
            )

        try:
            # This is the real schema validation against your app's config model.
            SimulationConfig.from_dict(config_data)
        except KeyError as e:
            missing_key = str(e).strip("'")
            return ConfigValidationResult(
                is_valid=False,
                config_data=None,
                missing_fields=[missing_key],
                error_message=f"Missing required nested field: {missing_key}",
            )
        except TypeError as e:
            return ConfigValidationResult(
                is_valid=False,
                config_data=None,
                missing_fields=[],
                error_message=f"Invalid config structure: {e}",
            )
        except Exception as e:
            return ConfigValidationResult(
                is_valid=False,
                config_data=None,
                missing_fields=[],
                error_message=f"Config validation failed: {e}",
            )

        return ConfigValidationResult(
            is_valid=True,
            config_data=config_data,
            missing_fields=[],
            error_message=None,
        )

    def load_and_validate(
        self,
        path: str | Path | None = None,
    ) -> ConfigValidationResult:
        try:
            config_data = self.load_yaml(path)
            return self.validate_dict(config_data)
        except Exception as e:
            return ConfigValidationResult(
                is_valid=False,
                config_data=None,
                missing_fields=[],
                error_message=str(e),
            )