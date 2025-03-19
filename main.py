# main.py

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import config
from database.db_manager import DatabaseManager
from database.models import setup_database  # Garantir que a importação esteja correta

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(config.APP_NAME)

def main():
    # Iniciar aplicação
    app = QApplication(sys.argv)
    
    # Aplicar folha de estilo
    try:
        with open(config.CSS_FILE, "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        logger.error(f"Erro ao carregar CSS: {str(e)}")
    
    # Verificar se o arquivo splash.jpeg existe
    splash_path = os.path.join("resources", "images", "splash.jpeg")
    if not os.path.exists(splash_path):
        logger.warning(f"Arquivo {splash_path} não encontrado!")
        # Criar pasta resources/images se não existir
        os.makedirs(os.path.dirname(splash_path), exist_ok=True)
        
        # Criar um splash screen básico (caso o arquivo não exista)
        from PIL import Image, ImageDraw, ImageFont
        
        # Configurações da imagem
        width, height = 500, 300
        background_color = (44, 62, 80)  # #2c3e50 (azul escuro)
        accent_color = (52, 152, 219)    # #3498db (azul claro)
        text_color = (255, 255, 255)     # branco
        
        # Criar imagem com fundo azul escuro
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Desenhar retângulo decorativo
        draw.rectangle([(0, height-40), (width, height)], fill=accent_color)
        
        # Adicionar título
        try:
            title_font = ImageFont.load_default()
            title_text = "Destak AutoCenter"
            title_size = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_size[2] - title_size[0]
            title_height = title_size[3] - title_size[1]
            title_position = ((width - title_width) // 2, 50)
            draw.text(title_position, title_text, font=title_font, fill=text_color)
            
            # Adicionar subtítulo
            subtitle_font = ImageFont.load_default()
            subtitle_text = "Sistema de Gerenciamento de Oficina"
            subtitle_size = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
            subtitle_width = subtitle_size[2] - subtitle_size[0]
            subtitle_position = ((width - subtitle_width) // 2, 100)
            draw.text(subtitle_position, subtitle_text, font=subtitle_font, fill=text_color)
            
            # Adicionar texto de carregando
            loading_text = "Carregando..."
            loading_position = (20, height - 30)
            draw.text(loading_position, loading_text, font=subtitle_font, fill=text_color)
            
            # Salvar a imagem
            img.save(splash_path)
            logger.info("Imagem splash.jpeg criada com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao criar splash screen: {str(e)}")
    
    # Criar e mostrar o splash screen
    splash_pix = QPixmap(splash_path)
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.setEnabled(False)
    splash.show()
    
    # Garantir que o splash seja exibido
    app.processEvents()
    
    # Inicializar banco de dados
    splash.showMessage("Inicializando banco de dados...", Qt.AlignBottom | Qt.AlignLeft, Qt.white)
    app.processEvents()
    
    db_manager = DatabaseManager()
    setup_database(config.DB_PATH)  # Chamando a função para configurar o banco
    
    # Importar a janela principal aqui para que o splash seja exibido enquanto ela carrega
    splash.showMessage("Carregando interface...", Qt.AlignBottom | Qt.AlignLeft, Qt.white)
    app.processEvents()
    
    from ui.main_window import MainWindow
    
    # Criar e configurar a janela principal
    window = MainWindow()
    
    # Fechar o splash e mostrar a janela principal após 2 segundos
    QTimer.singleShot(2000, lambda: show_main_window(window, splash))
    
    sys.exit(app.exec_())

def show_main_window(window, splash):
    window.show()
    splash.finish(window)

if __name__ == "__main__":
    main()
