class StreamRedirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.append(text)

    def flush(self):
        pass