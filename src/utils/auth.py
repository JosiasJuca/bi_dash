"""
Módulo de autenticação e segurança.
"""
import os
import streamlit as st


def get_senha_gerenciamento():
    """
    Obtém a senha para área de gerenciamento.
    Prioridade: senha customizada > variável ambiente > fallback padrão
    
    Returns:
        str: Senha para autenticação
    """
    return st.session_state.get('senha_customizada') or os.environ.get('DASH_SENHA', 'admin123')


def verificar_autenticacao():
    """
    Verifica se o usuário está autenticado na área de gerenciamento.
    
    Returns:
        bool: True se autenticado, False caso contrário
    """
    if 'gerenciamento_autenticado' not in st.session_state:
        st.session_state['gerenciamento_autenticado'] = False
    return st.session_state['gerenciamento_autenticado']


def autenticar_usuario(senha_input):
    """
    Autentica o usuário com a senha fornecida.
    
    Args:
        senha_input (str): Senha fornecida pelo usuário
        
    Returns:
        bool: True se autenticação bem-sucedida, False caso contrário
    """
    senha_correta = get_senha_gerenciamento()
    
    if senha_input == senha_correta:
        st.session_state['gerenciamento_autenticado'] = True
        return True
    return False


def logout():
    """
    Realiza logout do usuário da área de gerenciamento.
    """
    st.session_state['gerenciamento_autenticado'] = False


def obter_tipo_senha():
    """
    Retorna o tipo de senha sendo utilizada (para exibição).
    
    Returns:
        str: Descrição do tipo de senha
    """
    if st.session_state.get('senha_customizada'):
        return "🔒 Usando senha customizada definida via interface"
    elif os.environ.get('DASH_SENHA'):
        return "🔒 Usando variável de ambiente DASH_SENHA"
    else:
        return "🔒 Usando senha padrão (admin123)"


def renderizar_configuracao_senha():
    """
    Renderiza a configuração de senha na sidebar.
    """
    st.markdown("### ⚙️ Configurações do Sistema")
    
    # Verifica se existe variável de ambiente
    senha_env = os.environ.get('DASH_SENHA')
    
    if senha_env:
        st.success("✅ Senha configurada via variável de ambiente")
        st.caption("Usando: DASH_SENHA")
    else:
        st.warning("⚠️ Variável de ambiente DASH_SENHA não encontrada")
        st.caption("Usando senha padrão ou configuração manual")


def renderizar_tela_login():
    """
    Renderiza a tela de login para área de gerenciamento.
    
    Returns:
        bool: True se login foi realizado com sucesso
    """
    st.subheader('🔒 Acesso Restrito - Área de Gerenciamento')
    st.info('Esta área contém funcionalidades administrativas sensíveis.')
    
    col_senha, col_btn = st.columns([2, 1])
    login_realizado = False
    
    with col_senha:
        senha_input = st.text_input(
            'Digite a senha para acessar:', 
            type='password', 
            key='senha_gerenciamento'
        )
    
    with col_btn:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button('🔓 Entrar', use_container_width=True):
            if autenticar_usuario(senha_input):
                st.success('✅ Acesso liberado!')
                login_realizado = True
                st.rerun()
            else:
                st.error('❌ Senha incorreta!')
                
    # Mostra qual método de autenticação está sendo usado
    st.divider()
    st.caption(obter_tipo_senha())
    
    return login_realizado


def renderizar_header_gerenciamento():
    """
    Renderiza o header da área de gerenciamento com botão de logout.
    """
    col_title, col_logout = st.columns([3, 1])
    
    with col_title:
        st.subheader('🛠️ Área de Gerenciamento')
    
    with col_logout:
        if st.button('🚪 Sair', key='logout_gerenciamento'):
            logout()
            st.rerun()
    
    st.info('Você está na área administrativa. Use com cuidado!')