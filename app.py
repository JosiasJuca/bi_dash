"""
BI de Integrações - Versão 2.0 Profissional
Sistema de gestão de integrações com SQLite
Arquitetura modular e profissional
"""
import streamlit as st
import sys
import os

# Adiciona o diretório src ao path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Imports de módulos locais
from src.utils.constants import APP_CONFIG, CSS_STYLES
from src.utils.helpers import exibir_mensagens_persistentes
from src.utils.auth import (
    verificar_autenticacao, 
    renderizar_configuracao_senha,
    renderizar_tela_login,
    renderizar_header_gerenciamento
)
from src.database.operations import init_db
from src.components.dashboard import renderizar_dashboard
from src.components.regras import renderizar_regras  
from src.components.gerenciamento import renderizar_gerenciamento


def configurar_pagina():
    """Configura as configurações básicas da página Streamlit."""
    st.set_page_config(**APP_CONFIG)
    st.markdown(CSS_STYLES, unsafe_allow_html=True)


def renderizar_sidebar():
    """Renderiza a sidebar com configurações do sistema."""
    with st.sidebar:
        renderizar_configuracao_senha()


def main():
    """Função principal da aplicação."""
    # Configurações iniciais
    configurar_pagina()
    init_db()
    
    # Mensagens persistentes
    exibir_mensagens_persistentes()
    
    # Sidebar
    renderizar_sidebar()
    
    # Título principal
    st.title(" BI de Integrações")
    
    # Abas principais
    tab_dashboard, tab_regras, tab_gerenciamento = st.tabs([
        "📊 Dashboard",
        "📖 Regras", 
        "🔒 Gerenciamento"
    ])
    
    # ==================== ABA DASHBOARD ====================
    with tab_dashboard:
        renderizar_dashboard()
    
    # ==================== ABA REGRAS ====================
    with tab_regras:
        renderizar_regras()
    
    # ==================== ABA GERENCIAMENTO ====================
    with tab_gerenciamento:
        if not verificar_autenticacao():
            renderizar_tela_login()
        else:
            renderizar_header_gerenciamento()
            renderizar_gerenciamento()
    
    # ==================== RODAPÉ ====================
    st.divider()
    st.caption('BI de Integrações v1 - Sistema profissional de gestão de integrações')


if __name__ == "__main__":
    main()