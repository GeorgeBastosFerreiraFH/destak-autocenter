from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QPushButton, QLabel, QMessageBox, 
                            QDoubleSpinBox, QSpinBox)
from PyQt5.QtCore import Qt
import logging
from controllers.part_controller import PartController
import config

logger = logging.getLogger(config.APP_NAME)

class PartDialog(QDialog):
    """Diálogo para adicionar ou editar peças"""
    
    def __init__(self, parent=None, part=None):
        super().__init__(parent)
        self.part = part
        self.part_controller = PartController()
        
        self.setWindowTitle("Adicionar Peça" if not part else "Editar Peça")
        self.setMinimumWidth(400)
        
        self.setup_ui()
        
        # Se estiver editando, preencher os campos
        if self.part:
            self.fill_form()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        # Código
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("P001")
        form_layout.addRow("Código:", self.code_edit)
        
        # Descrição
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Descrição da peça")
        form_layout.addRow("Descrição:", self.description_edit)
        
        # Quantidade em estoque
        self.stock_quantity_spin = QSpinBox()
        self.stock_quantity_spin.setRange(0, 9999)
        form_layout.addRow("Quantidade em Estoque:", self.stock_quantity_spin)
        
        # Preço de compra
        self.buy_price_spin = QDoubleSpinBox()
        self.buy_price_spin.setRange(0, 99999.99)
        self.buy_price_spin.setDecimals(2)
        self.buy_price_spin.setSingleStep(1)
        self.buy_price_spin.setPrefix("R$ ")
        form_layout.addRow("Preço de Compra:", self.buy_price_spin)
        
        # Preço de venda
        self.sell_price_spin = QDoubleSpinBox()
        self.sell_price_spin.setRange(0, 99999.99)
        self.sell_price_spin.setDecimals(2)
        self.sell_price_spin.setSingleStep(1)
        self.sell_price_spin.setPrefix("R$ ")
        form_layout.addRow("Preço de Venda:", self.sell_price_spin)
        
        layout.addLayout(form_layout)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_part)
        self.save_button.setDefault(True)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def fill_form(self):
        """Preenche o formulário com os dados da peça"""
        self.code_edit.setText(self.part['code'])
        self.description_edit.setText(self.part['description'])
        self.stock_quantity_spin.setValue(self.part['stock_quantity'])
        self.buy_price_spin.setValue(self.part['buy_price'])
        self.sell_price_spin.setValue(self.part['sell_price'])
    
    def save_part(self):
        """Salva a peça no banco de dados"""
        # Validar campos
        if not self.validate_form():
            return
        
        try:
            part_data = {
                'code': self.code_edit.text().strip(),
                'description': self.description_edit.text().strip(),
                'stock_quantity': self.stock_quantity_spin.value(),
                'buy_price': self.buy_price_spin.value(),
                'sell_price': self.sell_price_spin.value()
            }
            
            if self.part:
                # Atualizar peça existente
                success = self.part_controller.update_part(self.part['id'], part_data)
                message = "Peça atualizada com sucesso!"
            else:
                # Inserir nova peça
                part_id = self.part_controller.add_part(part_data)
                success = part_id is not None
                message = "Peça adicionada com sucesso!"
            
            if success:
                QMessageBox.information(self, "Sucesso", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", "Não foi possível salvar a peça.")
                
        except Exception as e:
            logger.error(f"Erro ao salvar peça: {str(e)}")
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar a peça: {str(e)}")
    
    def validate_form(self):
        """Valida os campos do formulário"""
        if not self.code_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe o código da peça.")
            return False
        
        if not self.description_edit.text().strip():
            QMessageBox.warning(self, "Validação", "Informe a descrição da peça.")
            return False
        
        return True