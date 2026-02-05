"""
Componente da aba Regras e Passo a Passo.
"""
import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from typing import Optional, Dict


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


# -------------------------
# Seção: Regras — Parser AFD / AFDT-REP
# -------------------------

def parse_afd_compacto(linha: str) -> Optional[Dict]:
    """Parseia formato compacto AFD (ex.: NSR + tipo + DDMMYYYY + HHMM + PIS)."""
    linha = linha.strip()
    if len(linha) < 34:
        return None
    nsr = linha[0:9]
    tipo = linha[9]
    data = linha[10:18]
    hora = linha[18:22]
    pis = linha[22:34]
    # formata data/hora
    if len(data) == 8:
        # ex: YYYYMMDD ou DDMMYYYY — tentar detectar
        if data.startswith('20') or data.startswith('19'):
            # YYYYMMDD → DD/MM/YYYY
            data_format = f"{data[6:8]}/{data[4:6]}/{data[0:4]}"
        else:
            # DDMMYYYY → DD/MM/YYYY
            data_format = f"{data[0:2]}/{data[2:4]}/{data[4:]}"
    else:
        data_format = data
    hora_format = f"{hora[:2]}:{hora[2:]}" if len(hora) >= 4 else hora
    return {"nsr": nsr, "tipo": tipo, "data": data_format, "hora": hora_format, "pis": pis}


def parse_afdt_iso(linha: str) -> Optional[Dict]:
    """Tenta parsear registros que contenham timestamps ISO (AFDT / REP).
    Usa regex para localizar o primeiro timestamp no formato YYYY-MM-DDTHH:MM:SS.
    """
    linha = linha.strip()
    # procurar padrão ISO
    m = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", linha)
    if not m:
        return None
    try:
        nsr = linha[0:9] if len(linha) >= 9 else ""
        tipo = linha[9] if len(linha) > 9 else ""
        ts = m.group(0)
        dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        data_format = dt.strftime("%d/%m/%Y")
        hora_format = dt.strftime("%H:%M:%S")
        # buscar PIS logo após o timestamp (heurística)
        post = linha[m.end():]
        pis_m = re.search(r"\d{10,12}", post)
        pis = pis_m.group(0) if pis_m else ""
        return {"nsr": nsr, "tipo": tipo, "data": data_format, "hora": hora_format, "pis": pis}
    except Exception:
        return None


def parse_registro(linha: str) -> Dict:
    """Tenta identificar e parsear um registro AFD/AFDT.
    Retorna dicionário com formato detectado e campos.
    """
    linha = linha.strip()
    # Priorizar formato ISO/AFDT
    res = parse_afdt_iso(linha)
    if res:
        return {"formato": "AFDT/ISO", **res}
    res = parse_afd_compacto(linha)
    if res:
        return {"formato": "AFD-compacto", **res}
    return {"formato": "desconhecido", "raw": linha}


def renderizar_regras_parser():
    """Renderiza explicação e exemplos de parser para suporte."""
    st.markdown("### Como ler registros AFD / AFDT-REP")
    st.markdown(
        """
        - **NSR**: Identificador sequencial do registro (normalmente 9 dígitos).
        - **Tipo de Registro**: Código de 1 dígito que representa o tipo da linha.
        - **Data / Hora**: Pode vir em formato compacto (DDMMYYYY + HHMM) ou ISO (`YYYY-MM-DDTHH:MM:SS`).
        - **PIS**: Identificador do colaborador (10-12 dígitos, pode ter zeros à esquerda).
        
        O parser implementa heurísticas para detectar o formato e extrair campos. Se o layout oficial do REP/AFD estiver disponível, prefira usar o fatiamento exato baseado no layout.
        """,
    )

    # Mostrar código de exemplo
    codigo_exemplo = '''def parse_registro(linha: str) -> Dict:
    # detecta formato AFDT/ISO ou AFD compacto e retorna campos essenciais
    ...
'''
    st.code(codigo_exemplo, language="python")

    # Exemplos
    st.markdown("**Exemplo AFD compacto**")
    ex1 = "00033785732901202610360203640807955528"
    st.code(ex1, language="text")
    st.write(parse_registro(ex1))

    st.markdown("**Exemplo AFDT/REP (ISO)**")
    ex2 = "00003575872026-01-13T22:01:00-03000014529820582026-01-13T22:02:00-03000104f518c5ccdb62808a776c244439c46eae39cd1681c7b8cb8ab60940e7350f1fd"
    st.code(ex2[:180] + '...')
    st.write(parse_registro(ex2))


# Integração na página
def renderizar_regras():
    """Renderiza a aba de regras e passo a passo."""
    st.title(" Passo a passo integrações")
    st.markdown("""
    Este painel consolida o **Passo a passo integrações**. Siga os passos para uma melhor análise de divergências.
    """)

    # ==================== FLUXO PRINCIPAL ====================
    renderizar_fluxo_investigacao()
    st.markdown("---")

    # ==================== TABELA DE ARQUIVOS ====================
    renderizar_inteligencia_arquivos()
    st.markdown("---")

    # ==================== CHECKLIST E E-MAIL ====================
    renderizar_checklist_e_email()
    st.markdown("---")

    # ==================== PARSER AFD / AFDT ====================
    renderizar_regras_parser()
    st.markdown("---")

    # ==================== DOCUMENTAÇÃO VISUAL ====================
    renderizar_documentacao_visual()
