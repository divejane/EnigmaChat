import sys
from PySide6.QtWidgets import QApplication
from window import Window


if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Declare our window subclass and show it
    window = Window()
    window.show()

    # Run the main Qt loop
    sys.exit(app.exec())
