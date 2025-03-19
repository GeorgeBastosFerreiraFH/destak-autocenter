from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.part_controller import PartController
from ui.dialogs.part_dialog import PartDialog
import config

logger = logging.getLogger(config.APP_NAME)

class PartsTab(QWidget):
    """Aba de peças"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.part_controller = PartController()
        self.setup_ui()
        self.load_parts()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Peças")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Nova Peça")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por código ou descrição...")
        self.search_input.textChanged.connect(self.filter_parts)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de peças
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Descrição", "Estoque", "Preço de Compra", "Preço de Venda"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_parts(self):
        """Carrega as peças do banco de dados para a tabela"""
        parts = self.part_controller.get_all_parts()
        self.table.setRowCount(len(parts))
        
        for row, part in enumerate(parts):
            self.table.setItem(row, 0, QTableWidgetItem(str(part['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(part['code']))
            self.table.setItem(row, 2, QTableWidgetItem(part['description']))
            self.table.setItem(row, 3, QTableWidgetItem(str(part['stock_quantity'])))
            self.table.setItem(row, 4, QTableWidgetItem(f"R$ {part['buy_price']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(f"R$ {part['sell_price']:.2f}"))
            
            # Armazenar o ID da peça como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, part['id'])
            
            # Colorir a linha se o estoque estiver baixo
            if part['stock_quantity'] <= 5:
                for col in range(6):
                    self.table.item(row, col).setBackground(Qt.red)
    
    def filter_parts(self):
        """Filtra as peças com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 3):  # Colunas de código e descrição
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar uma nova peça"""
        dialog = PartDialog(self)
        if dialog.exec_():
            self.load_parts()
    
    def show_edit_dialog(self, part_id):
        """Exibe o diálogo para editar uma peça existente"""
        part = self.part_controller.get_part_by_id(part_id)
        if part:
            dialog = PartDialog(self, part)
            if dialog.exec_():
                self.load_parts()
        else:
            QMessageBox.warning(self, "Erro", "Peça não encontrada.")
    
    def confirm_delete(self, part_id):
        """Confirma a exclusão de uma peça"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir esta peça? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.part_controller.delete_part(part_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Peça excluída com sucesso!")
                self.load_parts()
            else:
                QMessageBox.critical(
                    self, "Erro", 
                    "Não foi possível excluir a peça. Ela pode estar associada a ordens de serviço."
                )
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID da peça selecionada
        row = indexes[0].row()
        part_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(part_id)
        elif action == delete_action:
            self.confirm_delete(part_id)