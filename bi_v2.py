"""
BI de Integrações - Versão 2.0 Simplificada
Sistema de gestão de integrações com SQLite
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os
from database import (
    init_db, adicionar_cliente, adicionar_chamado, resolver_chamado, 
    reabrir_chamado, listar_clientes, listar_chamados_abertos, 
    listar_chamados_resolvidos, obter_estatisticas, buscar_cliente_por_nome,
    excluir_chamado, excluir_cliente, atualizar_classificacao, 
    atualizar_cliente_checklist, limpar_checklist_cliente, listar_chamados_problemas
)
# ==================== CONFIGURAÇÃO ====================
st.set_page_config(page_title="BI Integrações", layout="wide", page_icon="📊")

# Inicializa o banco na primeira execução
init_db()

# ==================== CONSTANTES ====================
STATUS_OPTIONS = [
    "1. Implantado com problema",
    "2. Implantado refazendo",
    "3. Cliente sem integração",
    "4. Integração Parcial",
    "5. Status Normal",
    "6. Integração em construção"
]

CATEGORIAS = ["Batida", "Escala", "Feriados", "Funcionários", "PDV", "Venda", "SSO", "Geral"]

CORES_STATUS = {
    "1. Implantado com problema": "#ff8800",
    "2. Implantado refazendo": "#3b82f6",
    "3. Cliente sem integração": "#ef4444",
    "4. Integração Parcial": "#f87171",
    "5. Status Normal": "#10b981",
    "6. Integração em construção": "#727170"
}

# ==================== ESTILOS ====================
st.markdown("""
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
    /* Increase table and caption sizes */
    table, th, td { font-size: 15px !important; }
    .stCaption { font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================

def status_badge(status):
    """Retorna um badge HTML colorido para o status"""
    cor = CORES_STATUS.get(status, "#6b7280")
    return f'<span class="status-badge" style="background-color: {cor};">{status}</span>'

# ==================== INTERFACE ====================

st.title("📊 BI de Integrações - v2.0")

# Abas principais
tab_dashboard, tab_checklist, tab_chamados, tab_historico, tab_clientes = st.tabs([
    "📈 Dashboard",
    "⏳ Checklist",
    "🎫 Chamados Ativos", 
    "✅ Histórico",
    "👥 Gerenciar"
])

# ==================== ABA DASHBOARD ====================
with tab_dashboard:
    # KPIs
    stats = obter_estatisticas()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total de Clientes", stats['total_clientes'])
    
    with col2:
        st.metric("Chamados Abertos", stats['chamados_abertos'], 
                 delta=None, delta_color="inverse")
    
    with col3:
        st.metric("Chamados Resolvidos", stats['chamados_resolvidos'])
    
    with col4:
        sem_int = stats['sem_integracao']
        st.metric("Cliente sem integração", sem_int, delta=None, delta_color="inverse")
    
    with col5:
        taxa = round(((stats['total_clientes'] - sem_int) / stats['total_clientes'] * 100), 1) if stats['total_clientes'] > 0 else 0
        st.metric("Taxa de Implantação", f"{taxa}%")
    
    st.divider()
    
    # Gráficos
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Distribuição por Status")
        if stats['por_status']:
            df_status = pd.DataFrame([
                {'Status': k, 'Quantidade': v} 
                for k, v in stats['por_status'].items()
            ])
            fig_status = px.pie(
                df_status, 
                values='Quantidade', 
                names='Status',
                color='Status',
                color_discrete_map=CORES_STATUS,
                hole=0.4
            )
            fig_status.update_layout(
                font=dict(size=18),
                legend=dict(font=dict(size=16))
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Nenhum chamado aberto no momento")
    
    with col_g2:
        st.subheader("📂 Chamados por Categoria")
        if stats['por_categoria']:
            df_cat = pd.DataFrame(stats['por_categoria'])
            df_cat_melted = df_cat.melt(
                id_vars='categoria',
                value_vars=['abertos', 'resolvidos'],
                var_name='Status',
                value_name='Quantidade'
            )
            fig_cat = px.bar(
                df_cat_melted,
                x='categoria',
                y='Quantidade',
                color='Status',
                text='Quantidade',
                barmode='group',
                color_discrete_map={'abertos': '#ef4444', 'resolvidos': '#10b981'}
            )
            fig_cat.update_layout(
                font=dict(size=18),
                legend=dict(font=dict(size=16)),
                margin=dict(t=30,r=10,l=10,b=30)
            )
            fig_cat.update_xaxes(showline=False, showgrid=False, zeroline=False, ticks='')
            fig_cat.update_yaxes(showline=False, showgrid=False, zeroline=False, ticks='', showticklabels=False, title='')
            fig_cat.update_traces(texttemplate='%{text}', textposition='inside', textfont=dict(size=16, color='white'))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
    
    st.divider()
    
    # ==================== FILTROS PARA AS TABELAS ====================
    st.subheader("🔍 Filtrar Tabelas")
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    # Busca todos os chamados abertos para os filtros
    todos_chamados = listar_chamados_abertos()
    
    with col_filtro1:
        status_unicos = list(set([c['status'] for c in todos_chamados]))
        status_filtro_dash = st.multiselect(
            "Filtrar por Status",
            options=status_unicos,
            default=status_unicos,
            key="filtro_status_dash"
        )
    
    with col_filtro2:
        busca_cliente_dash = st.text_input("🔍 Buscar por cliente", placeholder="Digite o nome...", key="busca_dash")

    with col_filtro3:
        classificacoes_unicas = sorted(list(set([c.get('classificacao','novo') for c in todos_chamados])))
        if not classificacoes_unicas:
            classificacoes_unicas = ['novo', '+3 meses', '+6 meses']
        class_filtro_dash = st.multiselect(
            "Filtrar por Classificação",
            options=classificacoes_unicas,
            default=classificacoes_unicas,
            key="filtro_class_dash"
        )
    
    st.divider()
    
    # ==================== TABELAS DE STATUS ====================
    col_tab1, col_tab2 = st.columns([1, 1.5])
    
    with col_tab1:
        st.subheader("📋 Status de Implantação")
        
        # Busca chamados com problemas (status 1 e 2)
        chamados_problema = [
            c for c in todos_chamados 
            if c['status'] in ['1. Implantado com problema', '2. Implantado refazendo']
        ]
        
        # Aplica filtros
        chamados_filtrados = [
            c for c in chamados_problema 
            if c['status'] in status_filtro_dash and (
                not busca_cliente_dash or busca_cliente_dash.lower() in c['cliente'].lower()
            ) and (not class_filtro_dash or c.get('classificacao','novo') in class_filtro_dash)
        ]
        
        if chamados_filtrados:
            # Exibe a tabela
            table_html = '<div style="background: #f5f5f5; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0;">'
            table_html += '<table style="width: 100%; border-collapse: collapse;">'
            table_html += '<thead><tr style="border-bottom: 2px solid #444;">'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CLIENTE</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">STATUS_IMPLANTAÇÃO</th>'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CATEGORIA</th>'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">OBSERVAÇÃO</th>'
            table_html += '</tr></thead><tbody>'
            
            for chamado in chamados_filtrados:
                table_html += '<tr style="border-bottom: 1px solid #e0e0e0;">'
                table_html += f'<td style="padding: 10px; color: #111;">{chamado["cliente"]}</td>'
                table_html += f'<td style="padding: 10px; text-align: center;">{status_badge(chamado["status"])}</td>'
                table_html += f'<td style="padding: 10px; color: #111;">{chamado["categoria"]}</td>'
                table_html += f'<td style="padding: 10px; color: #333; font-size: 13px;">{chamado.get("observacao", "") or "-"}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum cliente com problemas")
    
    with col_tab2:
        st.subheader("⏳ Checklist de Integração")
        
        # Busca clientes sem integração (status 3 e 4) e também chamados "Em construção" (status 6)
        chamados_sem_int = [
            c for c in todos_chamados
            if ('sem integração' in (c.get('status') or '').lower()) or ('parcial' in (c.get('status') or '').lower()) or ('constru' in (c.get('status') or '').lower())
        ]
        
        # Primeiro agrupa TODOS os chamados por cliente (sem filtro de status ainda)
        clientes_checklist_completo = {}
        for chamado in chamados_sem_int:
            cliente = chamado['cliente']
            categoria = chamado.get('categoria', '')
            
            if cliente not in clientes_checklist_completo:
                clientes_checklist_completo[cliente] = {
                    'status_original': chamado['status'],  # Guarda o status original
                    'id': chamado['id'],
                    'batida': False,
                    'batida_construcao': False,
                    'escala': False,
                    'escala_construcao': False,
                    'feriados': False,
                    'feriados_construcao': False,
                    'funcionarios': False,
                    'funcionarios_construcao': False,
                    'pdv': False,
                    'pdv_construcao': False,
                    'venda': False,
                    'venda_construcao': False,
                    'sso': False,
                    'sso_construcao': False
                }
            
            # Se é categoria "Geral", sempre usa esse status (prioridade máxima)
            if categoria == "Geral":
                clientes_checklist_completo[cliente]['status_original'] = chamado['status']
            
            # Marca a categoria como concluída ou em construção
            cat = (chamado.get('categoria') or '').lower()
            status_lower = (chamado.get('status') or '').lower()
            is_construcao = 'constru' in status_lower or status_lower.startswith('6')

            if 'batida' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['batida_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['batida'] = True
            elif 'escala' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['escala_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['escala'] = True
            elif 'feriado' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['feriados_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['feriados'] = True
            elif 'funcionario' in cat or 'funcionário' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['funcionarios_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['funcionarios'] = True
            elif 'pdv' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['pdv_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['pdv'] = True
            elif 'venda' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['venda_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['venda'] = True
            elif 'sso' in cat:
                if is_construcao:
                    clientes_checklist_completo[cliente]['sso_construcao'] = True
                else:
                    clientes_checklist_completo[cliente]['sso'] = True
        
        # AGORA aplica os filtros (remove clientes cujo status não está no filtro)
        clientes_checklist = {}
        for cliente, dados in clientes_checklist_completo.items():
            # Pega o chamado para verificar classificação
            chamado_cliente = next((c for c in chamados_sem_int if c['cliente'] == cliente), None)
            
            # Aplica filtros
            if dados['status_original'] in status_filtro_dash and (
                not busca_cliente_dash or busca_cliente_dash.lower() in cliente.lower()
            ) and (chamado_cliente and (not class_filtro_dash or chamado_cliente.get('classificacao','novo') in class_filtro_dash)):
                dados['status'] = dados['status_original']  # Mantém o status original
                clientes_checklist[cliente] = dados
        
        if clientes_checklist:
            # Exibe a tabela
            table_html = '<div style="background: #f5f5f5; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0;">'
            table_html += '<table style="width: 100%; border-collapse: collapse;">'
            table_html += '<thead><tr style="border-bottom: 2px solid #444;">'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CLIENTE</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">STATUS_IMPLANTAÇÃO</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">BATIDA</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">ESCALA</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">FERIADOS</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">FUNCIONÁRIOS</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">PDV</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">VENDA</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">SSO</th>'
            table_html += '</tr></thead><tbody>'

            for cliente, dados in clientes_checklist.items():
                # Se categoria em construção -> mostra ícone de construção (🛠️)
                def pick_icon(has_chamado, construcao, na=False):
                    # Ordem de prioridade:
                    # 1) Em construção -> mostrar 🛠️
                    # 2) Existe chamado (qualquer) -> mostrar ✗ (problema pendente)
                    # 3) N/A -> mostrar 'N/A'
                    # 4) Sem chamado -> mostrar ✓ (ok)
                    if construcao:
                        return ('🛠️', '#d97706')
                    if has_chamado:
                        return ('✗', '#FF0000')
                    if na:
                        return ('N/A', '#000000')
                    return ('✓', '#015524')

                batida_icon, batida_color = pick_icon(dados.get('batida'), dados.get('batida_construcao'))
                escala_icon, escala_color = pick_icon(dados.get('escala'), dados.get('escala_construcao'))
                feriados_icon, feriados_color = pick_icon(dados.get('feriados'), dados.get('feriados_construcao'), na=True)
                funcionarios_icon, funcionarios_color = pick_icon(dados.get('funcionarios'), dados.get('funcionarios_construcao'))
                pdv_icon, pdv_color = pick_icon(dados.get('pdv'), dados.get('pdv_construcao'))
                venda_icon, venda_color = pick_icon(dados.get('venda'), dados.get('venda_construcao'))
                sso_icon, sso_color = pick_icon(dados.get('sso'), dados.get('sso_construcao'), na=True)

                table_html += '<tr style="border-bottom: 1px solid #e0e0e0;">'
                table_html += f'<td style="padding: 10px; color: #111;">{cliente}</td>'
                table_html += f'<td style="padding: 10px; text-align: center;">{status_badge(dados["status"])}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {batida_color}; font-size: 20px;">{batida_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {escala_color}; font-size: 20px;">{escala_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {feriados_color}; font-size: 20px;">{feriados_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {funcionarios_color}; font-size: 20px;">{funcionarios_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {pdv_color}; font-size: 20px;">{pdv_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {venda_color}; font-size: 20px;">{venda_icon}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: {sso_color}; font-size: 20px;">{sso_icon}</td>'
                table_html += '</tr>'

            table_html += '</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum cliente sem integração")
    
    st.divider()
    
    # ==================== GRÁFICO DE CHAMADOS POR CLIENTE ====================
    st.subheader("📊 Chamados por Cliente (Totalizado)")
    
    # Busca todos os chamados (abertos e resolvidos) e agrupa por cliente
    from database import get_db
    
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
        dados_cliente = [dict(row) for row in cursor.fetchall()]
    
    if dados_cliente:
        # Converte para DataFrame e formata para o gráfico
        df_clientes = pd.DataFrame(dados_cliente)
        df_clientes_melted = df_clientes.melt(
            id_vars='cliente',
            value_vars=['abertos', 'resolvidos'],
            var_name='Status',
            value_name='Quantidade'
        )
        
        # Cria o gráfico de barras
        fig_clientes = px.bar(
            df_clientes_melted,
            x='cliente',
            y='Quantidade',
            color='Status',
            barmode='group',
            text_auto=True,
            color_discrete_map={'abertos': '#ef4444', 'resolvidos': '#10b981'},
            labels={'cliente': 'Cliente', 'Quantidade': 'Quantidade de Chamados'}
        )
        fig_clientes.update_layout(
            xaxis_tickangle=-45,
            height=500,
            showlegend=True,
            legend=dict(title="Status", font=dict(size=16)),
            font=dict(size=18),
            margin=dict(t=30,r=10,l=10,b=80)
        )
        fig_clientes.update_xaxes(showline=False, showgrid=False, zeroline=False, ticks='')
        fig_clientes.update_yaxes(showline=False, showgrid=False, zeroline=False, ticks='', showticklabels=False, title='')
        fig_clientes.update_traces(texttemplate='%{y}', textposition='inside', textfont=dict(size=16, color='white'))

        st.plotly_chart(fig_clientes, use_container_width=True)
    else:
        st.info("Nenhum chamado registrado ainda.")

# ==================== ABA CHECKLIST ====================
with tab_checklist:
    st.subheader("⏳ Gerenciar Checklist de Integração")
    st.markdown("""Use esta aba para gerenciar clientes **sem integração completa** (novos, parciais ou em construção).
    Para problemas em clientes já implantados, use a aba **Chamados Ativos**.""")
    
    # Buscar todos os clientes
    todos_clientes = listar_clientes()
    
    # Filtro de busca
    col_search, col_add = st.columns([3, 1])
    with col_search:
        busca_checklist = st.text_input("🔍 Buscar cliente", placeholder="Digite o nome...", key="busca_checklist")
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Adicionar Cliente Novo", use_container_width=True):
            st.session_state['show_add_modal'] = True
    
    # Modal para adicionar cliente
    if st.session_state.get('show_add_modal', False):
        with st.form("form_add_cliente_checklist"):
            st.markdown("### ➕ Adicionar Novo Cliente")
            novo_nome = st.text_input("Nome do Cliente")
            nova_class = st.selectbox("Classificação", ["novo", "+3 meses", "+6 meses"])
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.form_submit_button("✅ Adicionar", use_container_width=True):
                    if novo_nome:
                        try:
                            cliente_id = adicionar_cliente(novo_nome, nova_class)
                            st.success(f"✅ Cliente '{novo_nome}' adicionado!")
                            st.session_state['show_add_modal'] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")
                    else:
                        st.warning("Digite um nome")
            with col_btn2:
                if st.form_submit_button("❌ Cancelar", use_container_width=True):
                    st.session_state['show_add_modal'] = False
                    st.rerun()
    
    # Filtrar clientes
    if busca_checklist:
        clientes_filtrados = [c for c in todos_clientes if busca_checklist.lower() in c['nome'].lower()]
    else:
        clientes_filtrados = todos_clientes
    
    st.divider()
    st.markdown(f"**{len(clientes_filtrados)} clientes encontrados**")
    
    # Buscar chamados existentes para cada cliente
    from database import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cliente_id, status, categoria, id as chamado_id
            FROM chamados
            WHERE data_resolucao IS NULL OR data_resolucao = ''
        """)
        chamados_por_cliente = {}
        for row in cursor.fetchall():
            cid = row['cliente_id']
            if cid not in chamados_por_cliente:
                chamados_por_cliente[cid] = {'status': None, 'categorias': {}}
            # Pega o status (prioriza 3, 4, 6)
            if row['status'] in ['3. Cliente sem integração', '4. Integração Parcial', '6. Integração em construção']:
                chamados_por_cliente[cid]['status'] = row['status']
            # Guarda categoria e seu chamado_id
            chamados_por_cliente[cid]['categorias'][row['categoria']] = {
                'status': row['status'],
                'chamado_id': row['chamado_id']
            }
    
    # Exibir cada cliente em um card expansível
    for cliente in clientes_filtrados:
        cliente_id = cliente['id']
        cliente_nome = cliente['nome']
        cliente_class = cliente.get('classificacao', 'novo')
        
        # Pegar dados existentes
        dados_cliente = chamados_por_cliente.get(cliente_id, {'status': None, 'categorias': {}})
        status_atual = dados_cliente['status'] or '3. Cliente sem integração'
        
        with st.expander(f"👤 {cliente_nome} • {cliente_class}", expanded=False):
            col_status, col_class = st.columns([2, 1])
            
            with col_status:
                novo_status = st.selectbox(
                    "Status Geral do Cliente",
                    ["3. Cliente sem integração", "4. Integração Parcial", "6. Integração em construção"],
                    index=["3. Cliente sem integração", "4. Integração Parcial", "6. Integração em construção"].index(status_atual),
                    key=f"status_{cliente_id}"
                )
            
            with col_class:
                nova_class = st.selectbox(
                    "Classificação",
                    ["novo", "+3 meses", "+6 meses"],
                    index=["novo", "+3 meses", "+6 meses"].index(cliente_class),
                    key=f"class_check_{cliente_id}"
                )
                if nova_class != cliente_class:
                    if st.button("💾", key=f"save_class_{cliente_id}"):
                        if atualizar_classificacao(cliente_id, nova_class):
                            st.success("Classificação atualizada!")
                            st.rerun()
            
            st.markdown("#### 📋 Categorias de Integração")
            st.caption("Selecione o status de cada categoria de integração:")
            
            # Grid de categorias
            categorias_integracoes = ["Batida", "Escala", "Feriados", "Funcionários", "PDV", "Venda", "SSO"]
            
            # Organizar em 4 colunas
            cols = st.columns(4)
            categorias_atualizadas = {}
            
            for idx, categoria in enumerate(categorias_integracoes):
                col_idx = idx % 4
                with cols[col_idx]:
                    # Determinar estado atual da categoria
                    cat_info = dados_cliente['categorias'].get(categoria, {})
                    cat_status = cat_info.get('status', '')
                    
                    # Mapear para opção do selectbox
                    if categoria in ['Feriados', 'SSO']:
                        opcoes = ["N/A", "✗ Problema", "🛠️ Em Construção"]
                        if 'constru' in cat_status.lower() or cat_status == '6. Integração em construção':
                            idx_atual = 2
                        elif cat_status in ['3. Cliente sem integração', '4. Integração Parcial']:
                            idx_atual = 1
                        else:
                            idx_atual = 0
                    else:
                        opcoes = ["✓ OK", "✗ Problema", "🛠️ Em Construção"]
                        if 'constru' in cat_status.lower() or cat_status == '6. Integração em construção':
                            idx_atual = 2
                        elif cat_status in ['3. Cliente sem integração', '4. Integração Parcial']:
                            idx_atual = 1
                        else:
                            idx_atual = 0
                    
                    categorias_atualizadas[categoria] = st.selectbox(
                        categoria,
                        opcoes,
                        index=idx_atual,
                        key=f"cat_{cliente_id}_{categoria}"
                    )
            
            st.divider()
            
            # Botão para salvar todas as alterações
            col_save, col_del = st.columns([3, 1])
            with col_save:
                if st.button("💾 Salvar Alterações", key=f"save_{cliente_id}", type="primary", use_container_width=True):
                    try:
                        from database import atualizar_cliente_checklist
                        # Atualizar status e categorias
                        atualizar_cliente_checklist(
                            cliente_id=cliente_id,
                            status_geral=novo_status,
                            categorias=categorias_atualizadas
                        )
                        st.success(f"✅ Checklist de {cliente_nome} atualizado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao salvar: {e}")
            
            with col_del:
                if st.button("🗑️ Limpar Tudo", key=f"clear_{cliente_id}", type="secondary", use_container_width=True):
                    try:
                        from database import limpar_checklist_cliente
                        limpar_checklist_cliente(cliente_id)
                        st.success(f"✅ Checklist de {cliente_nome} limpo!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")

# ==================== ABA CHAMADOS ATIVOS ====================
with tab_chamados:
    st.subheader("🎫 Gerenciar Chamados Ativos")
    
    # Formulário para novo chamado
    with st.expander("➕ Adicionar Novo Chamado", expanded=False):
        with st.form("form_novo_chamado"):
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                # Busca de cliente com autocomplete
                clientes = listar_clientes()
                nomes_clientes = [c['nome'] for c in clientes]
                
                cliente_sel = st.selectbox("Cliente", ["+ Novo Cliente"] + nomes_clientes)
                
                if cliente_sel == "+ Novo Cliente":
                    novo_cliente_nome = st.text_input("Nome do Novo Cliente")
                
                status_sel = st.selectbox("Status", [
                    "1. Implantado com problema",
                    "2. Implantado refazendo"
                ])  # Apenas status de problema
                
            with col_f2:
                categoria_sel = st.selectbox("Categoria", CATEGORIAS)
                data_abertura = st.date_input("Data de Abertura", value=date.today())
                observacao = st.text_area("Observação")
            
            if st.form_submit_button("💾 Criar Chamado", use_container_width=True):
                try:
                    # Adiciona ou busca cliente
                    if cliente_sel == "+ Novo Cliente":
                        if novo_cliente_nome:
                            cliente_id = adicionar_cliente(novo_cliente_nome)
                            st.success(f"✅ Cliente '{novo_cliente_nome}' criado!")
                        else:
                            st.error("⚠️ Digite o nome do novo cliente")
                            st.stop()
                    else:
                        cliente = buscar_cliente_por_nome(cliente_sel)
                        cliente_id = cliente['id']
                    
                    # Adiciona chamado
                    adicionar_chamado(
                        cliente_id=cliente_id,
                        status=status_sel,
                        categoria=categoria_sel,
                        observacao=observacao,
                        data_abertura=data_abertura.isoformat()
                    )
                    
                    st.success("✅ Chamado criado com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Erro: {e}")
    
    st.divider()
    
    # Lista de chamados abertos (apenas status 1 e 2)
    chamados = listar_chamados_problemas()
    
    if not chamados:
        st.info("🎉 Nenhum chamado aberto! Tudo funcionando perfeitamente.")
    else:
        # Filtros
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            status_filtro = st.multiselect(
                "Filtrar por Status",
                options=list(set([c['status'] for c in chamados])),
                default=list(set([c['status'] for c in chamados]))
            )
        
        with col_filtro2:
            busca_nome = st.text_input("🔍 Buscar por cliente", placeholder="Digite o nome...")
        
        # Aplica filtros
        chamados_filtrados = [
            c for c in chamados 
            if c['status'] in status_filtro and (
                not busca_nome or busca_nome.lower() in c['cliente'].lower()
            )
        ]
        
        st.markdown(f"**{len(chamados_filtrados)} chamados encontrados**")
        
        # Exibe chamados em cards
        for chamado in chamados_filtrados:
            with st.container():
                col_info, col_acoes = st.columns([4, 1])
                
                with col_info:
                    st.markdown(f"### {chamado['cliente']}")
                    st.markdown(status_badge(chamado['status']), unsafe_allow_html=True)
                    st.markdown(f"**Categoria:** {chamado['categoria']}")
                    if chamado['observacao']:
                        st.markdown(f"**Obs:** {chamado['observacao']}")
                    st.caption(f"Aberto em: {chamado['data_abertura']}")
                
                with col_acoes:
                    with st.form(f"form_resolver_{chamado['chamado_id']}"):
                        resolucao_txt = st.text_area("O que foi resolvido?", key=f"resolucao_{chamado['chamado_id']}")
                        if st.form_submit_button("✅ Resolver", use_container_width=True):
                            if not resolucao_txt.strip():
                                st.warning("Descreva o que foi resolvido!")
                                st.stop()
                            # Atualiza o chamado com a resolução
                            from database import get_db
                            with get_db() as conn:
                                cursor = conn.cursor()
                                cursor.execute("""
                                    UPDATE chamados SET resolucao = ?, status_original = COALESCE(status_original, status), status = '5. Status Normal', data_resolucao = CURRENT_DATE, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?
                                """, (resolucao_txt, chamado['chamado_id']))
                            st.success("Resolvido!")
                            st.rerun()
                    if st.button("🗑️ Excluir", key=f"excluir_ch_{chamado['chamado_id']}", type="secondary"):
                        if excluir_chamado(chamado['chamado_id']):
                            st.success("❌ Chamado excluído!")
                            st.rerun()
                
                st.divider()

# ==================== ABA HISTÓRICO ====================
with tab_historico:
    st.subheader("✅ Histórico de Chamados Resolvidos")
    
    historico = listar_chamados_resolvidos()
    
    if not historico:
        st.info("Nenhum chamado resolvido ainda.")
    else:
        # Busca
        busca_hist = st.text_input("🔍 Buscar no histórico", placeholder="Digite o nome do cliente...")
        
        # Filtra
        if busca_hist:
            historico = [h for h in historico if busca_hist.lower() in h['cliente'].lower()]
        
        st.markdown(f"**{len(historico)} chamados resolvidos**")
        
        # Exibe os chamados diretamente da lista
        for chamado in historico:
            col_tab, col_btn1, col_btn2 = st.columns([4, 1, 1])
            
            with col_tab:
                st.markdown(f"**{chamado['cliente']}** • {chamado['categoria']}")
                if chamado['observacao']:
                    st.caption(chamado['observacao'])
                if chamado.get('resolucao'):
                    st.markdown(f"<span style='color:#10b981'><b>Resolução:</b> {chamado['resolucao']}</span>", unsafe_allow_html=True)
                st.caption(f"Aberto: {chamado['data_abertura']} → Resolvido: {chamado['data_resolucao']}")
            
            with col_btn1:
                if st.button("🔁", key=f"reabrir_{chamado['chamado_id']}", help="Reabrir chamado"):
                    reabrir_chamado(chamado['chamado_id'])
                    st.success("Chamado reaberto!")
                    st.rerun()
            
            with col_btn2:
                if st.button("🗑️", key=f"excluir_hist_{chamado['chamado_id']}", help="Excluir chamado", type="secondary"):
                    if excluir_chamado(chamado['chamado_id']):
                        st.success("Excluído!")
                        st.rerun()
            
            st.divider()

# ==================== ABA GERENCIAR CLIENTES ====================
with tab_clientes:
    st.subheader("👥 Gerenciar Clientes")
    
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.markdown("### ➕ Adicionar Cliente")
        with st.form("form_add_cliente"):
            nome_novo = st.text_input("Nome do Cliente")
            classificacao_novo = st.selectbox("Classificação", ["novo", "+3 meses", "+6 meses"])
            
            if st.form_submit_button("Adicionar", use_container_width=True):
                if nome_novo:
                    try:
                        adicionar_cliente(nome_novo, classificacao_novo)
                        st.success(f"✅ {nome_novo} adicionado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")
                else:
                    st.warning("Digite um nome")
    
    with col_list:
        st.markdown("### 📋 Lista de Clientes")
        clientes = listar_clientes()
        
        busca_cli = st.text_input("🔍 Buscar cliente", key="busca_clientes")
        
        if busca_cli:
            clientes = [c for c in clientes if busca_cli.lower() in c['nome'].lower()]
        
        st.markdown(f"**{len(clientes)} clientes cadastrados**")
        
        for cliente in clientes:
            col_nome, col_btn = st.columns([4, 1])
            
            with col_nome:
                st.markdown(f"• **{cliente['nome']}**")
                st.caption(f"Classificação: {cliente.get('classificacao','novo')}")
            
            with col_btn:
                # seletor rápido para alterar classificacao
                new_class = st.selectbox("", ["novo", "+3 meses", "+6 meses"], index=["novo", "+3 meses", "+6 meses"].index(cliente.get('classificacao','novo')), key=f"class_{cliente['id']}")
                if st.button("💾", key=f"salvar_class_{cliente['id']}"):
                    if atualizar_classificacao(cliente['id'], new_class):
                        st.success("Classificação atualizada!")
                        st.rerun()
                if st.button("🗑️", key=f"excluir_cli_{cliente['id']}", help="Excluir cliente e todos os seus chamados"):
                    if excluir_cliente(cliente['id']):
                        st.success(f"❌ {cliente['nome']} excluído!")
                        st.rerun()

# ==================== RODAPÉ ====================
st.divider()
st.caption("BI Integrações v2.0 | Moavi © 2026")

# ==================== BOTÃO DE DOWNLOAD DO BANCO ====================
with st.expander(''):
    db_path = os.path.join(os.path.dirname(__file__), "integracoes.db")
    if os.path.exists(db_path):
        with open(db_path, "rb") as f:
            st.download_button(
                label="",
                data=f,
                file_name="integracoes.db",
                mime="application/octet-stream"
            )
