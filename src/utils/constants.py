"""
Constantes utilizadas em todo o projeto BI Dashboard.
"""

# Status de implantação dos clientes
STATUS_OPTIONS = [
    "1. Implantado com problema",
    "2. Implantado refazendo", 
    "3. Novo cliente sem integração",
    "4. Implantado sem integração",
    "5. Integração Parcial",
    "6. Status Normal",
]

# Categorias de integração disponíveis
CATEGORIAS = [
    "Batida", 
    "Escala", 
    "Feriados", 
    "Funcionários", 
    "PDV", 
    "Venda", 
    "SSO", 
    "Geral"
]

# Etapas do ciclo de vida de um chamado
ETAPAS_CHAMADO = [
    "Não iniciado",
    "Aguardando Cliente", 
    "Aguardando Moavi",
    "Em andamento",
    "Aguardando teste",
    "Pronto para finalizar"
]

# Mapeamento de cores para cada status
CORES_STATUS = {
    "1. Implantado com problema": "#143D6B",
    "2. Implantado refazendo": "#2E6FB2", 
    "3. Novo cliente sem integração": "#3FA7DF",
    "5. Implantado sem integração": "#78C6F0",
    "6. Status Normal": "#78C6F0",
    "8. Integração em construção": "#9CA3AF",
}

# Labels amigáveis para exibição na legenda
STATUS_LABELS = {
    "1. Implantado com problema": "Com problema",
    "2. Implantado refazendo": "Refazendo integração",
    "3. Novo cliente sem integração": "Sem integração", 
    "5. Implantado sem integração": "Sem integração",
    "7. Status Normal": "Normal",
    "8. Integração em construção": "Em construção"
}

# Responsáveis padrão do sistema
RESPONSAVEIS = ["Guilherme", "Eduardo", "Marcelo"]

# Configurações da aplicação
APP_CONFIG = {
    "page_title": "BI Integrações",
    "page_icon": "📊", 
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Configurações de estilo CSS
CSS_STYLES = """
<style>
    /* Global font sizing */
    html, body, .block-container, .streamlit-expanderHeader, .css-1dq8tca {
        font-size: 18px !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        color: white;
    } 

    span.st-c1, span.st-c2, p.st-bd{
        background-color: rgb(0, 84, 163) !important;
    }   

    .p {
        color: rgb(0, 84, 163);
    }           

    /* Increase table and caption sizes */
    table, th, td { font-size: 15px !important; }
    .stCaption { font-size: 13px !important; }

    /* Forçar abas em azul e remover underline/borda indesejada */
    [role="tablist"] {
        border-bottom: none !important;
    }

    /* Seleciona botões de abas */
    [role="tablist"] button[role="tab"] {
        color: #006ED2 !important;
        background: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 12px !important;
        box-shadow: none !important;
        outline: none !important;
        background-image: none !important;
    }
    /* Aba ativa */
    [role="tablist"] button[role="tab"][aria-selected="true"] {
        background-color: #006ED2 !important;
        color: white !important;
        box-shadow: none !important;
        border-bottom: none !important;
    }
    /* Hover */
    [role="presentation"] .st-c1 {
        background-color: rgba(0,110,210,0.08) !important;
        box-shadow: none !important;
    }

    /* Tab highlight (BaseWeb/Streamlit) - força azul */
    div[data-baseweb="tab-highlight"],
    [data-baseweb="tab-highlight"] {
        background-color: #006ED2 !important;
        background-image: none !important;
        border: none !important;
        box-shadow: none !important;
        height: 4px !important;
        opacity: 1 !important;
    }

    /* Garantia caso destaque seja aplicado por pseudo-elementos */
    [data-baseweb="tab-highlight"]::before,
    [data-baseweb="tab-highlight"]::after,
    div[data-baseweb="tab-highlight"]::before,
    div[data-baseweb="tab-highlight"]::after {
        background-color: #006ED2 !important;
        display: block !important;
        content: "" !important;
        box-shadow: none !important;
        border: none !important;
    }

</style>
"""