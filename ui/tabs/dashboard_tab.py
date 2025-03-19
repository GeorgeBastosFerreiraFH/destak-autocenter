import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from controllers.client_controller import ClientController
from controllers.vehicle_controller import VehicleController
from controllers.service_order_controller import ServiceOrderController
from controllers.expense_controller import ExpenseController
from controllers.part_controller import PartController
from controllers.employee_controller import EmployeeController

from ui.widgets.chart_widget import PieChartWidget, BarChartWidget, LineChartWidget

class DashboardTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client_controller = ClientController()
        self.vehicle_controller = VehicleController()
        self.service_order_controller = ServiceOrderController()
        self.expense_controller = ExpenseController()
        self.part_controller = PartController()
        self.employee_controller = EmployeeController()
        
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Dashboard")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Cards de estatísticas
        stats_layout = QGridLayout()
        
        # Criar cards
        self.clients_card = self.create_stat_card("Clientes", "0", "users")
        self.vehicles_card = self.create_stat_card("Veículos", "0", "car")
        self.orders_card = self.create_stat_card("Ordens de Serviço", "0", "file")
        self.revenue_card = self.create_stat_card("Faturamento", "R$ 0,00", "dollar")
        self.expenses_card = self.create_stat_card("Despesas", "R$ 0,00", "shopping-cart")
        self.profit_card = self.create_stat_card("Lucro", "R$ 0,00", "trending-up")
        
        # Adicionar cards ao layout
        stats_layout.addWidget(self.clients_card, 0, 0)
        stats_layout.addWidget(self.vehicles_card, 0, 1)
        stats_layout.addWidget(self.orders_card, 0, 2)
        stats_layout.addWidget(self.revenue_card, 1, 0)
        stats_layout.addWidget(self.expenses_card, 1, 1)
        stats_layout.addWidget(self.profit_card, 1, 2)
        
        main_layout.addLayout(stats_layout)
        
        # Gráficos
        charts_layout = QHBoxLayout()
        
        # Gráfico de pizza - Status das ordens
        status_chart_container = QFrame()
        status_chart_container.setFrameShape(QFrame.StyledPanel)
        status_chart_layout = QVBoxLayout(status_chart_container)
        status_chart_title = QLabel("Status das Ordens")
        status_chart_title.setFont(QFont("Arial", 12, QFont.Bold))
        status_chart_layout.addWidget(status_chart_title)
        
        self.status_chart = PieChartWidget()
        status_chart_layout.addWidget(self.status_chart)
        
        # Gráfico de barras - Faturamento por mês
        revenue_chart_container = QFrame()
        revenue_chart_container.setFrameShape(QFrame.StyledPanel)
        revenue_chart_layout = QVBoxLayout(revenue_chart_container)
        revenue_chart_title = QLabel("Faturamento por Mês")
        revenue_chart_title.setFont(QFont("Arial", 12, QFont.Bold))
        revenue_chart_layout.addWidget(revenue_chart_title)
        
        self.revenue_chart = BarChartWidget()
        revenue_chart_layout.addWidget(self.revenue_chart)
        
        # Gráfico de pizza - Despesas por categoria
        expense_chart_container = QFrame()
        expense_chart_container.setFrameShape(QFrame.StyledPanel)
        expense_chart_layout = QVBoxLayout(expense_chart_container)
        expense_chart_title = QLabel("Despesas por Categoria")
        expense_chart_title.setFont(QFont("Arial", 12, QFont.Bold))
        expense_chart_layout.addWidget(expense_chart_title)
        
        self.expense_chart = PieChartWidget()
        expense_chart_layout.addWidget(self.expense_chart)
        
        # Adicionar gráficos ao layout
        charts_layout.addWidget(status_chart_container)
        charts_layout.addWidget(revenue_chart_container)
        charts_layout.addWidget(expense_chart_container)
        
        main_layout.addLayout(charts_layout)
        
        self.setLayout(main_layout)
    
    def create_stat_card(self, title, value, icon_name):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setProperty("card", "true")  # Para estilização CSS
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setProperty("value", "true")  # Para estilização CSS
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        # Armazenar o label de valor para atualização posterior
        card.value_label = value_label
        
        return card
    
    def load_data(self):
        try:
            # Carregar estatísticas
            clients = self.client_controller.get_all_clients()
            vehicles = self.vehicle_controller.get_all_vehicles()
            orders = self.service_order_controller.get_all_service_orders()
            expenses = self.expense_controller.get_all_expenses()
            
            # Calcular valores
            client_count = len(clients)
            vehicle_count = len(vehicles)
            order_count = len(orders)
            
            total_revenue = sum(order['total_value'] for order in orders)
            total_expenses = sum(expense['value'] for expense in expenses)
            profit = total_revenue - total_expenses
            
            # Atualizar cards
            self.clients_card.value_label.setText(str(client_count))
            self.vehicles_card.value_label.setText(str(vehicle_count))
            self.orders_card.value_label.setText(str(order_count))
            self.revenue_card.value_label.setText(f"R$ {total_revenue:.2f}")
            self.expenses_card.value_label.setText(f"R$ {total_expenses:.2f}")
            self.profit_card.value_label.setText(f"R$ {profit:.2f}")
            
            # Dados para gráfico de status das ordens
            status_counts = {'em andamento': 0, 'concluído': 0, 'entregue': 0}
            for order in orders:
                status = order['status']
                if status in status_counts:
                    status_counts[status] += 1
            
            # Atualizar gráfico de status
            status_data = list(status_counts.values())
            status_labels = list(status_counts.keys())
            self.status_chart.update_chart(status_data, status_labels, "Status das Ordens")
            
            # Dados para gráfico de faturamento por mês
            months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
            revenue_data = [1200, 1800, 2200, 1900, 2500, 3000]  # Dados de exemplo
            self.revenue_chart.update_chart(revenue_data, months, "Faturamento por Mês", "Mês", "Valor (R$)")
            
            # Dados para gráfico de despesas por categoria
            expense_categories = {}
            for expense in expenses:
                category = expense['category']
                if category not in expense_categories:
                    expense_categories[category] = 0
                expense_categories[category] += expense['value']
            
            # Atualizar gráfico de despesas
            expense_data = list(expense_categories.values())
            expense_labels = list(expense_categories.keys())
            self.expense_chart.update_chart(expense_data, expense_labels, "Despesas por Categoria")
            
        except Exception as e:
            print(f"Erro ao carregar dados do dashboard: {str(e)}")
