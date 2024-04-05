import sys
sys.path.insert(1, "src")
from main import MainWindow, QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())