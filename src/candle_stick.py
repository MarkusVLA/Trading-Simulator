from PyQt5.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.generatePicture()
    
    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        # Initial pen set up is removed since pen color will be set dynamically
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            if open > close:
                p.setPen(pg.mkPen('r'))  # Set pen color to red for downward movement
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setPen(pg.mkPen('g'))  # Set pen color to green for upward movement
                p.setBrush(pg.mkBrush('g'))
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            p.drawRect(QtCore.QRectF(t-w, open, w*2, close-open))
        p.end()
    
    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)
    
    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())