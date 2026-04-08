from pathlib import Path
from typing import Callable, Literal

from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QPushButton,
    QStackedWidget, 
    QTabWidget,
    QSizePolicy
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QPicture, QPixmap



from experiments.experiment import Experiment
from experiments.experiment_executer import ExecutionResult


class ExperimentResultsScreen(QWidget):
    def __init__(
        self, 
        on_back: Callable[[], None] | None,
        on_analysis: Callable[[], None] | None,
    ) -> None:
        super().__init__()
        
        # -------- DATA --------
        self.execution_result = None
        self.experiment = None
        self.analysis = None
        

        # -------- CALLBACKS --------
        self.on_back = on_back
        self.on_run_analysis = on_analysis

        # -------- ROOT UI --------
        self.outer_layout = QVBoxLayout(self)

        self.stack = QStackedWidget()
        self.outer_layout.addWidget(self.stack)

        # Build both views once
        self.no_analysis_page = self._build_no_analysis_page()
        self.analysis_page = self._build_analysis_page()

        self.stack.addWidget(self.no_analysis_page)
        self.stack.addWidget(self.analysis_page)

        self._connect_init_signals()
        
        
        
    def _build_no_analysis_page(self):
        root = QWidget()
        root_layout = QVBoxLayout(root)
        
        title_label = QLabel("Experiment Analysis")
        title_label_font = title_label.font()
        title_label_font.setBold(True)
        title_label_font.setPointSize(16)
        title_label.setFont(title_label_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_text = QLabel("There is no experiment analysis for this experiment")
        self.run_a_button = QPushButton("Run Analysis")
        self.nr_back_button = QPushButton("Back")
        
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.addWidget(title_label)
        root_layout.addWidget(main_text)
        root_layout.addWidget(self.run_a_button)
        root_layout.addWidget(self.nr_back_button)
        root_layout.addStretch()
        
        return root
        
        
    def _build_analysis_page(self):
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # top controls
        header_row = QHBoxLayout()
        self.a_back_button = QPushButton("Back")
        self.a_title = QLabel("Experiment Analysis")
        header_row.addWidget(self.a_back_button)
        header_row.addWidget(self.a_title)
        header_row.addStretch()

        self.a_back_button.clicked.connect(self._handle_back)

        # scroll area
        self.analysis_scroll = QScrollArea()
        self.analysis_scroll.setWidgetResizable(True)

        self.analysis_content = QWidget()
        self.analysis_content_layout = QVBoxLayout(self.analysis_content)
        self.analysis_content_layout.setSpacing(16)

        self.analysis_scroll.setWidget(self.analysis_content)

        page_layout.addLayout(header_row)
        page_layout.addWidget(self.analysis_scroll)
        
        # self._connect_signals()
        self._build_header()
        self._build_price_analysis()
        self._build_fulfillment_analysis()
        self._build_supply_analysis()
        self._build_all_graphs()
        # self._buid_shockless_frame()
        
        return page
        
    def _build_header(self) -> None:
        
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)
        
        self.title_label = QLabel("Experiment Results")
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(18)
        self.title_label.setFont(title_font)
        
        
        root_layout.addWidget(self.title_label)
        
        self.cards = QWidget()
        self.cards_layout = QVBoxLayout(self.cards)
        self.details_card = QFrame()
        self.details_card.setFrameShape(QFrame.Shape.StyledPanel)
        details_layout = QVBoxLayout(self.details_card)
        details_layout.setContentsMargins(16, 16, 16, 16)
        details_layout.setSpacing(16)
        
        self.name_label = QLabel("Name: ")
        name_label_font = self.name_label.font()
        name_label_font.setBold(True)
        self.name_label.setFont(name_label_font)
        
        self.descritption_label = QLabel("Description: ")
        self.descritption_label.setWordWrap(True)
        
        
        
        self.cards_layout.addWidget(self.name_label)
        self.cards_layout.addWidget(self.descritption_label)
        
        
        
        self.config_sum = QFrame()
        self.config_sum.setFrameShape(QFrame.Shape.StyledPanel)
        self.config_sum_layout = QVBoxLayout(self.config_sum)
        self.config_sum_layout.setContentsMargins(12, 12, 12, 12)
        self.config_sum_layout.setSpacing(12)
        self.config_name_label = QLabel("Config Name: ")
        self.ticks_label = QLabel("Ticks: ")
        self.num_buyers_label = QLabel("Number of Buyers: ")
        self.num_sellers_label = QLabel("Number of Sellers: ")
        
        self.config_sum_layout.addWidget(self.config_name_label)
        self.config_sum_layout.addWidget(self.ticks_label)
        self.config_sum_layout.addWidget(self.num_buyers_label)
        self.config_sum_layout.addWidget(self.num_sellers_label)
        
        self.cards_layout.addWidget(self.config_sum)
        
        #self.cards.setLayout(self.cards_layout)
        root_layout.addWidget(self.cards)
        root_layout.addStretch()
        
        root.setLayout(root_layout)
        self.analysis_content_layout.addWidget(root)
    
    
    def _build_price_analysis(self):
        self.price_analysis_section = QWidget()
        self.pas_layout = QVBoxLayout(self.price_analysis_section)
        self.pas_layout.setContentsMargins(12, 12, 12, 12)
        self.l_pas_title = QLabel("Price Analysis")
        l_pas_t_font = self.l_pas_title.font()
        l_pas_t_font.setBold(True)
        l_pas_t_font.setPointSize(16)
        self.l_pas_title.setFont(l_pas_t_font)
        
        
        self.price_a_tabs = QTabWidget()
        
        self.pa_shockless_section = self._build_pa_tab("shockless")
        self.pa_shocked_section = self._build_pa_tab("shocked")
        self.pa_comparison_section = self._build_pa_tab("comparison")
        
        self.price_a_tabs.addTab(self.pa_shockless_section, "Shockless")
        self.price_a_tabs.addTab(self.pa_shocked_section, "Shocked")
        self.price_a_tabs.addTab(self.pa_comparison_section, "Comparison")
        
        self.pas_layout.addWidget(self.l_pas_title)
        self.pas_layout.addWidget(self.price_a_tabs)
        
        self.analysis_content_layout.addWidget(self.price_analysis_section)
        
    def _build_pa_tab(self, section: Literal["shockless", "shocked", "comparison"]):
        if not section:
            return
        else: print(section)
        
        if not self.analysis: 
            print("No analysis")
            return
            
        self.pa_tab = QWidget()
        self.pas_widget_layout = QVBoxLayout(self.pa_tab)
        self.pas_widget_layout.setContentsMargins(12, 12, 12, 12)
    
        if section == "shockless" or section == "shocked":
            mean_price = self.analysis["price"][section]["mean_price"]
            price_vol = self.analysis["price"][section]["price_volatility"]
            self.l_sl_mean_price = QLabel(f"Mean Price: {mean_price}")
            self.l_sl_price_vol = QLabel(f"Price Volatility: {price_vol}")
            self.pas_widget_layout.addWidget(self.l_sl_mean_price)
            self.pas_widget_layout.addWidget(self.l_sl_price_vol)
        elif section == "comparison":
            delta_mean = self.analysis["price"]["comparison"]["delta_mean_price"]
            delta_pv = self.analysis["price"]["comparison"]["delta_volatility"]
            self.l_sl_delta_mp = QLabel(f"Delta Mean Price: {delta_mean}")
            self.l_sl_delta_pv = QLabel(f"Delta Price Volatility: {delta_pv}")
            self.pas_widget_layout.addWidget(self.l_sl_delta_mp)
            self.pas_widget_layout.addWidget(self.l_sl_delta_pv)        
        
        return self.pa_tab
        
    
    def _build_fulfillment_analysis(self):
        self.fulfillment_analysis_section = QWidget()
        self.fas_layout = QVBoxLayout(self.fulfillment_analysis_section)
        self.fas_layout.setContentsMargins(12, 12, 12, 12)
        self.l_fas_title = QLabel("Fulfillment Analysis")
        l_fas_t_font = self.l_fas_title.font()
        l_fas_t_font.setBold(True)
        l_fas_t_font.setPointSize(16)
        self.l_fas_title.setFont(l_fas_t_font)
        
        
        self.fulfillment_a_tabs = QTabWidget()
        
        self.fa_shockless_section = self._build_fa_tab("shockless")
        self.fa_shocked_section = self._build_fa_tab("shocked")
        self.fa_comparison_section = self._build_fa_tab("comparison")
        
        self.fulfillment_a_tabs.addTab(self.fa_shockless_section, "Shockless")
        self.fulfillment_a_tabs.addTab(self.fa_shocked_section, "Shocked")
        self.fulfillment_a_tabs.addTab(self.fa_comparison_section, "Comparison")
        
        self.fas_layout.addWidget(self.l_fas_title)
        self.fas_layout.addWidget(self.fulfillment_a_tabs)
        
        self.analysis_content_layout.addWidget(self.fulfillment_analysis_section)
        
    def _build_fa_tab(self, section: Literal["shockless", "shocked", "comparison"]):
        if not section:
            return
        else: print(section)
        
        if not self.analysis: 
            print("No analysis")
            return
            
        self.fa_tab = QWidget()
        self.fas_widget_layout = QVBoxLayout(self.fa_tab)
        self.fas_widget_layout.setContentsMargins(12, 12, 12, 12)
    
        if section == "shockless" or section == "shocked":
            ff_rate = self.analysis["fulfillment"][section]["fulfillment_rate"]
            peak_unmet = self.analysis["fulfillment"][section]["peak_unmet"]
            self.l_sl_ff_rate = QLabel(f"Fulfillment Rate: {ff_rate}")
            self.l_sl_peak_unmet = QLabel(f"Peak Unmet Demand: {peak_unmet}")
            self.fas_widget_layout.addWidget(self.l_sl_ff_rate)
            self.fas_widget_layout.addWidget(self.l_sl_peak_unmet)
        elif section == "comparison":
            delta_ff_rate = self.analysis["fulfillment"]["comparison"]["delta_fulfillment_rate"]
            delta_peak_unmet = self.analysis["fulfillment"]["comparison"]["delta_peak_unmet"]
            self.l_sl_delta_ff_rate = QLabel(f"Delta Fulfillment Rate: {delta_ff_rate}")
            self.l_sl_delta_peak_unmet = QLabel(f"Delta Peak Unmet Demand: {delta_peak_unmet}")
            self.fas_widget_layout.addWidget(self.l_sl_delta_ff_rate)
            self.fas_widget_layout.addWidget(self.l_sl_delta_peak_unmet)        
        
        return self.fa_tab

        
    def _build_supply_analysis(self):
        self.supply_analysis_section = QWidget()
        self.sas_layout = QVBoxLayout(self.supply_analysis_section)
        self.sas_layout.setContentsMargins(12, 12, 12, 12)
        self.l_sas_title = QLabel("Supply Analysis")
        l_sas_t_font = self.l_sas_title.font()
        l_sas_t_font.setBold(True)
        l_sas_t_font.setPointSize(16)
        self.l_sas_title.setFont(l_sas_t_font)
        
        
        self.supply_a_tabs = QTabWidget()
        
        self.sa_shockless_section = self._build_sa_tab("shockless")
        self.sa_shocked_section = self._build_sa_tab("shocked")
        self.sa_comparison_section = self._build_sa_tab("comparison")
        
        self.supply_a_tabs.addTab(self.sa_shockless_section, "Shockless")
        self.supply_a_tabs.addTab(self.sa_shocked_section, "Shocked")
        self.supply_a_tabs.addTab(self.sa_comparison_section, "Comparison")
        
        self.sas_layout.addWidget(self.l_sas_title)
        self.sas_layout.addWidget(self.supply_a_tabs)
        
        self.analysis_content_layout.addWidget(self.supply_analysis_section)
        
    def _build_sa_tab(self, section: Literal["shockless", "shocked", "comparison"]):
        if not section:
            return
        else: print(section)
        
        if not self.analysis: 
            print("No analysis")
            return
            
        self.sa_tab = QWidget()
        self.sas_widget_layout = QVBoxLayout(self.sa_tab)
        self.sas_widget_layout.setContentsMargins(12, 12, 12, 12)
    
        if section == "shockless" or section == "shocked":
            avg_supply = self.analysis["supply"][section]["avg_supply"]
            min_supply = self.analysis["supply"][section]["min_supply"]
            self.l_sl_avg_supply = QLabel(f"Average Supply: {avg_supply}")
            self.l_sl_min_supply = QLabel(f"Minimum Supply: {min_supply}")
            self.sas_widget_layout.addWidget(self.l_sl_avg_supply)
            self.sas_widget_layout.addWidget(self.l_sl_min_supply)
        elif section == "comparison":
            delta_avg_supply = self.analysis["supply"]["comparison"]["delta_avg_supply"]
            delta_min_supply = self.analysis["supply"]["comparison"]["delta_min_supply"]
            percent_avg_supply_change = self.analysis["supply"]["comparison"]["percent_avg_supply_change"]
            self.l_sl_delta_avg_s = QLabel(f"Delta Average Supply: {delta_avg_supply}")
            self.l_sl_delta_min_s = QLabel(f"Delta Minimum Supply: {delta_min_supply}")
            self.l_sl_delta_perc_avg_s = QLabel(f"Percent Delta Avg Supply: {percent_avg_supply_change}")
            self.sas_widget_layout.addWidget(self.l_sl_delta_avg_s)
            self.sas_widget_layout.addWidget(self.l_sl_delta_min_s) 
            self.sas_widget_layout.addWidget(self.l_sl_delta_perc_avg_s)        
        
        return self.sa_tab
        

        
        from pathlib import Path


    def _build_all_graphs(self) -> None:
        """Builds graphs onto scrollable layout using execution result and the build_graph_card() function."""

        if not self.execution_result:
            self._load_execution_result()
            if self.execution_result is None: return
        
        shocked_price_plot_path = self.execution_result["shocked_results"].get("price_plot")
        shocked_snd_plot_path = self.execution_result["shocked_results"].get("supply_demand_plot")
        shocked_fulfillment_plot_path = self.execution_result["shocked_results"].get("fulfillment_plot")
        
        shockless_price_plot_path = self.execution_result["shockless_results"].get("price_plot")
        shockless_snd_plot_path = self.execution_result["shockless_results"].get("supply_demand_plot")
        shockless_fulfillment_plot_path = self.execution_result["shockless_results"].get("fulfillment_plot")
        
        self.graph_container = QWidget()
        self.gc_layout = QVBoxLayout(self.graph_container)
        self.gc_layout.setContentsMargins(12, 12, 12, 12)
        
        self.l_gc_title = QLabel("Experiment Graphs")
        title_font = self.l_gc_title.font()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.l_gc_title.setFont(title_font)
        
        self.gc_shocked_tabs = QTabWidget()
        
        self.s_graph_pl_tab     = self._build_graph_card(shocked_price_plot_path, title="Shocked Prices / Time", caption="Shows the average prices over time.")
        self.s_graph_snd_tab    = self._build_graph_card(shocked_snd_plot_path, title="Supply and Demand Graph", caption="Shows the supply vs demand over time.")
        self.s_graph_ff_tab     = self._build_graph_card(shocked_fulfillment_plot_path, title="Fullfilment / Time", caption="Shows the fulfillment behavior over time.")
        
        self.gc_shocked_tabs.addTab(self.s_graph_pl_tab, "Price Plot")
        self.gc_shocked_tabs.addTab(self.s_graph_snd_tab, "S & D")
        self.gc_shocked_tabs.addTab(self.s_graph_ff_tab, "Fulfillment")
        
        self.gc_shockless_tabs = QTabWidget()
        
        self.sl_graph_pl_tab    = self._build_graph_card(shockless_price_plot_path, title="Shocked Prices / Time", caption="Shows the average prices over time.")
        self.sl_graph_snd_tab   = self._build_graph_card(shockless_snd_plot_path, title="Supply and Demand Graph", caption="Shows the supply vs demand over time.")
        self.sl_graph_ff_tab    = self._build_graph_card(shockless_fulfillment_plot_path, title="Fullfilment / Time", caption="Shows the fulfillment behavior over time.")

        self.gc_shockless_tabs.addTab(self.sl_graph_pl_tab, "Price Plot")
        self.gc_shockless_tabs.addTab(self.sl_graph_snd_tab, "S & D")
        self.gc_shockless_tabs.addTab(self.sl_graph_ff_tab, "Fulfillment")
        
        self.gc_shocked_title = QLabel("Shocked Graphs")
        self.gc_shockless_title = QLabel("Shockless Graphs")
        
        self.gc_layout.addWidget(self.gc_shocked_title)
        self.gc_layout.addWidget(self.gc_shocked_tabs)
        self.gc_layout.addWidget(self.gc_shockless_title)
        self.gc_layout.addWidget(self.gc_shockless_tabs)
        
        self.analysis_content_layout.addWidget(self.graph_container)

    def _build_graph_card(
        self,
        image_path: str | Path,
        title: str = "Graph",
        caption: str = "",
        max_width: int = 900,
    ) -> QWidget:
        """
        Build a reusable card widget for displaying a graph image with a title and caption.
        """

        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setObjectName("graphCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setWordWrap(True)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        caption_label = QLabel(caption)
        caption_label.setWordWrap(True)
        caption_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        path = Path(image_path) if image_path else None

        if not path or not path.exists():
            image_label.setText("Graph image not found.")
        else:
            pixmap = QPixmap(str(path))

            if pixmap.isNull():
                image_label.setText("Failed to load graph image.")
            else:
                if pixmap.width() > max_width:
                    pixmap = pixmap.scaledToWidth(
                        max_width,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                image_label.setPixmap(pixmap)

        layout.addWidget(title_label)
        layout.addWidget(image_label)

        if caption:
            layout.addWidget(caption_label)

        return card
        
        
    def _connect_init_signals(self)  -> None:
        self.nr_back_button.clicked.connect(lambda: self._handle_back())
        self.run_a_button.clicked.connect(lambda: self._handle_run_analysis())
        
        
    def _populate_header(self) -> None:
        if not self.analysis: return
        if not self.experiment: return
        # FROM EXPERIMENT
        name = self.experiment.name
        desc = self.experiment.description
        #FROM ANALYSIS
        config_sum: dict = self.analysis.get("config_summary", {})
        buyers: dict = config_sum.get("buyers", {})
        sellers: dict = config_sum.get("sellers", {})
        seller_count = 0
        major_count = sellers.get("major").get("count")
        medium_count = sellers.get("medium").get("count")
        small_count = sellers.get("small").get("count")
        seller_count += major_count + medium_count + small_count
        
        if config_sum:
            ticks = config_sum.get("ticks", "")
            num_buyers = buyers.get("count", 0)
            num_sellers = seller_count
            
        self.ticks_label.setText(f"Ticks: {ticks}")
        self.num_buyers_label.setText(f"Number of Buyers: {num_buyers}")
        self.num_sellers_label.setText(f"Number of Sellers: {num_sellers}")
    
    
    
    def set_experiment_and_result(self, experiment: Experiment, execution_result: ExecutionResult) -> None:
        self.experiment = experiment if isinstance(experiment, Experiment) else None #sometimes passed as dict, need to handle properly.
        self.execution_result = execution_result #never passed as anything other than class instance.
        
        if self.experiment is None:
            return
        
    def set_experiment_analysis(self, analysis: dict) -> None:
        if not self.analysis:
            self.analysis = analysis
            print(f"Analysis set: {analysis.keys()}")
    
    def _create_experiment_vars(self) -> None:
        if not self.experiment:
            return
        
        print(self.experiment)
        
    def show_no_analysis(self, experiment = None):
        self.experiment = experiment
        
        self.stack.setCurrentWidget(self.no_analysis_page)
        
    def show_analysis(self, experiment = None, analysis = None):
        self.experiment = experiment
        self.analysis = analysis
        
        self.stack.setCurrentWidget(self.analysis_page)
        self._populate_header()
        
    def _handle_back(self) -> None:
        if self.on_back:
            self.on_back()
            
    def _handle_run_analysis(self) -> None:
        if self.on_run_analysis:
            self.on_run_analysis()
           
    def _load_execution_result(self) -> None:
        if not self.experiment: return
        
        if self.execution_result is not None: return
        
        has_er = self.experiment.has_execution()
        if has_er:
            self.execution_result = self.experiment.load_execution()
        else:
            print("There is no execution result")
            return
            
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)

            widget = item.widget()
            child_layout = item.layout()

            if widget:
                widget.deleteLater()
            elif child_layout:
                self.clear_layout(child_layout)
                
    def refresh_analysis(self):
        self.clear_layout(self.analysis_content_layout)

        self._build_header()
        self._build_price_analysis()
        self._build_fulfillment_analysis()
        self._build_supply_analysis()
        self._build_all_graphs()
        self._populate_header()