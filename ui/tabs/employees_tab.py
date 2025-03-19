from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.employee_controller import EmployeeController
from ui.dialogs.employee_dialog import EmployeeDialog
import config

logger = logging.getLogger(config.APP_NAME)

class EmployeesTab(QWidget):
    """Aba de funcionários"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.employee_controller = EmployeeController()
        self.setup_ui()
        self.load_employees()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Funcionários")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Novo Funcionário")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por nome ou cargo...")
        self.search_input.textChanged.connect(self.filter_employees)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de funcionários
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Cargo", "Data de Contratação"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_employees(self):
        """Carrega os funcionários do banco de dados para a tabela"""
        employees = self.employee_controller.get_all_employees()
        self.table.setRowCount(len(employees))
        
        for row, employee in enumerate(employees):
            self.table.setItem(row, 0, QTableWidgetItem(str(employee['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(employee['name']))
            self.table.setItem(row, 2, QTableWidgetItem(employee['document']))
            self.table.setItem(row, 3, QTableWidgetItem(employee['role']))
            self.table.setItem(row, 4, QTableWidgetItem(employee['hire_date']))
            
            # Armazenar o ID do funcionário como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, employee['id'])
    
    def filter_employees(self):
        """Filtra os funcionários com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 4):  # Colunas de nome, CPF e cargo
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar um novo funcionário"""
        dialog = EmployeeDialog(self)
        if dialog.exec_():
            self.load_employees()
    
    def show_edit_dialog(self, employee_id):
        """Exibe o diálogo para editar um funcionário existente"""
        employee = self.employee_controller.get_employee_by_id(employee_id)
        if employee:
            dialog = EmployeeDialog(self, employee)
            if dialog.exec_():
                self.load_employees()
        else:
            QMessageBox.warning(self, "Erro", "Funcionário não encontrado.")
    
    def confirm_delete(self, employee_id):
        """Confirma a exclusão de um funcionário"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir este funcionário? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.employee_controller.delete_employee(employee_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Funcionário excluído com sucesso!")
                self.load_employees()
            else:
                QMessageBox.critical(
                    self, "Erro", 
                    "Não foi possível excluir o funcionário. Ele pode estar associado a ordens de serviço."
                )
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID do funcionário selecionado
        row = indexes[0].row()
        employee_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(employee_id)
        elif action == delete_action:
            self.confirm_delete(employee_id)