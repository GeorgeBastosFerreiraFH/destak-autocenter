from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox, 
                            QDateEdit)
from PyQt5.QtCore import Qt, QDate
import logging
from controllers.employee_controller import EmployeeController
import config

logger = logging.getLogger(config.APP_NAME)

class EmployeeDialog(QDialog):
    """Diálogo para adicionar ou editar funcionários"""
    
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.employee = employee
        self.employee_controller = EmployeeController()
        
        self.setWindowTitle("Adicionar Funcionário" if not employee else "Editar Funcionário")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
        # Se estiver editando, preencher os campos
        if self.employee:
            self.fill_form()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        # Nome
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nome completo")
        form_layout.addRow("Nome:", self.name_edit)
        
        # Documento (CPF)
        self.document_edit = QLineEdit()
        self.document_edit.setPlaceholderText("000.000.000-00")
        form_layout.addRow("CPF:", self.document_edit)
        
        # Cargo
        self.role_edit = QLineEdit()
        self.role_edit.setPlaceholderText("Mecânico, Atendente, etc.")
        form_layout.addRow("Cargo:", self.role_edit)
        
        # Data de contratação
        self.hire_date_edit = QDateEdit()
        self.hire_date_edit.setCalendarPopup(True)
        self.hire_date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Data de Contratação:", self.hire_date_edit)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_employee)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def fill_form(self):
        """Preenche o formulário com os dados do funcionário"""
        self.name_edit.setText(self.employee['name'])
        self.document_edit.setText(self.employee['document'])
        self.role_edit.setText(self.employee['role'])
        
        # Data de contratação
        hire_date = QDate.fromString(self.employee['hire_date'], "yyyy-MM-dd")
        self.hire_date_edit.setDate(hire_date)
    
    def save_employee(self):
        """Salva o funcionário no banco de dados"""
        # Validar campos
        if not self.validate_form():
            return
        
        try:
            employee_data = {
                'name': self.name_edit.text().strip(),
                'document': self.document_edit.text().strip(),
                'role': self.role_edit.text().strip(),
                'hire_date': self.hire_date_edit.date().toString("yyyy-MM-dd")
            }
            
            if self.employee:
                # Atualizar funcionário existente
                success = self.employee_controller.update_employee(self.employee['id'], employee_data)
                message = "Funcionário atualizado com sucesso!"
            else:
                # Inserir novo funcionário
                employee_id = self.employee_controller.add_employee(employee_data)
                success = employee_id is not None
                message = "Funcionário adicionado com sucesso!"
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o funcionário.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar funcionário: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o funcionário: {str(e)}")
    
    def validate_form(self):
        """Valida os campos do formulário"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o nome do funcionário.")
            return False
        
        if not self.document_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o CPF do funcionário.")
            return False
        
        if not self.role_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o cargo do funcionário.")
            return False
        
        return True