#!/usr/bin/env python3
"""
Script para instalar todas as dependências necessárias para o mapa temático
"""

import subprocess
import sys
import os

def instalar_pacote(pacote):
    """Instala um pacote via pip"""
    try:
        print(f"📦 Instalando {pacote}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pacote])
        print(f"✅ {pacote} instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar {pacote}: {e}")
        return False

def main():
    print("🚀 Instalando dependências para o mapa temático...")
    print()
    
    # Lista de dependências
    dependencias = [
        "geopandas",
        "folium", 
        "pyproj",
        "pyodbc",
        "pandas",
        "numpy",
        "branca",
        "shapely",
        "fiona"
    ]
    
    # Instalar cada dependência
    sucessos = 0
    falhas = 0
    
    for pacote in dependencias:
        if instalar_pacote(pacote):
            sucessos += 1
        else:
            falhas += 1
        print()
    
    # Resumo
    print("📊 RESUMO DA INSTALAÇÃO:")
    print(f"✅ Pacotes instalados com sucesso: {sucessos}")
    print(f"❌ Falhas na instalação: {falhas}")
    
    if falhas == 0:
        print("\n🎉 Todas as dependências foram instaladas com sucesso!")
        print("💡 Agora você pode executar: python mapa_tematico.py")
    else:
        print("\n⚠️ Algumas dependências falharam na instalação.")
        print("💡 Tente instalar manualmente os pacotes que falharam.")
        print("💡 Ou use: pip install --user <nome_do_pacote>")

if __name__ == "__main__":
    main() 