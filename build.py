import os
import sys
import shutil
import subprocess

def build_executable():
    """Cria o executável do aplicativo"""
    print("Criando executável com PyInstaller...")
    
    # Limpar diretórios de build anteriores
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    # Configurar opções do PyInstaller
    icon_path = os.path.abspath("resources/icons/app_icon.ico")
    resources_path = os.path.abspath("resources")
    
    # Comando para o PyInstaller
    cmd = [
        "pyinstaller",
        "--name=AutoRepairShop",
        "--windowed",
        f"--icon={icon_path}",
        f"--add-data={resources_path};resources",
        "--hidden-import=sqlite3",
        "--hidden-import=requests",
        "--hidden-import=reportlab",
        "--hidden-import=PIL",
        "main.py"
    ]
    
    # Executar o comando
    subprocess.run(cmd)
    
    print("Executável criado com sucesso!")
    print("O executável está disponível em: dist/AutoRepairShop/AutoRepairShop.exe")

if __name__ == "__main__":
    build_executable()