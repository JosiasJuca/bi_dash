"""
Componente da aba Regras e Passo a Passo.
"""
import streamlit as st
import pandas as pd
import os


def renderizar_regras():
    """Renderiza a aba de regras e passo a passo."""
    
    st.title(" Passo a passo integrações")
    
    st.markdown("""
    Este painel consolida o **Passo a passo integrações**. Siga os passos para uma melhor análise de divergências.""")

    # ==================== FLUXO PRINCIPAL ====================
    renderizar_fluxo_investigacao()
    
    st.markdown("---")

    # ==================== TABELA DE ARQUIVOS ====================
    renderizar_inteligencia_arquivos()

    # ==================== CHECKLIST E E-MAIL ====================
    renderizar_checklist_e_email()

    # ==================== DOCUMENTAÇÃO VISUAL ====================
    st.markdown("---")
    renderizar_documentacao_visual()


def renderizar_fluxo_investigacao():
    """Renderiza o fluxo principal de investigação."""
    st.markdown("###  Fluxo de Investigação")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.info("**1. Site do Cliente**")
        st.caption("Validar se a divergência existe na ponta.")
    
    with c2:
        st.success("**2. Servidor SFTP**")
        st.caption("Verificar se o dado bruto foi enviado ao FileZilla.")
    
    with c3:
        st.warning("**3. Conformidade**")
        st.caption("Comparar conteúdo do arquivo vs. registro esperado.")


def renderizar_inteligencia_arquivos():
    """Renderiza a tabela de inteligência de arquivos."""
    st.markdown("###  Inteligência de Arquivos")
    
    df_metodos = pd.DataFrame({
        "Formato": ["AFD / Variações", "AFDT", "Tipo Moavi"],
        "Ação de Investigação": [
            "Usar comandos de busca de texto ou Data Studio.",
            "Filtrar por padrões de Timestamp e ID de cliente.",
            "Análise via delimitador (CSV, ; ou |)."
        ]
    })
    
    st.table(df_metodos)


def renderizar_checklist_e_email():
    """Renderiza seções de checklist e modelo de e-mail."""
    col_check, col_email = st.columns([1, 1])

    with col_check:
        renderizar_checklist_auditoria()

    with col_email:
        renderizar_modelo_email()


def renderizar_checklist_auditoria():
    """Renderiza checklist de auditoria interativo."""
    with st.expander(" Checklist de Auditoria", expanded=True):
        st.checkbox("Absenteísmo confirmado no Site", key="reg_1")
        st.checkbox("Arquivos presentes no FileZilla", key="reg_2")
        st.checkbox("Registro de ponto encontrado no arquivo", key="reg_3")
        st.checkbox("Dados íntegros no Banco de Dados", key="reg_4")


def renderizar_modelo_email():
    """Renderiza modelo de e-mail para notificação."""
    with st.expander(" Modelo de Notificação", expanded=False):
        st.markdown("Copie o texto abaixo caso as batidas não constem no arquivo:")
        
        template_email = """
Assunto: Inconsistência no envio de batidas - [Cliente]

Prezado responsável,

Identificamos que nos últimos [N] dias, os arquivos 
enviados via integração não contém as marcações 
de ponto dos colaboradores.

Poderia verificar o envio na origem?

Atenciosamente,
Equipe de Integrações
        """
        
        st.code(template_email.strip(), language="text")
        
        # Botão para copiar template
        if st.button("📋 Copiar Template", key="copy_template"):
            st.success("Template copiado! (Cole com Ctrl+V)")


def renderizar_documentacao_visual():
    """Renderiza documentação visual com imagens."""
    st.subheader(" Documentação Visual")
    
    img_dir = os.path.join(os.path.dirname(__file__), "..", "..", "img")
    
    images = [
        ("Diretório FileZilla", "CaminhoPASTA.png", 220),
        ("Estrutura Moavi (CSV)", "ExpBATIDAS2.png", 520),
        ("Estrutura AFD (TXT)", "ExpBATIDAS_AFD.png", 440)
    ]

    cols = st.columns([1, 2, 2])

    for i, (label, filename, width) in enumerate(images):
        full_path = os.path.join(img_dir, filename)
        
        with cols[i]:
            st.markdown(f"**{label}**")
            
            if os.path.exists(full_path):
                st.image(full_path, width=width, use_container_width=False)
            else:
                st.warning(f"Imagem ausente: {filename}")
                renderizar_placeholder_imagem(label)


def renderizar_placeholder_imagem(label):
    """
    Renderiza um placeholder quando a imagem não está disponível.
    
    Args:
        label (str): Rótulo da imagem
    """
    st.markdown(f"""
    <div style="
        border: 2px dashed #ccc; 
        padding: 20px; 
        text-align: center; 
        border-radius: 8px;
        background-color: #f9f9f9;
        color: #666;
        margin: 10px 0;
    ">
        📷 {label}<br>
        <small>Imagem não encontrada</small>
    </div>
    """, unsafe_allow_html=True)