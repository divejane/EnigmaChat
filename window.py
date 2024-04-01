from PySide6.QtWidgets import (QVBoxLayout, QMainWindow, QScrollArea,
                               QSizePolicy, QSpacerItem, QTextEdit, QWidget)

# Subclass of QMainWindow used to create a window tailored exactly how we want it
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Basic settings for title of window, color, and geometry
        # TODO: Figure out a way to set geometry based on size of monitor (like tkinter screenwidth() function)
        self.setWindowTitle("Discreet Dial")
        self.setStyleSheet("background-color: #222222;")
        self.setGeometry(300, 200, 1000, 800)

        # Create the central widget and set it as the central widget of our class
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a layout for the central widget
        self.central_layout = QVBoxLayout(self.central_widget)

        # Add a stretchable spacer to push the text to the bottom (temp solution hopefully)
        # TODO: Change this to be another QTextEdit that will be unmodifiable to the user and will print necessary outputs
        self.spacer = QSpacerItem(20, 400, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.central_layout.addItem(self.spacer)

        # Create a QTextEdit for text entry
        self.text_entry = QTextEdit()
        self.text_entry.setFontFamily("Courier")

        # Create a QScrollArea to make the text area scrollable
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.text_entry)
        self.central_layout.addWidget(self.scroll_area)

