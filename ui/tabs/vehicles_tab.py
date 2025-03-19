from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QLineEdit, QLabel, QMessageBox, QMenu)
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QIcon
import logging
from controllers.vehicle_controller import VehicleController
from ui.dialogs.vehicle_dialog import VehicleDialog
import config

logger = logging.getLogger(config.APP_NAME)

class VehiclesTab(QWidget):
    """Aba de veículos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vehicle_controller = VehicleController()
        self.setup_ui()
        self.load_vehicles()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        title = QLabel("Veículos")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)
        
        # Botão de adicionar
        self.add_button = QPushButton("Novo Veículo")
        self.add_button.setIcon(QIcon("resources/icons/add.png"))
        self.add_button.clicked.connect(self.show_add_dialog)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        layout.addLayout(header_layout)
        
        # Campo de busca
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite para filtrar por placa, marca ou modelo...")
        self.search_input.textChanged.connect(self.filter_vehicles)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Tabela de veículos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Placa", "Marca", "Modelo", "Ano", "Cor", "Cliente"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_vehicles(self):
        """Carrega os veículos do banco de dados para a tabela"""
        vehicles = self.vehicle_controller.get_all_vehicles()
        self.table.setRowCount(len(vehicles))
        
        for row, vehicle in enumerate(vehicles):
            self.table.setItem(row, 0, QTableWidgetItem(str(vehicle['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(vehicle['plate']))
            self.table.setItem(row, 2, QTableWidgetItem(vehicle['brand']))
            self.table.setItem(row, 3, QTableWidgetItem(vehicle['model']))
            self.table.setItem(row, 4, QTableWidgetItem(str(vehicle['year'])))
            self.table.setItem(row, 5, QTableWidgetItem(vehicle['color']))
            self.table.setItem(row, 6, QTableWidgetItem(vehicle.get('client_name', 'N/A')))
            
            # Armazenar o ID do veículo como dado do item
            self.table.item(row, 0).setData(Qt.UserRole, vehicle['id'])
    
    def filter_vehicles(self):
        """Filtra os veículos com base no texto digitado"""
        search_text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(1, 7):  # Colunas de placa, marca, modelo, ano, cor e cliente
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)
    
    def show_add_dialog(self):
        """Exibe o diálogo para adicionar um novo veículo"""
        dialog = VehicleDialog(self)
        if dialog.exec_():
            self.load_vehicles()
    
    def show_edit_dialog(self, vehicle_id):
        """Exibe o diálogo para editar um veículo existente"""
        vehicle = self.vehicle_controller.get_vehicle_by_id(vehicle_id)
        if vehicle:
            dialog = VehicleDialog(self, vehicle)
            if dialog.exec_():
                self.load_vehicles()
        else:
            QMessageBox.warning(self, "Erro", "Veículo não encontrado.")
    
    def confirm_delete(self, vehicle_id):
        """Confirma a exclusão de um veículo"""
        reply = QMessageBox.question(
            self, 'Confirmar Exclusão',
            'Tem certeza que deseja excluir este veículo? Esta ação não pode ser desfeita.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.vehicle_controller.delete_vehicle(vehicle_id)
            if success:
                QMessageBox.information(self, "Sucesso", "Veículo excluído com sucesso!")
                self.load_vehicles()
            else:
                QMessageBox.critical(
                    self, "Erro", 
                    "Não foi possível excluir o veículo. Ele pode estar associado a ordens de serviço."
                )
    
    def show_context_menu(self, position):
        """Exibe o menu de contexto ao clicar com o botão direito na tabela"""
        indexes = self.table.selectedIndexes()
        if not indexes:
            return
        
        # Obter o ID do veículo selecionado
        row = indexes[0].row()
        vehicle_id = self.table.item(row, 0).data(Qt.UserRole)
        
        # Criar menu
        menu = QMenu()
        edit_action = menu.addAction("Editar")
        delete_action = menu.addAction("Excluir")
        
        # Executar ação selecionada
        action = menu.exec_(self.table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.show_edit_dialog(vehicle_id)
        elif action == delete_action:
            self.confirm_delete(vehicle_id)