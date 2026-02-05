"""
Funções auxiliares e utilitários gerais.
"""
import re
import streamlit as st
from datetime import datetime, timedelta
from src.utils.constants import CORES_STATUS


def status_badge(status):
    """
    Retorna um badge HTML colorido para o status.
    
    Args:
        status (str): Status do cliente/chamado
        
    Returns:
        str: HTML do badge colorido
    """
    cor = CORES_STATUS.get(status, "#6b7280")
    return f'<span class="status-badge" style="background-color: {cor};">{status}</span>'


def exibir_mensagens_persistentes():
    """
    Exibe mensagens que foram salvas no session_state após rerun.
    """
    if 'saved_messages' in st.session_state and st.session_state.get('saved_messages'):
        for _msg in st.session_state.get('saved_messages', []):
            st.success(_msg)
        # limpa mensagens exibidas
        st.session_state['saved_messages'] = []


def adicionar_mensagem_sucesso(mensagem):
    """
    Adiciona uma mensagem de sucesso para ser exibida após rerun.
    
    Args:
        mensagem (str): Mensagem a ser exibida
    """
    st.session_state.setdefault('saved_messages', []).append(mensagem)


def formatar_data_brasileira(data_str):
    """
    Formata data de YYYY-MM-DD para DD/MM/YYYY.
    
    Args:
        data_str (str): Data no formato YYYY-MM-DD
        
    Returns:
        str: Data no formato DD/MM/YYYY
    """
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_str


def calcular_previsao_resolucao(data_abertura_str, observacao=""):
    """
    Calcula a previsão de resolução de um chamado.
    
    Args:
        data_abertura_str (str): Data de abertura no formato YYYY-MM-DD
        observacao (str): Observação que pode conter previsão manual
        
    Returns:
        str: Data de previsão no formato DD/MM/YYYY
    """
    # Primeiro tenta extrair da observação se existe "Previsão: DD/MM/AAAA"
    if observacao:
        match = re.search(r'Previsão:\s*(\d{2}/\d{2}/\d{4})', observacao)
        if match:
            return match.group(1)
    
    # Se não encontrar na observação, calcula 7 dias a partir da abertura
    try:
        data_abertura = datetime.strptime(data_abertura_str, '%Y-%m-%d')
        # Adiciona 7 dias (assumindo 5 dias úteis + fim de semana)
        previsao = data_abertura + timedelta(days=7)
        return previsao.strftime('%d/%m/%Y')
    except:
        return "A definir"


def pick_icon_checklist(has_chamado, construcao, na):
    """
    Escolhe ícone e cor baseado nos estados do checklist.
    
    Args:
        has_chamado (bool): Se existe chamado ativo
        construcao (bool): Se está em construção
        na (bool): Se não se aplica
        
    Returns:
        tuple: (ícone, cor)
    """
    # Ordem de prioridade:
    # 1) N/A -> mostrar 'N/A'
    # 2) Em construção -> mostrar 🛠️
    # 3) Existe chamado (qualquer) -> mostrar ✗ (problema pendente)
    # 4) Sem chamado -> mostrar ✓ (ok)
    if na:
        return ('N/A', '#8FA9BF')
    if construcao:
        return ('🛠️', '#2E6FB2')
    if has_chamado:
        return ('✗', "#E91616")
    return ('✓', "#045F2D")


def obter_estilos_etapa(etapa):
    """
    Obtém estilos CSS para diferentes etapas de chamados.
    
    Args:
        etapa (str): Nome da etapa
        
    Returns:
        str: Código CSS da cor de fundo
    """
    etapa_styles = {
        "Não iniciado": "#f8f9fa",
        "Aguardando Cliente": "#fff3cd", 
        "Aguardando Moavi": "#d1ecf1"
    }
    return etapa_styles.get(etapa, "#f8f9fa")


def validar_entrada_obrigatoria(valor, nome_campo):
    """
    Valida se um campo obrigatório foi preenchido.
    
    Args:
        valor: Valor a ser validado
        nome_campo (str): Nome do campo para mensagem de erro
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not valor or (isinstance(valor, str) and not valor.strip()):
        st.error(f"⚠️ {nome_campo} é obrigatório!")
        return False
    return True


def confirmar_acao_destrutiva(mensagem, chave_confirmacao):
    """
    Cria um checkbox de confirmação para ações destrutivas.
    
    Args:
        mensagem (str): Mensagem de confirmação
        chave_confirmacao (str): Chave única para o checkbox
        
    Returns:
        bool: True se confirmado, False caso contrário
    """
    return st.checkbox(
        mensagem,
        key=chave_confirmacao,
        help="Marque esta opção para confirmar que deseja prosseguir"
    )