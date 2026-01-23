"""
BI de Integrações - Versão 2.0 Simplificada
Sistema de gestão de integrações com SQLite
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import (
    init_db, adicionar_cliente, adicionar_chamado, resolver_chamado, 
    reabrir_chamado, listar_clientes, listar_chamados_abertos, 
    listar_chamados_resolvidos, obter_estatisticas, buscar_cliente_por_nome,
    atualizar_checklist, obter_checklist, excluir_chamado, excluir_cliente
)

# ==================== CONFIGURAÇÃO ====================
st.set_page_config(page_title="BI Integrações v2", layout="wide", page_icon="📊")

# Inicializa o banco na primeira execução
init_db()

# ==================== CONSTANTES ====================
STATUS_OPTIONS = [
    "1. Implantado com problema",
    "2. Implantado refazendo",
    "3. Novo cliente sem integração",
    "4. Implantado sem integração",
    "5. Status Normal"
]

CATEGORIAS = ["Batida", "Escala", "Feriados", "Funcionários", "PDV", "Venda", "SSO", "Geral"]

CORES_STATUS = {
    "1. Implantado com problema": "#f59e0b",
    "2. Implantado refazendo": "#3b82f6",
    "3. Novo cliente sem integração": "#ef4444",
    "4. Implantado sem integração": "#f87171",
    "5. Status Normal": "#10b981"
}

# ==================== ESTILOS ====================
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        color: white;
    }
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
tab_dashboard, tab_chamados, tab_historico, tab_clientes = st.tabs([
    "📈 Dashboard", 
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
                barmode='group',
                color_discrete_map={'abertos': '#ef4444', 'resolvidos': '#10b981'}
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("Nenhum dado disponível")
    
    st.divider()
    
    # ==================== FILTROS PARA AS TABELAS ====================
    st.subheader("🔍 Filtrar Tabelas")
    col_filtro1, col_filtro2 = st.columns(2)
    
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
            )
        ]
        
        if chamados_filtrados:
            # Agrupa por cliente e pega o último status
            clientes_vistos = {}
            for chamado in chamados_filtrados:
                cliente = chamado['cliente']
                if cliente not in clientes_vistos:
                    clientes_vistos[cliente] = chamado
            
            # Exibe a tabela
            table_html = '<div style="background: #1e1e1e; border-radius: 10px; padding: 15px; border: 1px solid #333;">'
            table_html += '<table style="width: 100%; border-collapse: collapse;">'
            table_html += '<thead><tr style="border-bottom: 2px solid #444;">'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CLIENTE</th>'
            table_html += '<th style="padding: 10px; text-align: center; color: #888; font-size: 11px;">STATUS_IMPLANTAÇÃO</th>'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">CATEGORIA</th>'
            table_html += '<th style="padding: 10px; text-align: left; color: #888; font-size: 11px;">OBSERVAÇÃO</th>'
            table_html += '</tr></thead><tbody>'
            
            for cliente, chamado in clientes_vistos.items():
                table_html += '<tr style="border-bottom: 1px solid #333;">'
                table_html += f'<td style="padding: 10px; color: white;">{chamado["cliente"]}</td>'
                table_html += f'<td style="padding: 10px; text-align: center;">{status_badge(chamado["status"])}</td>'
                table_html += f'<td style="padding: 10px; color: white;">{chamado["categoria"]}</td>'
                table_html += f'<td style="padding: 10px; color: #aaa; font-size: 13px;">{chamado.get("observacao", "") or "-"}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("Nenhum cliente com problemas")
    
    with col_tab2:
        st.subheader("⏳ Checklist de Integração")
        
        # Busca clientes sem integração (status 3 e 4)
        chamados_sem_int = [
            c for c in todos_chamados
            if 'sem integração' in c['status'].lower()
        ]
        
        # Aplica filtros
        chamados_sem_int_filtrados = [
            c for c in chamados_sem_int
            if c['status'] in status_filtro_dash and (
                not busca_cliente_dash or busca_cliente_dash.lower() in c['cliente'].lower()
            )
        ]
        
        if chamados_sem_int_filtrados:
            # Agrupa por cliente
            clientes_checklist = {}
            for chamado in chamados_sem_int_filtrados:
                cliente = chamado['cliente']
                if cliente not in clientes_checklist:
                    clientes_checklist[cliente] = {
                        'status': chamado['status'],
                        'id': chamado['id'],
                        'batida': False,
                        'escala': False,
                        'feriados': False,
                        'funcionarios': False,
                        'pdv': False,
                        'venda': False,
                        'sso': False
                    }
                # Marca a categoria como concluída
                cat = chamado['categoria'].lower()
                if 'batida' in cat:
                    clientes_checklist[cliente]['batida'] = True
                elif 'escala' in cat:
                    clientes_checklist[cliente]['escala'] = True
                elif 'feriado' in cat:
                    clientes_checklist[cliente]['feriados'] = True
                elif 'funcionario' in cat or 'funcionário' in cat:
                    clientes_checklist[cliente]['funcionarios'] = True
                elif 'pdv' in cat:
                    clientes_checklist[cliente]['pdv'] = True
                elif 'venda' in cat:
                    clientes_checklist[cliente]['venda'] = True
                elif 'sso' in cat:
                    clientes_checklist[cliente]['sso'] = True
            
            # Exibe a tabela
            table_html = '<div style="background: #1e1e1e; border-radius: 10px; padding: 15px; border: 1px solid #333;">'
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
                table_html += '<tr style="border-bottom: 1px solid #333;">'
                table_html += f'<td style="padding: 10px; color: white;">{cliente}</td>'
                table_html += f'<td style="padding: 10px; text-align: center;">{status_badge(dados["status"])}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["batida"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["escala"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["feriados"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["funcionarios"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["pdv"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["venda"] else ""}</td>'
                table_html += f'<td style="padding: 10px; text-align: center; color: #10b981; font-size: 18px;">{"✓" if dados["sso"] else ""}</td>'
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
            legend=dict(title="Status")
        )
        
        st.plotly_chart(fig_clientes, use_container_width=True)
    else:
        st.info("Nenhum chamado registrado ainda.")

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
                
                status_sel = st.selectbox("Status", STATUS_OPTIONS[:-1])  # Exceto "Status Normal"
                
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
    
    # Lista de chamados abertos
    chamados = listar_chamados_abertos()
    
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
                    if st.button("✅ Resolver", key=f"resolver_{chamado['chamado_id']}"):
                        resolver_chamado(chamado['chamado_id'])
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
            
            if st.form_submit_button("Adicionar", use_container_width=True):
                if nome_novo:
                    try:
                        adicionar_cliente(nome_novo)
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
            
            with col_btn:
                if st.button("🗑️", key=f"excluir_cli_{cliente['id']}", help="Excluir cliente e todos os seus chamados"):
                    if excluir_cliente(cliente['id']):
                        st.success(f"❌ {cliente['nome']} excluído!")
                        st.rerun()

# ==================== RODAPÉ ====================
st.divider()
st.caption("BI Integrações v2.0 | Sistema simplificado com SQLite | Moavi © 2026")
