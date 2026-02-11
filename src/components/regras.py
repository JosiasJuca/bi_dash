"""
Componente da aba Regras e Passo a Passo.
"""
import streamlit as st
import os
import re
from datetime import datetime
from typing import Optional, Dict





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
    # Observações: tabela de passos removida conforme solicitado


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
        st.checkbox("Registro de ponto não encontrado no arquivo", key="reg_3")
    


def renderizar_modelo_email():
    """Renderiza modelo de e-mail para notificação."""
    with st.expander(" Modelo de Notificação", expanded=False):
        st.markdown("")
        
        template_email = """
    Assunto: Moavi | [<Cliente>] | Batidas de ponto

    Boa tarde!
    Tudo bem?

    Ao conferir o acompanhamento de batidas, identifiquei que algumas filiais ficaram sem registro de batidas.
 
    Vocês conseguem confirmar se houve algum problema operacional?
 
    Caso não tenha ocorrido problema, poderia, por gentileza, me enviar o retroativo das batidas?

    Atenciosamente,
        """

        # Exibe o template como bloco de código para habilitar o botão 'copiar'
        st.code(template_email.strip(), language="text")
        
        


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


def renderizar_inteligencia_arquivos():
    # Função de listagem de arquivos removida — não é mais necessária
    return

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
         {label}<br>
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
    # procurar padrão ISO (presença indica AFDT/REP) — em seguida usamos fatiamento fixo do primeiro registro
    m = re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", linha)
    if not m:
        return None

    nsr = linha[0:9] if len(linha) >= 9 else ""
    tipo = linha[9] if len(linha) > 9 else ""
    try:
        # fatiamento conforme layout fornecido
        data_raw = linha[10:20]  # AAAA-MM-DD
        hora_raw = linha[21:26]  # HH:MM
        pis = linha[35:46] if len(linha) >= 46 else ""
        data_formatada = data_raw.replace('-', '/')
        hora_formatada = hora_raw
        return {"nsr": nsr, "tipo": tipo, "data": data_formatada, "hora": hora_formatada, "pis": pis}
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

        Para registros AFDT/REP este painel utiliza o fatiamento do primeiro registro com o layout padrão (quando presente):
        - `nsr = linha[0:9]`
        - `tipo = linha[9]`
        - `data_raw = linha[10:20]`  # AAAA-MM-DD
        - `hora_raw = linha[21:26]`  # HH:MM
        - `pis = linha[35:46]`
        """,
    )

    # Exemplos
    st.markdown("**Exemplo AFD compacto**")
    ex1 = "00033785732901202610360203640807955528"
    st.code(ex1, language="text")
    st.write(parse_registro(ex1))

    st.markdown("**Exemplo AFDT/REP (ISO)**")
    ex2 = "00003575872026-01-13T22:01:00-03000014529820582026-01-13T22:02:00-03000104f518c5ccdb62808a776c244439c46eae39cd1681c7b8cb8ab60940e7350f1fd"
    st.code(ex2[:180] + '...')
    # Mostrar parse do exemplo AFDT/REP (primeiro registro)
    st.write(parse_registro(ex2))

    # Campo para colagem (paste) da linha e botão de validação
    st.markdown("**Validar linha (cole o conteúdo AFD/AFDT aqui)**")
    linha_input = st.text_area("Cole a linha AFD/AFDT", value="", height=120, key="regras_paste")
    validar = st.button(" Validar linha", key="regras_validar")

    if validar:
        if not linha_input or not linha_input.strip():
            st.warning("Cole uma linha válida para análise.")
        else:
            # Sempre mostrar apenas o primeiro registro detectado (fatiamento AFDT/REP ou AFD compacto)
            st.subheader("Resultado (primeiro registro detectado)")
            st.json(parse_registro(linha_input))


def renderizar_conteudo_batidas():
    """Renderiza o conteúdo principal da aba Batidas."""
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


def renderizar_regras():
    """Renderiza a aba de regras e passo a passo com subtabs."""
    st.title(" Regras e Fluxo")
    st.markdown("Visualize o fluxo ou escolha uma aba para ver conteúdos específicos.")

    tab_fluxo, tab_batidas, tab_colaboradores, tab_vendas = st.tabs([
        "Fluxo",
        "Batidas",
        "Colaboradores",
        "Vendas",
    ])

    with tab_fluxo:
        img_dir = os.path.join(os.path.dirname(__file__), "..", "..", "img")
        fluxo_path = os.path.join(img_dir, "fluxo.png")
        if os.path.exists(fluxo_path):
            st.image(fluxo_path, caption="Fluxo de investigação", use_container_width=True)
        else:
            renderizar_placeholder_imagem("Fluxo de investigação")

    with tab_batidas:
        renderizar_conteudo_batidas()

    with tab_colaboradores:
        st.markdown("""
# Fluxo de Atendimento: Colaboradores

Este guia orienta o processo de investigação e resolução de problemas relacionados aos dados de colaboradores e batidas de ponto na plataforma.

## 1. Integrações Essenciais (Dados de Novos Colaboradores)

Antes de iniciar a análise de erros, entenda como os dados são recebidos:

* **Formato:** Os arquivos são recebidos exclusivamente em formato **CSV**.
* **Localização:** Os arquivos são depositados em nossa pasta de **"Importados"**.
* **Identificação (Campos Chave):** A integração pode utilizar o **PIS**, **CPF** ou **Matrícula** como identificador principal.
* **Método de Análise:** 1. Baixar o arquivo da pasta de importados.
2. Abrir e separar os dados por **delimitador** (ex: vírgula ou ponto e vírgula).
3. Buscar as informações do colaborador para validar o envio.

---

## 2. Fluxo de Investigação de Divergências

Siga os passos abaixo quando houver ausência de marcações ou erro de cadastro.

### **Cenário: Batida do colaborador não aparece**

1. **Baixar arquivo de colaboradores:** Analise o CSV na pasta de importados.
2. **Avaliar cadastro na Moavi:** Verifique se o registro foi processado corretamente.

| Cenário | Causa Identificada | Ação Necessária |
| --- | --- | --- |
| **Não encontra o colaborador** | Não está cadastrada | Ensinar o usuário a adicionar na escala. |
| **Colaborador cadastrado** | Colocou colaborador errado | Explicar que a escala está com a pessoa errada. |
| **Dados divergentes** | Dado diferente do real | Seguir para análise de PIS/Integração. |

---

## 3. Diagnóstico de Integração (PIS e Dados)

> [!IMPORTANT]
> **Ação Padrão:** Para qualquer erro de PIS ou ausência de dados na integração, o contato deve ser feito com o **RH** do cliente.

* **PIS Diferente:** O PIS no sistema de integração não coincide com o informado pela pessoa.
* *Ação:* Pedir ao usuário para solicitar a atualização do PIS no RH (sistema de ponto).

* **PIS Zerado:** O campo de PIS está vindo vazio ou zerado no CSV.
* *Ação:* Solicitar ao RH a correção do cadastro no sistema de origem.

* **Sem PIS / Dados Ausentes:** Não estamos recebendo os dados da pessoa no arquivo.
* *Ação:* Solicitar ao RH que inclua/envie o colaborador na próxima integração.

---

## 4. Dúvidas Frequentes (FAQ)

**Podemos corrigir uma integração manualmente?**

* **Não.** Nunca alteramos dados vindos de integração para evitar desalinhamento entre os sistemas.

**Podemos corrigir dados do colaborador diretamente?**

* **Somente** em casos onde **não existe** integração ativa. Se houver integração, a origem deve ser corrigida.

**Para quem devo encaminhar casos críticos?**

* Siga o fluxo da coluna **"Contato"** na página de **Integrações**. Caso não haja, acione: **Ju, Madruga ou Edu**.

---

""")

    with tab_vendas:
        st.markdown("""
# Fluxo de Atendimento: Vendas

Este guia orienta a validação e análise técnica dos dados de vendas integrados na plataforma.

## 1. Integrações Essenciais (Vendas)

Para que a análise de performance seja precisa, os dados de vendas devem seguir estes critérios obrigatórios:

* **Granularidade:** A curva de vendas precisa ser enviada **hora a hora** e **dia a dia**.
* **Métricas Necessárias:**
* Faturamento (**R$**);
* Quantidade de **cupons** emitidos;
* Quantidade de **itens** vendidos.


* **Histórico Inicial:** Sempre garantir o envio do **último mês completo** para base de comparação.

---

## 2. Quebra por Setores (Departamentalização)

Os dados devem ser segmentados conforme o ramo do cliente. **Atenção à regra do Setor Total.**

### **Segmentos Comuns**

* **Farmácia:** Total, Balcão e Dermocosméticos.
* **Supermercado:** Total, Padaria, FLV (Frutas, Legumes e Verduras), Frios, Açougue, Adega, etc.

> [!CAUTION]
> **REGRA DE OURO:** O cliente deve enviar o setor **TOTAL** separadamente no arquivo.
> **Nunca somar a quantidade de cupons dos setores** para tentar chegar ao total, pois um único cupom pode conter itens de vários setores diferentes (gerando duplicidade na contagem).

---

## 3. Análise Visual do Arquivo

Utilize o espaço abaixo para anexar ou visualizar o layout padrão do arquivo de vendas que o sistema processa.

### **Exemplo de um Arquivo de Vendas**
""")

        # Exibe imagem de vendas se disponível
        img_dir = os.path.join(os.path.dirname(__file__), "..", "..", "img")
        vendas_path = os.path.join(img_dir, "vendas.png")
        if os.path.exists(vendas_path):
            st.image(vendas_path, caption="Layout de vendas (exemplo)", width=900)
        else:
            renderizar_placeholder_imagem("Layout de vendas")

        st.markdown("""
---

## 4. Checklist de Validação de Vendas

Ao analisar o arquivo recebido, verifique:

* [ ] O delimitador do CSV está correto?
* [ ] O faturamento (R$) está usando o formato decimal adequado?
* [ ] Existem registros para todas as horas do dia em que a loja esteve aberta?
* [ ] O campo "Setor" identifica claramente o que é o "Total"?
* [ ] O número de cupons do setor Total é coerente com o movimento da loja?

---

## 5. Dúvidas Frequentes | Vendas

**A soma dos setores não bate com o Total, o que fazer?**

* Isso é normal para **Cupons**, mas o faturamento (R$) e itens devem bater. Se o faturamento não bater, peça ao RH/TI do cliente para revisar a exportação.

**O arquivo veio sem a quebra de hora em hora, podemos subir?**

* Não. Sem a quebra horária, o sistema não consegue gerar a curva de produtividade e a escala ficará comprometida.
""")
