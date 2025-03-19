from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor
import logging
import config

logger = logging.getLogger(config.APP_NAME)

class PieChartWidget(QWidget):
    """Widget para exibir gráficos de pizza"""
    
    def __init__(self, parent=None, title="Gráfico de Pizza"):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Criar gráfico
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        
        # Criar visualização do gráfico
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def update_chart(self, data, labels, title):
        """Atualiza os dados do gráfico de pizza
        
        Args:
            data: Lista de valores
            labels: Lista de rótulos
            title: Título do gráfico
        """
        self.title = title
        self.chart.setTitle(self.title)
        
        series = QPieSeries()
        for label, value in zip(labels, data):
            series.append(label, value)
        
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()

class BarChartWidget(QWidget):
    """Widget para exibir gráficos de barras"""
    
    def __init__(self, parent=None, title="Gráfico de Barras"):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Criar gráfico
        self.chart = QChart()
        self.chart.setTitle(self.title)
        
        # Criar visualização do gráfico
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def update_chart(self, data, categories, title, x_label, y_label):
        """Atualiza os dados do gráfico de barras
        
        Args:
            data: Lista de valores
            categories: Lista de categorias (rótulos)
            title: Título do gráfico
            x_label: Rótulo do eixo X
            y_label: Rótulo do eixo Y
        """
        self.title = title
        self.chart.setTitle(self.title)
        
        series = QBarSeries()
        bar_set = QBarSet("Valor")
        bar_set.append(data)
        series.append(bar_set)
        
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        self.chart.setAxisX(axis_x, series)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat('%i')
        self.chart.setAxisY(axis_y, series)

class LineChartWidget(QWidget):
    """Widget para exibir gráficos de linha"""
    
    def __init__(self, parent=None, title="Gráfico de Linha"):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Criar gráfico
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Criar visualização do gráfico
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def update_chart(self, data, categories, title, x_label, y_label):
        """Atualiza os dados do gráfico de linha
        
        Args:
            data: Lista de valores
            categories: Lista de categorias (rótulos)
            title: Título do gráfico
            x_label: Rótulo do eixo X
            y_label: Rótulo do eixo Y
        """
        self.title = title
        self.chart.setTitle(self.title)
        
        series = QLineSeries()
        for category, value in zip(categories, data):
            series.append(categories.index(category), value)
        
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        
        axis_x = QValueAxis()
        axis_x.setTitleText(x_label)
        axis_x.setLabelFormat('%d')
        axis_x.setTickCount(len(categories))
        self.chart.setAxisX(axis_x, series)
        
        axis_y = QValueAxis()
        axis_y.setLabelFormat('%i')
        axis_y.setTitleText(y_label)
        self.chart.setAxisY(axis_y, series)
