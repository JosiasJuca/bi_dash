"""
Componentes para renderização de tabelas.
"""
import streamlit as st
from datetime import datetime
from src.utils.helpers import (
    status_badge, 
    calcular_previsao_resolucao, 
    obter_estilos_etapa,
    pick_icon_checklist
)


def renderizar_tabela_chamados_problemas(chamados_filtrados):
    """
    Renderiza tabela de chamados com problemas.
    
    Args:
        chamados_filtrados (list): Lista de chamados filtrados
    """
    if not chamados_filtrados:
        st.info("Nenhum cliente com problemas")
        return
    
    # Constrói a tabela HTML
    table_html = criar_cabecalho_tabela_problemas()
    
    for chamado in chamados_filtrados:
        # Formatar data de abertura
        data_formatada = formatar_data_tabela(chamado["data_abertura"])
        previsao = calcular_previsao_resolucao(
            chamado["data_abertura"], 
            chamado.get("observacao", "")
        )
        
        # Estilo para a etapa
        etapa = chamado.get('etapa', 'Não iniciado')
        etapa_bg = obter_estilos_etapa(etapa)
        
        table_html += f'''
        <tr style="border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 10px; color: #111;">{chamado["cliente"]}</td>
            <td style="padding: 10px; text-align: center;">{status_badge(chamado["status"])}</td>
            <td style="padding: 10px; color: #111;">{chamado["categoria"]}</td>
            <td style="padding: 10px; text-align: center; color: #666;">{data_formatada}</td>
            <td style="padding: 10px; text-align: center; color: #666; font-weight: bold;">{previsao}</td>
            <td style="padding: 10px; text-align: center; background-color: {etapa_bg}; color: #333; font-weight: 500; border-radius: 4px;">{etapa}</td>
            <td style="padding: 10px; color: #333; font-size: 13px;">{chamado.get("observacao", "") or "-"}</td>
        </tr>'''
    
    table_html += '</tbody></table></div>'
    st.markdown(table_html, unsafe_allow_html=True)


def renderizar_tabela_checklist(clientes_checklist):
    """
    Renderiza tabela de checklist de integração.
    
    Args:
        clientes_checklist (dict): Dicionário com dados do checklist
    """
    if not clientes_checklist:
        st.info("Nenhum cliente sem integração")
        return
    
    # Constrói a tabela HTML
    table_html = criar_cabecalho_tabela_checklist()
    
    for cliente, dados in clientes_checklist.items():
        # Obtém ícones para cada categoria
        categorias_icons = obter_icons_checklist(dados)
        
        table_html += f'''
        <tr style="border-bottom: 1px solid #e0e0e0;">
            <td style="padding: 10px; color: #111;">{cliente}</td>
            <td style="padding: 10px; text-align: center;">{status_badge(dados["status"])}</td>'''
        
        # Adiciona ícones das categorias
        for icon, color in categorias_icons:
            table_html += f'<td style="padding: 10px; text-align: center; color: {color}; font-size: 20px;">{icon}</td>'
        
        table_html += '</tr>'
    
    table_html += '</tbody></table></div>'
    st.markdown(table_html, unsafe_allow_html=True)


def criar_cabecalho_tabela_problemas():
    """
    Cria o cabeçalho HTML para tabela de problemas.
    
    Returns:
        str: HTML do cabeçalho da tabela
    """
    return '''
    <div style="background: #f5f5f5; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0;">
    <table style="width: 100%; border-collapse: collapse;">
    <thead><tr style="border-bottom: 2px solid #444;">
    <th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CLIENTE</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">STATUS</th>
    <th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CATEGORIA</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">DATA ABERTURA</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">PREVISÃO RESOLUÇÃO</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">ETAPA</th>
    <th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">OBSERVAÇÃO</th>
    </tr></thead><tbody>'''


def criar_cabecalho_tabela_checklist():
    """
    Cria o cabeçalho HTML para tabela de checklist.
    
    Returns:
        str: HTML do cabeçalho da tabela
    """
    return '''
    <div style="background: #f5f5f5; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0;">
    <table style="width: 100%; border-collapse: collapse;">
    <thead><tr style="border-bottom: 2px solid #444;">
    <th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CLIENTE</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">STATUS_IMPLANTAÇÃO</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">BATIDA</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">ESCALA</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">FERIADOS</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">FUNCIONÁRIOS</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">PDV</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">VENDA</th>
    <th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">SSO</th>
    </tr></thead><tbody>'''


def obter_icons_checklist(dados):
    """
    Obtém ícones e cores para cada categoria do checklist.
    
    Args:
        dados (dict): Dados do cliente com informações das categorias
        
    Returns:
        list: Lista de tuplas (ícone, cor) para cada categoria
    """
    categorias = ['batida', 'escala', 'feriados', 'funcionarios', 'pdv', 'venda', 'sso']
    icons = []
    
    for categoria in categorias:
        has_chamado = dados.get(categoria, False)
        construcao = dados.get(f'{categoria}_construcao', False)
        na = dados.get(f'{categoria}_na', False)
        
        icon, color = pick_icon_checklist(has_chamado, construcao, na)
        icons.append((icon, color))
    
    return icons


def formatar_data_tabela(data_str):
    """
    Formata data para exibição na tabela.
    
    Args:
        data_str (str): Data no formato YYYY-MM-DD
        
    Returns:
        str: Data formatada para exibição
    """
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return data_str


def renderizar_tabela_historico(historico):
    """
    Renderiza tabela do histórico de chamados resolvidos.
    
    Args:
        historico (list): Lista de chamados resolvidos
    """
    if not historico:
        st.info("Nenhum chamado resolvido ainda.")
        return
    
    st.markdown(f"**{len(historico)} chamados resolvidos**")
    
    for chamado in historico:
        col_tab, col_btn1, col_btn2 = st.columns([4, 1, 1])
        
        with col_tab:
            st.markdown(f"**{chamado['cliente']}** • {chamado['categoria']}")
            if chamado['observacao']:
                st.caption(chamado['observacao'])
            if chamado.get('resolucao'):
                st.markdown(
                    f"<span style='color:#2E6FB2'><b>Resolução:</b> {chamado['resolucao']}</span>", 
                    unsafe_allow_html=True
                )
            st.caption(f"Aberto: {chamado['data_abertura']} → Resolvido: {chamado['data_resolucao']}")
        
        with col_btn1:
            if st.button("🔁", key=f"reabrir_{chamado['chamado_id']}", help="Reabrir chamado"):
                from src.database.operations import reabrir_chamado
                reabrir_chamado(chamado['chamado_id'])
                st.success("Chamado reaberto!")
                st.rerun()
        
        with col_btn2:
            if st.button("🗑️", key=f"excluir_hist_{chamado['chamado_id']}", help="Excluir chamado", type="secondary"):
                from src.database.operations import excluir_chamado
                if excluir_chamado(chamado['chamado_id']):
                    st.success("Excluído!")
                    st.rerun()
        
        st.divider()