from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.expense_controller import ExpenseController
from ui.dialogs.expense_dialog import ExpenseDialog
import config

logger = logging.getLogger(config.APP_NAME)

class ExpensesTab(QWidget):
    """Aba de gastos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.expense_controller = ExpenseController()
        self.setup_ui()
        self.load_expenses()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Gastos")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Novo Gasto")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por descrição ou categoria...")
        self.search_input.textChanged.connect(self.filter_expenses)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de gastos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Data", "Descrição", "Valor", "Categoria", "Forma de Pagamento"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_expenses(self):
        """Carrega os gastos do banco de dados para a tabela"""
        expenses = self.expense_controller.get_all_expenses()
        self.table.setRowCount(len(expenses))
        
        for row, expense in enumerate(expenses):
            self.table.setItem(row, 0, QTableWidgetItem(str(expense['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(expense['date']))
            self.table.setItem(row, 2, QTableWidgetItem(expense['description']))
            self.table.setItem(row, 3, QTableWidgetItem(f"R$ {expense['value']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(expense['category']))
            self.table.setItem(row, 5, QTableWidgetItem(expense['payment_method']))
            
            # Armazenar o ID do gasto como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, expense['id'])
    
    def filter_expenses(self):
        """Filtra os gastos com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 5):  # Colunas de data, descrição, valor e categoria
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar um novo gasto"""
        dialog = ExpenseDialog(self)
        if dialog.exec_():
            self.load_expenses()
    
    def show_edit_dialog(self, expense_id):
        """Exibe o diálogo para editar um gasto existente"""
        expense = self.expense_controller.get_expense_by_id(expense_id)
        if expense:
            dialog = ExpenseDialog(self, expense)
            if dialog.exec_():
                self.load_expenses()
        else:
            QMessageBox.warning(self, "Erro", "Gasto não encontrado.")
    
    def confirm_delete(self, expense_id):
        """Confirma a exclusão de um gasto"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir este gasto? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.expense_controller.delete_expense(expense_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Gasto excluído com sucesso!")
                self.load_expenses()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir o gasto.")
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID do gasto selecionado
        row = indexes[0].row()
        expense_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(expense_id)
        elif action == delete_action:
            self.confirm_delete(expense_id)