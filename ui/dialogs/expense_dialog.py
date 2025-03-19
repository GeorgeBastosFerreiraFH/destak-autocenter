from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QLabel, 
                            QMessageBox, QDateEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
import logging
from controllers.expense_controller import ExpenseController
import config

logger = logging.getLogger(config.APP_NAME)

class ExpenseDialog(QDialog):
    """Diálogo para adicionar ou editar gastos"""
    
    def __init__(self, parent=None, expense=None):
        super().__init__(parent)
        self.expense = expense
        self.expense_controller = ExpenseController()
        
        self.setWindowTitle("Adicionar Gasto" if not expense else "Editar Gasto")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
        # Se estiver editando, preencher os campos
        if self.expense:
            self.fill_form()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        # Data
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("Data:", self.date_edit)
        
        # Descrição
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Descrição do gasto")
        form_layout.addRow("Descrição:", self.description_edit)
        
        # Valor
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0.01, 999999.99)
        self.value_spin.setDecimals(2)
        self.value_spin.setSingleStep(10)
        self.value_spin.setPrefix("R$ ")
        form_layout.addRow("Valor:", self.value_spin)
        
        # Categoria
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "peças", "mão de obra", "ferramentas", "aluguel", 
            "energia", "água", "internet", "outros"
        ])
        form_layout.addRow("Categoria:", self.category_combo)
        
        # Forma de pagamento
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.addItems(["pix", "cartão", "dinheiro", "boleto"])
        form_layout.addRow("Forma de Pagamento:", self.payment_method_combo)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_expense)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def fill_form(self):
        """Preenche o formulário com os dados do gasto"""
        # Data
        date = QDate.fromString(self.expense['date'], "yyyy-MM-dd")
        self.date_edit.setDate(date)
        
        self.description_edit.setText(self.expense['description'])
        self.value_spin.setValue(self.expense['value'])
        
        # Categoria
        index = self.category_combo.findText(self.expense['category'])
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        
        # Forma de pagamento
        index = self.payment_method_combo.findText(self.expense['payment_method'])
        if index >= 0:
            self.payment_method_combo.setCurrentIndex(index)
    
    def save_expense(self):
        """Salva o gasto no banco de dados"""
        # Validar campos
        if not self.validate_form():
            return
        
        try:
            expense_data = {
                'date': self.date_edit.date().toString("yyyy-MM-dd"),
                'description': self.description_edit.text().strip(),
                'value': self.value_spin.value(),
                'category': self.category_combo.currentText(),
                'payment_method': self.payment_method_combo.currentText()
            }
            
            if self.expense:
                # Atualizar gasto existente
                success = self.expense_controller.update_expense(self.expense['id'], expense_data)
                message = "Gasto atualizado com sucesso!"
            else:
                # Inserir novo gasto
                expense_id = self.expense_controller.add_expense(expense_data)
                success = expense_id is not None
                message = "Gasto adicionado com sucesso!"
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar o gasto.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar gasto: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o gasto: {str(e)}")
    
    def validate_form(self):
        """Valida os campos do formulário"""
        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe a descrição do gasto.")
            return False
        
        if self.value_spin.value() <= 0:
            QMessageBox.warning(self, "Validação", "O valor deve ser maior que zero.")
            return False
        
        return True