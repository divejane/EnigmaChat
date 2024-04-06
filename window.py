from PySide6.QtWidgets import (QMainWindow, QScrollArea, QTextEdit,
                               QVBoxLayout, QWidget)


# Subclass of QMainWindow used to create a window tailored exactly how we want it
class Window(QMainWindow):
    def __init__(self, height: int, width: int):
        super().__init__()

        # Creates constants for us based on the parameters passed to our subclass
        self.HEIGHT, self.WIDTH = height, width

        # Basic settings for title of window, color, and geometry
        # The geometry settings should make it appear roughly in the center of any screen, regardless of resolution
        self.setWindowTitle("Discreet Dial")
        self.setStyleSheet("background-color: #222222;")
        self.setGeometry(
            int(self.WIDTH / 4),
            int(self.HEIGHT / 4),
            int(self.WIDTH / 2),
            int(self.HEIGHT / 2),
        )

        # Create the central widget and set it as the central widget of our class
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a layout for the central widget
        # This ensures that our text boxes will stack themselves on top of each other
        self.central_layout = QVBoxLayout(self.central_widget)

        # This is our output for text chat
        # We give it a stretch factor of 2 to ensure that it is bigger than our entry box
        self.output = QTextEdit()
        self.output.setFontFamily("JetBrains Mono")
        self.output.setFontPointSize(20)
        self.output.setMinimumHeight(int(self.HEIGHT / 2.1))
        self.output.setReadOnly(True)

        # Create a QScrollArea to make the output text scrollable and adds our output box to the scroll area
        self.output_scroll_area = QScrollArea()
        self.output_scroll_area.setWidgetResizable(True)
        self.output_scroll_area.setWidget(self.output)
        self.central_layout.addWidget(self.output_scroll_area, 7)

        # This is the input for text chat
        self.input = QTextEdit()
        self.input.setFontFamily("JetBrains Mono")
        self.input.setFontPointSize(20)
        self.input.setStyleSheet("border: 1px solid white")

        # Create a QScrollArea to make the input text area scrollable and adds our text entry to it
        self.input_scroll_area = QScrollArea()
        self.input_scroll_area.setWidgetResizable(True)
        self.input_scroll_area.setWidget(self.input)
        self.central_layout.addWidget(self.input_scroll_area, 2)
