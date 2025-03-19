from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.client_controller import ClientController
from ui.dialogs.client_dialog import ClientDialog
import config

logger = logging.getLogger(config.APP_NAME)

class ClientsTab(QWidget):
    """Aba de clientes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client_controller = ClientController()
        self.setup_ui()
        self.load_clients()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Clientes")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Novo Cliente")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por nome, documento ou email...")
        self.search_input.textChanged.connect(self.filter_clients)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de clientes
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "CPF/CNPJ", "Endereço", "Telefone", "Email"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_clients(self):
        """Carrega os clientes do banco de dados para a tabela"""
        clients = self.client_controller.get_all_clients()
        self.table.setRowCount(len(clients))
        
        for row, client in enumerate(clients):
            self.table.setItem(row, 0, QTableWidgetItem(str(client['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(client['name']))
            self.table.setItem(row, 2, QTableWidgetItem(client['document']))
            self.table.setItem(row, 3, QTableWidgetItem(client['address']))
            self.table.setItem(row, 4, QTableWidgetItem(client['phone']))
            self.table.setItem(row, 5, QTableWidgetItem(client['email']))
            
            # Armazenar o ID do cliente como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, client['id'])
    
    def filter_clients(self):
        """Filtra os clientes com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 6):  # Colunas de nome, documento, endereço, telefone e email
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar um novo cliente"""
        dialog = ClientDialog(self)
        if dialog.exec_():
            self.load_clients()
    
    def show_edit_dialog(self, client_id):
        """Exibe o diálogo para editar um cliente existente"""
        client = self.client_controller.get_client_by_id(client_id)
        if client:
            dialog = ClientDialog(self, client)
            if dialog.exec_():
                self.load_clients()
        else:
            QMessageBox.warning(self, "Erro", "Cliente não encontrado.")
    
    def confirm_delete(self, client_id):
        """Confirma a exclusão de um cliente"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir este cliente? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.client_controller.delete_client(client_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.load_clients()
            else:
                QMessageBox.critical(
                    self, "Erro", 
                    "Não foi possível excluir o cliente. Ele pode estar associado a veículos."
                )
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID do cliente selecionado
        row = indexes[0].row()
        client_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(client_id)
        elif action == delete_action:
            self.confirm_delete(client_id)