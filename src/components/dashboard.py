"""
Componente da aba Dashboard.
"""
import streamlit as st
from src.database.operations import obter_estatisticas, get_db
from src.components.charts import (
    renderizar_metricas_kpi,
    renderizar_grafico_status, 
    renderizar_grafico_categorias,
    renderizar_grafico_clientes,
    renderizar_filtros_dashboard
)
from src.components.tables import (
    renderizar_tabela_chamados_problemas,
    renderizar_tabela_checklist
)
from src.utils.constants import STATUS_OPTIONS


def renderizar_dashboard():
    """Renderiza o dashboard principal com KPIs, gráficos e tabelas."""
    
    # ==================== KPIs ====================
    stats = obter_estatisticas()
    renderizar_metricas_kpi(stats)
    
    st.divider()
    
    # ==================== GRÁFICOS ====================
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        renderizar_grafico_status(stats)
    
    with col_g2:
        renderizar_grafico_categorias(stats)
    
    st.divider()
    
    # ==================== FILTROS ====================
    status_filtro, busca_cliente, class_filtro, todos_chamados = renderizar_filtros_dashboard()
    
    st.divider()
    
    # ==================== TABELAS DE STATUS ====================
    renderizar_secao_chamados_problemas(status_filtro, busca_cliente, class_filtro, todos_chamados)
    
    st.divider()
    
    renderizar_secao_checklist(status_filtro, busca_cliente, class_filtro, todos_chamados)
    
    st.divider()
    
    # ==================== GRÁFICO POR CLIENTE ====================
    dados_cliente = obter_dados_chamados_por_cliente()
    renderizar_grafico_clientes(dados_cliente)


def renderizar_secao_chamados_problemas(status_filtro, busca_cliente, class_filtro, todos_chamados):
    """
    Renderiza seção de chamados com problemas.
    
    Args:
        status_filtro: Filtro de status selecionado
        busca_cliente: Texto de busca por cliente
        class_filtro: Filtro de classificação
        todos_chamados: Lista de todos os chamados
    """
    st.subheader("Chamados")
    
    # Busca chamados com problemas (status 1 e 2)
    chamados_problema = [
        c for c in todos_chamados 
        if c['status'] in ['1. Implantado com problema', '2. Implantado refazendo']
    ]
    
    # Aplica filtros
    chamados_filtrados = filtrar_chamados(
        chamados_problema, status_filtro, busca_cliente, class_filtro
    )
    
    renderizar_tabela_chamados_problemas(chamados_filtrados)


def renderizar_secao_checklist(status_filtro, busca_cliente, class_filtro, todos_chamados):
    """
    Renderiza seção de checklist de integração.
    
    Args:
        status_filtro: Filtro de status selecionado
        busca_cliente: Texto de busca por cliente  
        class_filtro: Filtro de classificação
        todos_chamados: Lista de todos os chamados
    """
    from src.database.operations import listar_chamados_abertos_completos
    
    st.subheader("Checklist de Integração")
    
    # Busca clientes sem integração
    chamados_sem_int = [
        c for c in todos_chamados
        if ('sem integração' in (c.get('status') or '').lower()) or 
           ('parcial' in (c.get('status') or '').lower()) or 
           ('constru' in (c.get('status') or '').lower())
    ]
    
    # Constrói dados do checklist
    clientes_checklist = construir_dados_checklist(chamados_sem_int, status_filtro, busca_cliente, class_filtro)
    
    renderizar_tabela_checklist(clientes_checklist)


def filtrar_chamados(chamados, status_filtro, busca_cliente, class_filtro):
    """
    Aplica filtros aos chamados.
    
    Args:
        chamados: Lista de chamados
        status_filtro: Filtro de status
        busca_cliente: Filtro de busca de cliente
        class_filtro: Filtro de classificação
        
    Returns:
        list: Chamados filtrados
    """
    return [
        c for c in chamados 
        if c['status'] in status_filtro and (
            not busca_cliente or busca_cliente.lower() in c['cliente'].lower()
        ) and (not class_filtro or c.get('classificacao','Guilherme') in class_filtro)
    ]


def construir_dados_checklist(chamados_sem_int, status_filtro, busca_cliente, class_filtro):
    """
    Constrói os dados do checklist de integração.
    
    Args:
        chamados_sem_int: Chamados sem integração
        status_filtro: Filtro de status
        busca_cliente: Filtro de busca de cliente
        class_filtro: Filtro de classificação
        
    Returns:
        dict: Dados do checklist organizados por cliente
    """
    from src.database.operations import listar_chamados_abertos_completos
    
    chamados_completos = listar_chamados_abertos_completos()
    clientes_checklist_completo = {}
    
    # Primeiro agrupa TODOS os chamados por cliente
    for chamado in chamados_completos:
        cliente = chamado['cliente']
        categoria = chamado.get('categoria', '')
        
        if cliente not in clientes_checklist_completo:
            clientes_checklist_completo[cliente] = inicializar_dados_cliente(chamado)
        
        # Se é categoria "Geral", sempre usa esse status (prioridade máxima)
        if categoria == "Geral":
            clientes_checklist_completo[cliente]['status_original'] = chamado['status']
        
        # Processa categorias específicas
        processar_categoria_checklist(clientes_checklist_completo[cliente], chamado)
    
    # Aplica filtros
    return aplicar_filtros_checklist(
        clientes_checklist_completo, chamados_sem_int, 
        status_filtro, busca_cliente, class_filtro
    )


def inicializar_dados_cliente(chamado):
    """
    Inicializa estrutura de dados para um cliente no checklist.
    
    Args:
        chamado: Dados do chamado
        
    Returns:
        dict: Estrutura inicializada
    """
    return {
        'status_original': chamado['status'],
        'id': chamado['id'],
        'batida': False, 'batida_construcao': False, 'batida_na': False,
        'escala': False, 'escala_construcao': False, 'escala_na': False,
        'feriados': False, 'feriados_construcao': False, 'feriados_na': False,
        'funcionarios': False, 'funcionarios_construcao': False, 'funcionarios_na': False,
        'pdv': False, 'pdv_construcao': False, 'pdv_na': False,
        'venda': False, 'venda_construcao': False, 'venda_na': False,
        'sso': False, 'sso_construcao': False, 'sso_na': False,
    }


def processar_categoria_checklist(dados_cliente, chamado):
    """
    Processa uma categoria específica do checklist.
    
    Args:
        dados_cliente: Dados do cliente
        chamado: Dados do chamado
    """
    cat = (chamado.get('categoria') or '').lower()
    status_lower = (chamado.get('status') or '').lower()
    observacao = (chamado.get('observacao') or '').strip()
    
    is_construcao = 'constru' in status_lower or status_lower.startswith('6')
    is_na = observacao == 'N/A'
    
    # IGNORAR chamados de problemas (status 1 e 2) - só considerar checklist manual
    is_problema_ativo = chamado['status'] in ['1. Implantado com problema', '2. Implantado refazendo']
    if is_problema_ativo:
        return
    
    # Mapear categorias
    mapeamento_categorias = {
        'batida': 'batida',
        'escala': 'escala', 
        'feriado': 'feriados',
        'funcionario': 'funcionarios',
        'funcionário': 'funcionarios',
        'pdv': 'pdv',
        'venda': 'venda',
        'sso': 'sso'
    }
    
    for termo, campo in mapeamento_categorias.items():
        if termo in cat:
            if is_na:
                dados_cliente[f'{campo}_na'] = True
            elif is_construcao:
                dados_cliente[f'{campo}_construcao'] = True
            else:
                dados_cliente[campo] = True
            break


def aplicar_filtros_checklist(clientes_completo, chamados_sem_int, status_filtro, busca_cliente, class_filtro):
    """
    Aplica filtros aos dados do checklist.
    
    Args:
        clientes_completo: Dados completos dos clientes
        chamados_sem_int: Chamados sem integração
        status_filtro: Filtro de status
        busca_cliente: Filtro de busca de cliente
        class_filtro: Filtro de classificação
        
    Returns:
        dict: Dados filtrados do checklist
    """
    clientes_checklist = {}
    
    for cliente, dados in clientes_completo.items():
        # Pega o chamado para verificar classificação
        chamado_cliente = next((c for c in chamados_sem_int if c['cliente'] == cliente), None)
        
        # Aplica filtros
        if (dados['status_original'] in status_filtro and 
            (not busca_cliente or busca_cliente.lower() in cliente.lower()) and 
            (chamado_cliente and (not class_filtro or chamado_cliente.get('classificacao','Guilherme') in class_filtro))):
            
            dados['status'] = dados['status_original']
            clientes_checklist[cliente] = dados
    
    return clientes_checklist


def obter_dados_chamados_por_cliente():
    """
    Obtém dados de chamados agrupados por cliente.
    
    Returns:
        list: Lista de dados por cliente
    """
    status_criticos = STATUS_OPTIONS[:2]  # 1 e 2
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.nome as cliente,
                   COALESCE(SUM(CASE 
                           WHEN (ch.data_resolucao IS NULL OR ch.data_resolucao = '') 
                                AND ch.status IN (?, ?) THEN 1 
                           ELSE 0 END
                   ), 0) as abertos,
                   COALESCE(SUM(CASE 
                           WHEN (ch.data_resolucao IS NOT NULL AND ch.data_resolucao != '') 
                                AND COALESCE(ch.status_original, ch.status) IN (?, ?) THEN 1 
                           ELSE 0 END
                   ), 0) as resolvidos
            FROM chamados ch
            JOIN clientes c ON ch.cliente_id = c.id
            WHERE ch.status IN (?, ?) OR COALESCE(ch.status_original, ch.status) IN (?, ?)
            GROUP BY c.nome
            HAVING abertos > 0 OR resolvidos > 0
            ORDER BY c.nome
        """, status_criticos * 4)
        
        return [dict(row) for row in cursor.fetchall()]