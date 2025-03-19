from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPoint, QBuffer, QIODevice
import base64
from io import BytesIO

class SignatureWidget(QWidget):
    """Widget para captura de assinaturas"""
    
    def __init__(self, parent=None, title="Assinatura"):
        super().__init__(parent)
        self.title = title
        self.drawing = False
        self.lastPoint = QPoint()
        self.image = QPixmap(400, 200)
        self.image.fill(Qt.white)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(title_label)
        
        # Área de desenho
        self.signature_area = QLabel()
        self.signature_area.setPixmap(self.image)
        self.signature_area.setFixedSize(400, 200)
        self.signature_area.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        layout.addWidget(self.signature_area)
        
        # Botões
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Limpar")
        self.clear_button.clicked.connect(self.clear_signature)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos() - self.signature_area.pos()
    
    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            pos = event.pos() - self.signature_area.pos()
            
            # Verificar se o ponto está dentro da área de assinatura
            if (pos.x() >= 0 and pos.x() < self.image.width() and 
                pos.y() >= 0 and pos.y() < self.image.height()):
                
                painter = QPainter(self.image)
                painter.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.drawLine(self.lastPoint, pos)
                painter.end()
                
                self.signature_area.setPixmap(self.image)
                self.lastPoint = pos
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
    
    def clear_signature(self):
        """Limpa a assinatura"""
        self.image.fill(Qt.white)
        self.signature_area.setPixmap(self.image)
    
    def get_signature_base64(self):
        """Retorna a assinatura como uma string base64"""
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)  # Abre o buffer para escrita
        self.image.save(buffer, "PNG")  # Salva a imagem no buffer
        return base64.b64encode(buffer.data()).decode()  # Codifica o conteúdo do buffer em base64
    
    def set_signature_from_base64(self, base64_data):
        """Define a assinatura a partir de uma string base64"""
        if not base64_data:
            self.clear_signature()
            return
        
        try:
            binary_data = base64.b64decode(base64_data)
            pixmap = QPixmap()
            if not pixmap.loadFromData(binary_data):
                raise ValueError("Falha ao carregar os dados da assinatura.")
            self.image = pixmap
            self.signature_area.setPixmap(self.image)
        except Exception as e:
            print(f"Erro ao carregar assinatura: {str(e)}")
            self.clear_signature()

    
    def has_signature(self):
        """Verifica se há uma assinatura"""
        # Cria uma cópia da imagem para verificação
        temp_image = self.image.copy()
        # Converte para imagem e verifica se há pixels não brancos
        image = temp_image.toImage()
        
        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixel(x, y) != QColor(Qt.white).rgb():
                    return True
        
        return False