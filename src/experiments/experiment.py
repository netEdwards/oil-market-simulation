from __future__ import annotations

import json
from logging import config
from operator import is_
from os import name
import re
import shutil
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
        default_factory=lambda: datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
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

    @property
    def analysis_path(self) -> Path:
        return self.folder_path / "analysis.json"
    
    @property
    def execution_result_path(self) -> Path:
        return self.folder_path / "execution_result.json"

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

    def save_analysis(self, payload: dict) -> Path:
        """Saves a generated analysis from the ExperimentAnalyzer class specifically. But can take any dict payload

        Args:
            payload (dict): Payload of analysis data

        Returns:
            Path: path to experiments analysis json
        """
        with self.analysis_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)
        return self.analysis_path
    
    def load_analysis(self) -> dict:
        """Loads the analysis from the classes analysis_path property. If not present will raise. Use `has_analysis()` to check if an experiment has an analysis.

        Raises:
            FileNotFoundError: Missing file at path in class. Or it does not exist. 

        Returns:
            dict: full analysis payload.
        """
        if not self.analysis_path:
            raise FileNotFoundError(f"No analysis found at: {self.analysis_path}")
        
        with self.analysis_path.open("r", encoding="utf-8") as f:
            return json.load(f)
        
    def has_analysis(self) -> bool:
        return self.analysis_path.exists()

    def save_execution(self, payload: dict) -> Path:        
        with open(self.execution_result_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

        return self.execution_result_path
    
    def load_execution(self) -> dict:
        if not self.execution_result_path.exists():
            raise FileNotFoundError(f"No execution result found at: {self.execution_result_path}")

        with self.execution_result_path.open("r", encoding="utf-8") as f:
            return json.load(f)
        
    def has_execution(self) -> bool:
        return self.execution_result_path.exists()

    def clear_experiment(self) -> None:
        self.clear_runs()
        self.clear_analysis()
        self.clear_execution()

    def clear_runs(self) -> None:
        runs_path = self.folder_path / "runs"
        
        if not runs_path.exists():
            return
        
        for item in runs_path.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def clear_execution(self) -> None:
        if not self.has_execution(): return
        
        path = self.execution_result_path
        if path.exists() and path.is_file():
            path.unlink()
        
    def clear_analysis(self) -> None:
        if not self.has_analysis: return
        
        path = self.analysis_path
        if path.exists() and path.is_file():
            path.unlink()

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