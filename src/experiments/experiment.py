from __future__ import annotations

import json
from logging import config
from os import name
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from matplotlib.inset import InsetIndicator
import yaml


EXPERIMENTS_ROOT = Path(__file__).resolve().parent.parent.parent / "experiments"


def _slugify(value: str) -> str:
    """
    Convert a human-readable experiment name into a filesystem-safe slug.
    """
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "experiment"


@dataclass
class Experiment:
    """
    Represents one saved experiment definition.

    Each experiment is persisted under:

        experiments/
          exp-<short_id>-<slug>/
            experiment.json
            config.yaml
    """

    name: str
    description: str
    config_data: dict[str, Any] | None

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

    METADATA_FILENAME: ClassVar[str] = "experiment.json"
    CONFIG_FILENAME: ClassVar[str] = "config.yaml"

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.description = self.description.strip()

        if not self.name:
            raise ValueError("Experiment name is required.")

        if not isinstance(self.config_data, dict) or not self.config_data:
            raise ValueError("config_data must be a non-empty dictionary.")

    @property
    def slug(self) -> str:
        return _slugify(self.name)

    @property
    def short_id(self) -> str:
        return self.id[:8]

    @property
    def folder_name(self) -> str:
        return f"exp-{self.short_id}-{self.slug}"

    @property
    def folder_path(self) -> Path:
        return EXPERIMENTS_ROOT / self.folder_name

    @property
    def metadata_path(self) -> Path:
        return self.folder_path / self.METADATA_FILENAME

    @property
    def config_path(self) -> Path:
        return self.folder_path / self.CONFIG_FILENAME
    
    @property
    def output_path(self) -> Path:
        return self.folder_path / "runs"

    def to_dict(self) -> dict[str, Any]:
        """
        Metadata only. Intentionally excludes config_data.
        """
        return {
            "id":           self.id,
            "name":         self.name,
            "slug":         self.slug,
            "folder_name":  self.folder_name,
            "description":  self.description,
            "created_at":   self.created_at,
            "config_file":  self.CONFIG_FILENAME,
            "output_path":  str(self.output_path),
            "folder_path":  str(self.folder_path)
        }

    def save(self) -> Path:
        """
        Save experiment metadata and config into the experiment's folder.

        Returns:
            Path to the experiment folder.
        """
        self.folder_path.mkdir(parents=True, exist_ok=False)

        with self.metadata_path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

        with self.config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.config_data,
                f,
                sort_keys=False,
                allow_unicode=True,
            )

        return self.folder_path



    @classmethod
    def load(cls, folder_path: Path | str) -> "Experiment":
        """
        Load an experiment and its config from a saved experiment folder.
        """
        folder = Path(folder_path)
        metadata_path = folder / cls.METADATA_FILENAME

        if not metadata_path.exists():
            raise FileNotFoundError(f"No experiment metadata found at: {metadata_path}")

        with metadata_path.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        config_file = metadata.get("config_file", cls.CONFIG_FILENAME)
        config_path = folder / config_file

        if not config_path.exists():
            raise FileNotFoundError(f"No config file found at: {config_path}")

        with config_path.open("r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f) or {}

        experiment = cls(
            name=metadata["name"],
            description=metadata.get("description", ""),
            config_data=config_data,
            id=metadata["id"],
            created_at=metadata["created_at"],
        )
        
        print(f'Experiment loaded successfully: {experiment.name}')

        return experiment

    @classmethod
    def list_saved_experiments(cls) -> list[dict[str, Any]]:
        """
        Scan the experiments root and return lightweight metadata
        for all saved experiments.
        """
        if not EXPERIMENTS_ROOT.exists():
            return []

        results: list[dict[str, Any]] = []

        for folder in sorted(EXPERIMENTS_ROOT.iterdir()):
            if not folder.is_dir():
                continue

            metadata_path = folder / cls.METADATA_FILENAME
            if not metadata_path.exists():
                continue

            try:
                with metadata_path.open("r", encoding="utf-8") as f:
                    metadata = json.load(f)

                results.append(
                    {
                        "id": metadata.get("id"),
                        "name": metadata.get("name"),
                        "description": metadata.get("description", ""),
                        "created_at": metadata.get("created_at"),
                        "folder_name": folder.name,
                        "folder_path": str(folder),
                    }
                )
            except Exception:
                # Skip malformed experiment folders for now.
                continue

        return results