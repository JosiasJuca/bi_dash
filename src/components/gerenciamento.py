"""
Componente da área de Gerenciamento protegida.
"""
import streamlit as st


def renderizar_gerenciamento():
    """Renderiza a área de gerenciamento com suas sub-abas."""
    
    # Sub-abas dentro do Gerenciamento
    tab_checklist, tab_chamados, tab_historico = st.tabs([
        "📋 Checklist",
        "🎫 Chamados Ativos", 
        "📚 Histórico"
    ])

    with tab_checklist:
        from src.components.checklist import renderizar_checklist
        renderizar_checklist()

    with tab_chamados:
        from src.components.chamados import renderizar_chamados
        renderizar_chamados()

    with tab_historico:
        from src.components.historico import renderizar_historico
        renderizar_historico()