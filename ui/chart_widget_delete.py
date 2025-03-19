# ui/widgets/chart_widget.py
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = MatplotlibCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas)
        
    def update_chart(self, data, labels, title=""):
        self.canvas.axes.clear()
        self.canvas.axes.pie(data, labels=labels, autopct='%1.1f%%', startangle=90)
        self.canvas.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        if title:
            self.canvas.axes.set_title(title)
        self.canvas.draw()

class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = MatplotlibCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas)
        
    def update_chart(self, data, categories, title="", xlabel="", ylabel=""):
        self.canvas.axes.clear()
        self.canvas.axes.bar(categories, data)
        if title:
            self.canvas.axes.set_title(title)
        if xlabel:
            self.canvas.axes.set_xlabel(xlabel)
        if ylabel:
            self.canvas.axes.set_ylabel(ylabel)
        self.canvas.axes.tick_params(axis='x', rotation=45)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

class LineChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.canvas = MatplotlibCanvas(self, width=5, height=4)
        self.layout.addWidget(self.canvas)
        
    def update_chart(self, data, categories, title="", xlabel="", ylabel=""):
        self.canvas.axes.clear()
        self.canvas.axes.plot(categories, data, marker='o')
        if title:
            self.canvas.axes.set_title(title)
        if xlabel:
            self.canvas.axes.set_xlabel(xlabel)
        if ylabel:
            self.canvas.axes.set_ylabel(ylabel)
        self.canvas.axes.tick_params(axis='x', rotation=45)
        self.canvas.fig.tight_layout()
        self.canvas.draw()