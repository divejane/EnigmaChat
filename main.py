import sys
from PySide6.QtWidgets import QApplication
from window import Window


if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Gets the height and width of the screen that the app is on and stores them as constants
    # This is used to determine the geometry of the window upon opening
    SCREEN_HEIGHT = app.primaryScreen().size().height()
    SCREEN_WIDTH = app.primaryScreen().size().width()

    # Declare our window subclass and show it
    window = Window(SCREEN_HEIGHT, SCREEN_WIDTH)
    window.show()

    print(f'{SCREEN_HEIGHT}, {SCREEN_WIDTH}')

    # Run the main Qt loop
    sys.exit(app.exec())
