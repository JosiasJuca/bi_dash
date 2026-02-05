"""
Componente da área de Gerenciamento protegida.
"""
import streamlit as st


def renderizar_gerenciamento():
    """Renderiza a área de gerenciamento com suas sub-abas."""
    # Botão de download do banco de dados (backup rápido)
    try:
        from src.database.operations import DB_PATH
        with open(DB_PATH, "rb") as _f:
            db_bytes = _f.read()
        st.download_button(
            label=" Baixar banco de dados (integracoes.db)",
            data=db_bytes,
            file_name="integracoes.db",
            mime="application/x-sqlite3",
        )
    except FileNotFoundError:
        st.warning("Banco de dados não encontrado para download.")

    # Sub-abas dentro do Gerenciamento
    tab_checklist, tab_chamados, tab_historico = st.tabs([
        " Checklist",
        " Chamados Ativos", 
        " Histórico"
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