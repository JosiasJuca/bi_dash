"""
Componentes para renderização de gráficos e visualizações.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.constants import STATUS_LABELS, CORES_STATUS


def renderizar_grafico_status(stats):
    """
    Renderiza gráfico de pizza com distribuição por status.
    
    Args:
        stats (dict): Dicionário com estatísticas do sistema
    """
    st.subheader(" Distribuição por Status")
    
    if stats['por_status']:
        df_status = pd.DataFrame([
            {'Status': k, 'Quantidade': v}
            for k, v in stats['por_status'].items()
        ])
        
        # Mapeia os rótulos longos para nomes amigáveis usados na legenda
        df_status['Label'] = df_status['Status'].map(lambda s: STATUS_LABELS.get(s, s))
        
        # Gera mapa de cores baseado nos labels (mantendo cores originais)
        label_color_map = {STATUS_LABELS.get(k, k): v for k, v in CORES_STATUS.items()}
        
        fig_status = px.pie(
            df_status,
            values='Quantidade',
            names='Label',
            color='Label',
            color_discrete_map=label_color_map,
            hole=0.4
        )
        fig_status.update_layout(
            font=dict(size=18),
            legend=dict(font=dict(size=16))
        )
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.info("Nenhum chamado aberto no momento")


def renderizar_grafico_categorias(stats):
    """
    Renderiza gráfico de barras com chamados por categoria.
    
    Args:
        stats (dict): Dicionário com estatísticas do sistema
    """
    st.subheader(" Chamados por Categoria")
    
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
            color_discrete_map={'abertos': '#9CA3AF', 'resolvidos': '#006ED2'}
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


def renderizar_grafico_clientes(dados_cliente):
    """
    Renderiza gráfico de chamados por cliente.
    
    Args:
        dados_cliente (list): Lista com dados de chamados por cliente
    """
    st.subheader(" Chamados por Cliente (Totalizado)")
    
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
            color_discrete_map={'abertos': '#9CA3AF', 'resolvidos': '#006ED2'},
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


def renderizar_metricas_kpi(stats):
    """
    Renderiza as métricas principais do dashboard.
    
    Args:
        stats (dict): Dicionário com estatísticas do sistema
    """
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
        total = stats['total_clientes']
        taxa = round(((total - sem_int) / total * 100), 1) if total > 0 else 0
        st.metric("Taxa de Implantação", f"{taxa}%")


def renderizar_filtros_dashboard():
    """
    Renderiza os filtros para as tabelas do dashboard.
    
    Returns:
        tuple: (status_filtro, busca_cliente, class_filtro, todos_chamados)
    """
    from src.database.operations import listar_chamados_abertos
    
    st.subheader(" Filtrar Tabelas")
    col_filtro1, col_filtro2, col_filtro3 = st.columns(3)
    
    # Busca todos os chamados abertos para os filtros
    todos_chamados = listar_chamados_abertos()
    
    with col_filtro1:
        status_unicos = list(set([c['status'] for c in todos_chamados]))
        status_filtro = st.multiselect(
            "Filtrar por Status",
            options=status_unicos,
            default=status_unicos,
            key="filtro_status_dash"
        )
    
    with col_filtro2:
        busca_cliente = st.text_input(
            "🔍 Buscar por cliente", 
            placeholder="Digite o nome...", 
            key="busca_dash"
        )

    with col_filtro3:
        classificacoes_unicas = sorted(list(set([
            c.get('classificacao','Guilherme') for c in todos_chamados
        ])))
        if not classificacoes_unicas:
            classificacoes_unicas = ['Guilherme', 'Eduardo', 'Marcelo']
        
        class_filtro = st.multiselect(
            "Filtrar por Responsável",
            options=classificacoes_unicas,
            default=classificacoes_unicas,
            key="filtro_class_dash"
        )
    
    return status_filtro, busca_cliente, class_filtro, todos_chamados


def gerar_grafico_pizza(valores, labels, titulo):
    """
    Gera um gráfico de pizza usando Plotly.
    
    Args:
        valores (list): Lista de valores numéricos
        labels (list): Lista de labels correspondentes
        titulo (str): Título do gráfico
        
    Returns:
        plotly.graph_objects.Figure: Objeto figura do Plotly
    """
    import plotly.graph_objects as go
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=valores,
        hole=0.3,  # Para criar um gráfico de rosquinha
        textinfo='label+percent',
        textposition='outside',
        marker_line=dict(color='#FFFFFF', width=2)
    )])
    
    fig.update_layout(
        title=titulo,
        title_x=0.5,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.01
        ),
        margin=dict(t=50, b=50, l=50, r=150),
        height=400
    )
    
    return fig