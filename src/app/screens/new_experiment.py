from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import yaml

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QFormLayout,
    QGroupBox,
    QScrollArea,
    QMessageBox,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QFileDialog,
    QFrame
)

from experiments.experiment import Experiment
from experiments.experiment_config_loader import ExperimentConfigLoader


DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "default.yaml"


class NewExperimentScreen(QWidget):
    def __init__(
        self,
        on_cancel: Callable[[], None] | None = None,
        on_saved: Callable[[Experiment], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.on_cancel = on_cancel
        self.on_saved = on_saved

        self.default_config = self._load_default_config()
        self.imported_config_data = None
        
        
        self._build_ui()
        
        self._populate_defaults()

    def _load_default_config(self) -> dict[str, Any]:
        with DEFAULT_CONFIG_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        title = QLabel("Create New Experiment")
        title_font = title.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        form_container = QWidget()
        self.form_layout = QVBoxLayout(form_container)
        self.form_layout.setSpacing(14)

        self._build_metadata_group()
        self._build_upload_config()
        self._build_general_group()
        self._build_shock_group()
        self._build_buyers_group()
        self._build_seller_groups()
        self._build_pricing_group()

        self.form_layout.addStretch()

        scroll.setWidget(form_container)
        root.addWidget(scroll)

        button_row = QHBoxLayout()
        button_row.addStretch()

        self.save_button = QPushButton("Save Experiment")
        self.cancel_button = QPushButton("Cancel")

        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)

        root.addLayout(button_row)

        self._connect_signals()

    def _build_metadata_group(self) -> None:
        group = QGroupBox("Experiment Info")
        layout = QFormLayout(group)

        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(100)

        layout.addRow("Name", self.name_input)
        layout.addRow("Description", self.description_input)

        self.form_layout.addWidget(group)

    def _build_general_group(self) -> None:
        group = QGroupBox("General Configuration")
        layout = QFormLayout(group)

        self.seed_input = QSpinBox()
        self.seed_input.setMaximum(999999999)

        self.ticks_input = QSpinBox()
        self.ticks_input.setMaximum(100000)

        self.base_price_input = QDoubleSpinBox()
        self.base_price_input.setMaximum(1_000_000)
        self.base_price_input.setDecimals(3)

        layout.addRow("Seed", self.seed_input)
        layout.addRow("Ticks", self.ticks_input)
        layout.addRow("Base Price", self.base_price_input)

        self.form_layout.addWidget(group)

    def _build_shock_group(self) -> None:
        group = QGroupBox("Shock")
        layout = QFormLayout(group)

        self.shock_severity_input = QDoubleSpinBox()
        self.shock_severity_input.setRange(0.0, 1.0)
        self.shock_severity_input.setSingleStep(0.05)
        self.shock_severity_input.setDecimals(3)

        self.shock_duration_input = QSpinBox()
        self.shock_duration_input.setMaximum(100000)

        self.shock_start_time_input = QDoubleSpinBox()
        self.shock_start_time_input.setMaximum(100000)
        self.shock_start_time_input.setDecimals(3)

        self.shock_target_input = QComboBox()
        self.shock_target_input.addItems(["top_seller"])

        layout.addRow("Severity", self.shock_severity_input)
        layout.addRow("Duration", self.shock_duration_input)
        layout.addRow("Start Time", self.shock_start_time_input)
        layout.addRow("Target", self.shock_target_input)

        self.form_layout.addWidget(group)

    def _build_buyers_group(self) -> None:
        buyers_group = QGroupBox("Buyers")
        buyers_layout = QFormLayout(buyers_group)

        self.buyers_count_input = QSpinBox()
        self.buyers_count_input.setMaximum(1_000_000)
        buyers_layout.addRow("Count", self.buyers_count_input)
        self.form_layout.addWidget(buyers_group)

        wtp_group = QGroupBox("Buyers → WTP")
        wtp_layout = QFormLayout(wtp_group)

        self.wtp_dist_input = QComboBox()
        self.wtp_dist_input.addItems(["truncated_nomral", "truncated_normal"])

        self.wtp_mu_input = QDoubleSpinBox()
        self.wtp_mu_input.setMaximum(1_000_000)
        self.wtp_mu_input.setDecimals(3)

        self.wtp_sigma_input = QDoubleSpinBox()
        self.wtp_sigma_input.setMaximum(1_000_000)
        self.wtp_sigma_input.setDecimals(3)

        self.wtp_min_input = QDoubleSpinBox()
        self.wtp_min_input.setMaximum(1_000_000)
        self.wtp_min_input.setDecimals(3)

        self.wtp_max_input = QDoubleSpinBox()
        self.wtp_max_input.setMaximum(1_000_000)
        self.wtp_max_input.setDecimals(3)

        wtp_layout.addRow("Distribution", self.wtp_dist_input)
        wtp_layout.addRow("Mu", self.wtp_mu_input)
        wtp_layout.addRow("Sigma", self.wtp_sigma_input)
        wtp_layout.addRow("Min", self.wtp_min_input)
        wtp_layout.addRow("Max", self.wtp_max_input)

        self.form_layout.addWidget(wtp_group)

        demand_group = QGroupBox("Buyers → Demand")
        demand_layout = QFormLayout(demand_group)

        self.lambda_demand_input = QDoubleSpinBox()
        self.lambda_demand_input.setMaximum(1_000_000)
        self.lambda_demand_input.setDecimals(3)

        demand_layout.addRow("Lambda Demand", self.lambda_demand_input)
        self.form_layout.addWidget(demand_group)

    def _build_seller_groups(self) -> None:
        self.major_inputs = self._build_seller_tier_group("Major Sellers")
        self.medium_inputs = self._build_seller_tier_group("Medium Sellers")
        self.small_inputs = self._build_seller_tier_group("Small Sellers")

    def _build_seller_tier_group(self, title: str) -> dict[str, QWidget]:
        group = QGroupBox(title)
        layout = QFormLayout(group)

        count = QSpinBox()
        count.setMaximum(1_000_000)

        prod_rate = QDoubleSpinBox()
        prod_rate.setMaximum(1_000_000)
        prod_rate.setDecimals(3)

        capacity = QDoubleSpinBox()
        capacity.setMaximum(1_000_000)
        capacity.setDecimals(3)

        init_inventory = QDoubleSpinBox()
        init_inventory.setMaximum(1_000_000)
        init_inventory.setDecimals(3)

        init_price = QDoubleSpinBox()
        init_price.setMaximum(1_000_000)
        init_price.setDecimals(3)

        layout.addRow("Count", count)
        layout.addRow("Production Rate", prod_rate)
        layout.addRow("Capacity", capacity)
        layout.addRow("Initial Inventory", init_inventory)
        layout.addRow("Initial Price", init_price)

        self.form_layout.addWidget(group)

        return {
            "count": count,
            "prod_rate": prod_rate,
            "capacity": capacity,
            "init_inventory": init_inventory,
            "init_price": init_price,
        }

    def _build_pricing_group(self) -> None:
        group = QGroupBox("Sellers → Pricing")
        layout = QFormLayout(group)

        self.min_price_input = QDoubleSpinBox()
        self.min_price_input.setMaximum(1_000_000)
        self.min_price_input.setDecimals(3)

        self.target_utilization_input = QDoubleSpinBox()
        self.target_utilization_input.setRange(0.0, 1.0)
        self.target_utilization_input.setSingleStep(0.05)
        self.target_utilization_input.setDecimals(3)

        self.responsiveness_input = QDoubleSpinBox()
        self.responsiveness_input.setMaximum(1000)
        self.responsiveness_input.setDecimals(4)

        layout.addRow("Minimum Price", self.min_price_input)
        layout.addRow("Target Utilization", self.target_utilization_input)
        layout.addRow("Responsiveness", self.responsiveness_input)

        self.form_layout.addWidget(group)

    def _populate_defaults(self) -> None:
        cfg = self.default_config

        self.seed_input.setValue(cfg["seed"])
        self.ticks_input.setValue(cfg["ticks"])
        self.base_price_input.setValue(cfg["base_price"])

        self.shock_severity_input.setValue(cfg["shock"]["severity"])
        self.shock_duration_input.setValue(cfg["shock"]["duration"])
        self.shock_start_time_input.setValue(cfg["shock"]["start_time"])
        self.shock_target_input.setCurrentText(cfg["shock"]["target"])

        self.buyers_count_input.setValue(cfg["buyers"]["count"])
        self.wtp_dist_input.setCurrentText(cfg["buyers"]["wtp"]["dist"])
        self.wtp_mu_input.setValue(cfg["buyers"]["wtp"]["mu"])
        self.wtp_sigma_input.setValue(cfg["buyers"]["wtp"]["sigma"])
        self.wtp_min_input.setValue(cfg["buyers"]["wtp"]["_min"])
        self.wtp_max_input.setValue(cfg["buyers"]["wtp"]["_max"])
        self.lambda_demand_input.setValue(cfg["buyers"]["demand"]["lambda_demand"])

        self._set_seller_values(self.major_inputs, cfg["sellers"]["major"])
        self._set_seller_values(self.medium_inputs, cfg["sellers"]["medium"])
        self._set_seller_values(self.small_inputs, cfg["sellers"]["small"])

        self.min_price_input.setValue(cfg["sellers"]["pricing"]["min_price"])
        self.target_utilization_input.setValue(cfg["sellers"]["pricing"]["target_utilization"])
        self.responsiveness_input.setValue(cfg["sellers"]["pricing"]["responsiveness"])

    def _set_seller_values(self, widgets: dict[str, QWidget], data: dict[str, Any]) -> None:
        widgets["count"].setValue(data["count"])
        widgets["prod_rate"].setValue(data["prod_rate"])
        widgets["capacity"].setValue(data["capacity"])
        widgets["init_inventory"].setValue(data["init_inventory"])
        widgets["init_price"].setValue(data["init_price"])

    def _connect_signals(self) -> None:
        self.cancel_button.clicked.connect(self._handle_cancel)
        self.save_button.clicked.connect(self._handle_save)

    def _build_config_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed_input.value(),
            "ticks": self.ticks_input.value(),
            "base_price": self.base_price_input.value(),
            "shock": {
                "severity": self.shock_severity_input.value(),
                "duration": self.shock_duration_input.value(),
                "start_time": self.shock_start_time_input.value(),
                "target": self.shock_target_input.currentText(),
            },
            "buyers": {
                "count": self.buyers_count_input.value(),
                "wtp": {
                    "dist": self.wtp_dist_input.currentText(),
                    "mu": self.wtp_mu_input.value(),
                    "sigma": self.wtp_sigma_input.value(),
                    "_min": self.wtp_min_input.value(),
                    "_max": self.wtp_max_input.value(),
                },
                "demand": {
                    "lambda_demand": self.lambda_demand_input.value(),
                },
            },
            "sellers": {
                "major": self._collect_seller_tier(self.major_inputs),
                "medium": self._collect_seller_tier(self.medium_inputs),
                "small": self._collect_seller_tier(self.small_inputs),
                "pricing": {
                    "min_price": self.min_price_input.value(),
                    "target_utilization": self.target_utilization_input.value(),
                    "responsiveness": self.responsiveness_input.value(),
                },
            },
        }

    def _collect_seller_tier(self, widgets: dict[str, QWidget]) -> dict[str, Any]:
        return {
            "count": widgets["count"].value(),
            "prod_rate": widgets["prod_rate"].value(),
            "capacity": widgets["capacity"].value(),
            "init_inventory": widgets["init_inventory"].value(),
            "init_price": widgets["init_price"].value(),
        }

    def _handle_cancel(self) -> None:
        if self.on_cancel:
            self.on_cancel()

    def _handle_save(self) -> None:
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Missing Name", "Experiment name is required.")
            return

        config_data = self._build_config_dict()

        try:
            experiment = Experiment(
                name=name,
                description=description,
                config_data=config_data,
            )
            experiment.save()
        except Exception as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
            return

        QMessageBox.information(self, "Saved", f'Experiment "{name}" was created successfully.')

        if self.on_saved:
            self.on_saved()
            
    def _build_upload_config(self) -> None:
        """
        Build a small config import section for the New Experiment screen.

        Returns:
            QWidget: section widget you can add into your page layout.
        """
        self.upload_config_section = QFrame()
        self.upload_config_section.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self.upload_config_section)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title_label = QLabel("Import Existing Config")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)

        helper_label = QLabel(
            "Upload a .yaml or .yml simulation config to populate the experiment form."
        )
        helper_label.setWordWrap(True)

        button_row = QHBoxLayout()
        self.upload_config_button = QPushButton("Upload Config")
        self.upload_config_button.clicked.connect(self._on_upload_config_clicked)
        button_row.addWidget(self.upload_config_button)
        button_row.addStretch()

        self.selected_config_label = QLabel("Selected file: None")
        self.selected_config_label.setWordWrap(True)

        self.config_import_status_label = QLabel("")
        self.config_import_status_label.setWordWrap(True)
        self.config_import_status_label.setTextFormat(Qt.PlainText)

        layout.addWidget(title_label)
        layout.addWidget(helper_label)
        layout.addLayout(button_row)
        layout.addWidget(self.selected_config_label)
        layout.addWidget(self.config_import_status_label)

        self.form_layout.addWidget(self.upload_config_section)


    def _on_upload_config_clicked(self) -> None:
        """
        Open file picker and attempt to import a YAML config.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Simulation Config",
            "",
            "YAML Files (*.yaml *.yml)",
        )

        if not file_path:
            return

        self._import_config_from_path(file_path)


    def _import_config_from_path(self, file_path: str) -> None:
        """
        Validate and import config from a selected path.
        """
        path = Path(file_path)

        # quick UI-side extension check
        if path.suffix.lower() not in {".yaml", ".yml"}:
            self._show_config_import_error(
                "Invalid file type. Please select a .yaml or .yml file."
            )
            return

        loader = ExperimentConfigLoader(path)
        result = loader.load_and_validate()

        self.selected_config_label.setText(f"Selected file: {path.name}")

        if not result.is_valid:
            error_text = result.error_message or "Config import failed."

            if result.missing_fields:
                missing = "\n".join(f"- {field}" for field in result.missing_fields)
                error_text = f"{error_text}\n\nMissing fields:\n{missing}"

            self.config_import_status_label.setText("Import failed.")
            self._show_config_import_error(error_text)
            return

        config_data = result.config_data or {}
        self.imported_config_data = config_data
        self.config_import_status_label.setText("Config imported successfully.")

        # Populate your form fields here
        self._populate_form_from_config(config_data)


    def _show_config_import_error(self, message: str) -> None:
        """
        Show a popup for config import errors.
        """
        QMessageBox.warning(self, "Config Import Error", message)


    def _populate_form_from_config(self, config_data: dict) -> None:
        """
        Fill your New Experiment form widgets from imported config_data.

        Replace the widget names below with your actual form widgets.
        """
        # Example top-level fields
        self.ticks_input.setValue(config_data.get("ticks", 0))
        self.seed_input.setValue(config_data.get("seed", 0))
        self.base_price_input.setValue(config_data.get("base_price", 0.0))

        # Shock
        shock = config_data.get("shock", {})
        self.shock_severity_input.setValue(shock.get("severity", 0.0))
        self.shock_duration_input.setValue(shock.get("duration", 0))
        self.shock_start_time_input.setValue(shock.get("start_time", 0))
        self.shock_target_input.setCurrentText(shock.get("target", ""))

        # Buyers
        buyers = config_data.get("buyers", {})
        self.buyers_count_input.setValue(buyers.get("count", 0))

        wtp = buyers.get("wtp", {})
        self.wtp_dist_input.setCurrentText(wtp.get("dist", "truncated_normal"))
        self.wtp_mu_input.setValue(wtp.get("mu", 0.0))
        self.wtp_sigma_input.setValue(wtp.get("sigma", 0.0))
        self.wtp_min_input.setValue(wtp.get("_min", 0.0))
        self.wtp_max_input.setValue(wtp.get("_max", 0.0))

        demand = buyers.get("demand", {})
        self.lambda_demand_input.setValue(demand.get("lambda_demand", 0.0))

        # Sellers
        sellers = config_data.get("sellers", {})
        pricing = sellers.get("pricing", {})
        self.min_price_input.setValue(pricing.get("min_price", 0.0))
        self.target_utilization_input.setValue(pricing.get("target_utilization", 0.0))
        self.responsiveness_input.setValue(pricing.get("responsiveness", 0.0))

        major = sellers.get("major", {})
        medium = sellers.get("medium", {})
        small = sellers.get("small", {})
        
        self._set_seller_values(self.major_inputs, major)
        self._set_seller_values(self.medium_inputs, medium)
        self._set_seller_values(self.small_inputs, small)  
                
                
                