from PySide6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QSize, Qt



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oil Market Simulation Experiments")
        self.resize(QSize(800, 600))
        self.setMinimumSize(QSize(800, 600)) #in pixels
        # Set central widget
        self.set_central_widget()
        
        
        
    def set_central_widget(self):
        central = QWidget()
        outer_layout = QVBoxLayout()
        central.setLayout(outer_layout)
        
        
        title_label = QLabel("Market Experiments", alignment=Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setPointSize(20)
        title_label.setFont(font)
        
        menu_container = QWidget()
        menu_container.setFixedWidth(400)
        menu_layout = QVBoxLayout()
        menu_container.setLayout(menu_layout)
        
        new_experiment_button = QPushButton("New Experiment")
        view_experiments_button = QPushButton("View Experiments")
        new_baseline_button = QPushButton("New Baseline")
        exit_button = QPushButton("Exit")
        menu_layout.addWidget(title_label)
        menu_layout.addWidget(new_experiment_button)
        menu_layout.addWidget(view_experiments_button)
        menu_layout.addWidget(new_baseline_button)
        menu_layout.addWidget(exit_button)
        
        outer_layout.addStretch()
        outer_layout.addWidget(menu_container, alignment=Qt.AlignmentFlag.AlignCenter)
        outer_layout.addStretch()
        
        self.setCentralWidget(central)
        
        