from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.service_order_controller import ServiceOrderController
from ui.dialogs.service_order_dialog import ServiceOrderDialog
from ui.dialogs.print_dialog import PrintDialog
import config

logger = logging.getLogger(config.APP_NAME)

class ServiceOrdersTab(QWidget):
    """Aba de ordens de serviço"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service_order_controller = ServiceOrderController()
        self.setup_ui()
        self.load_orders()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Ordens de Serviço")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Nova Ordem")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por número, veículo ou cliente...")
        self.search_input.textChanged.connect(self.filter_orders)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de ordens
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Número", "Data", "Veículo", "Cliente", "Status", "Valor Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_orders(self):
        """Carrega as ordens de serviço do banco de dados para a tabela"""
        orders = self.service_order_controller.get_all_orders()
        self.table.setRowCount(len(orders))
        
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(order['number']))
            self.table.setItem(row, 2, QTableWidgetItem(order['open_date'].split()[0]))
            self.table.setItem(row, 3, QTableWidgetItem(order.get('vehicle_plate', 'N/A')))
            self.table.setItem(row, 4, QTableWidgetItem(order.get('client_name', 'N/A')))
            self.table.setItem(row, 5, QTableWidgetItem(order['status']))
            self.table.setItem(row, 6, QTableWidgetItem(f"R$ {order['total_value']:.2f}"))
            
            # Armazenar o ID da ordem como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, order['id'])
            
            # Colorir a linha de acordo com o status
            if order['status'] == 'em andamento':
                for col in range(7):
                    self.table.item(row, col).setBackground(Qt.yellow)
            elif order['status'] == 'concluído':
                for col in range(7):
                    self.table.item(row, col).setBackground(Qt.cyan)
            elif order['status'] == 'entregue':
                for col in range(7):
                    self.table.item(row, col).setBackground(Qt.green)
    
    def filter_orders(self):
        """Filtra as ordens com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 5):  # Colunas de número, data, veículo e cliente
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar uma nova ordem de serviço"""
        dialog = ServiceOrderDialog(self)
        if dialog.exec_():
            self.load_orders()
    
    def show_edit_dialog(self, order_id):
        """Exibe o diálogo para editar uma ordem de serviço existente"""
        order = self.service_order_controller.get_order_by_id(order_id)
        if order:
            dialog = ServiceOrderDialog(self, order)
            if dialog.exec_():
                self.load_orders()
        else:
            QMessageBox.warning(self, "Erro", "Ordem de serviço não encontrada.")
    
    def show_print_dialog(self, order_id):
        """Exibe o diálogo para imprimir uma ordem de serviço"""
        dialog = PrintDialog(self, order_id)
        dialog.exec_()
    
    def confirm_delete(self, order_id):
        """Confirma a exclusão de uma ordem de serviço"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir esta ordem de serviço? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.service_order_controller.delete_order(order_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Ordem de serviço excluída com sucesso!")
                self.load_orders()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir a ordem de serviço.")
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID da ordem selecionada
        row = indexes[0].row()
        order_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        print_action = menu.addAction("Imprimir")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(order_id)
        elif action == print_action:
            self.show_print_dialog(order_id)
        elif action == delete_action:
            self.confirm_delete(order_id)