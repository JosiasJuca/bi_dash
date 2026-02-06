"""
Componente de histórico e relatórios.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from src.database.operations import (
    listar_historico_completo, obter_estatisticas_periodo, buscar_resolvidos_periodo,
    get_db
)
from src.utils.helpers import status_badge
from src.components.charts import gerar_grafico_pizza


def renderizar_historico():
    """Renderiza a aba de histórico e relatórios."""
    st.subheader(" Histórico e Relatórios")
    
    # Filtros de período
    col_periodo1, col_periodo2 = st.columns(2)
    
    with col_periodo1:
        data_inicio = st.date_input(
            "Data Início",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
    
    with col_periodo2:
        data_fim = st.date_input(
            "Data Fim",
            value=date.today(),
            max_value=date.today()
        )
    
    if data_inicio > data_fim:
        st.error("⚠️ Data inicial não pode ser maior que a data final!")
        return
    
    # (Estatísticas resumidas removidas por solicitação)
    st.divider()
    
    # Tabs para diferentes visualizações — removida a aba 'Histórico'
    tab_graficos, tab_resolvidos = st.tabs([" Gráficos", " Resolvidos"])

    with tab_graficos:
        renderizar_graficos_historico(data_inicio, data_fim)

    with tab_resolvidos:
        renderizar_chamados_resolvidos(data_inicio, data_fim)


def renderizar_estatisticas_periodo(data_inicio, data_fim):
    """
    Renderiza estatísticas do período selecionado.
    
    Args:
        data_inicio (date): Data inicial
        data_fim (date): Data final
    """
    estatisticas = obter_estatisticas_periodo(data_inicio.isoformat(), data_fim.isoformat())
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(" Total de Registros", estatisticas['total_registros'])
    
    with col2:
        st.metric(" Chamados Abertos", estatisticas['chamados_problemas'])
    
    with col3:
        st.metric(" Resolvidos", estatisticas['resolvidos'])
    
    with col4:
        taxa_resolucao = 0
        if estatisticas['total_registros'] > 0:
            taxa_resolucao = round(
                (estatisticas['resolvidos'] / estatisticas['total_registros']) * 100, 1
            )
        st.metric(" Taxa de Resolução", f"{taxa_resolucao}%")


def renderizar_historico_detalhado(data_inicio, data_fim):
    """
    Renderiza histórico detalhado do período.
    
    Args:
        data_inicio (date): Data inicial
        data_fim (date): Data final
    """
    historico = listar_historico_completo(data_inicio.isoformat(), data_fim.isoformat())
    
    if not historico:
        st.info(f" Nenhum registro encontrado no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        return
    
    # Filtros adicionais
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        clientes_unicos = list(set([h['cliente'] for h in historico]))
        clientes_filtro = st.multiselect(
            "Filtrar por Cliente",
            options=clientes_unicos,
            default=clientes_unicos,
            key="filtro_clientes_hist"
        )
    
    with col_filtro2:
        status_unicos = list(set([h['status'] for h in historico]))
        status_filtro = st.multiselect(
            "Filtrar por Status",
            options=status_unicos,
            default=status_unicos,
            key="filtro_status_hist"
        )
    
    # Aplicar filtros
    historico_filtrado = [
        h for h in historico 
        if h['cliente'] in clientes_filtro and h['status'] in status_filtro
    ]
    
    st.markdown(f"**{len(historico_filtrado)} registros encontrados**")
    
    # Exibir registros
    for registro in historico_filtrado:
        with st.container():
            col_info, col_detalhes = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"### {registro['cliente']}")
                st.markdown(status_badge(registro['status']), unsafe_allow_html=True)
                st.markdown(f"**Categoria:** {registro['categoria']}")
                
                if registro['observacao']:
                    st.markdown(f"**Observação:** {registro['observacao']}")
                
                if registro['resolucao']:
                    st.markdown(f"** Resolução:** {registro['resolucao']}")
                    if registro['data_resolucao']:
                        st.caption(f"Resolvido em: {registro['data_resolucao']}")
            
            with col_detalhes:
                st.caption(f"**Criado em:** {registro['data_criacao']}")
                if registro['data_atualizacao']:
                    st.caption(f"**Atualizado em:** {registro['data_atualizacao']}")
                
                # Calcular dias em aberto (se não resolvido)
                if not registro['data_resolucao'] and '1. Implantado com problema' in registro['status']:
                    data_criacao = datetime.strptime(registro['data_criacao'][:10], '%Y-%m-%d').date()
                    dias_aberto = (date.today() - data_criacao).days
                    if dias_aberto > 0:
                        st.warning(f" {dias_aberto} dias em aberto")
            
            st.divider()


def renderizar_graficos_historico(data_inicio, data_fim):
    """
    Renderiza gráficos do histórico.
    
    Args:
        data_inicio (date): Data inicial
        data_fim (date): Data final
    """
    historico = listar_historico_completo(data_inicio.isoformat(), data_fim.isoformat())
    
    if not historico:
        st.info(" Nenhum dado para gerar gráficos no período selecionado")
        return
    
    # Converter para DataFrame e filtrar apenas itens resolvidos
    df = pd.DataFrame(historico)
    if 'data_resolucao' in df.columns:
        df = df[df['data_resolucao'].notnull() & (df['data_resolucao'] != '')]

    if df.empty:
        st.info(" Nenhum registro resolvido no período para gerar gráficos")
        return

    # Alinha os dois gráficos restantes na mesma linha
    col_clientes, col_evolucao = st.columns(2)

    with col_clientes:
        st.subheader(" Distribuição por Cliente")
        contagem_clientes = df['cliente'].value_counts().head(10)  # Top 10 clientes
        fig_clientes = gerar_grafico_pizza(
            list(contagem_clientes.values),
            list(contagem_clientes.index),
            "Top 10 Clientes"
        )
        st.plotly_chart(fig_clientes, use_container_width=True)

    with col_evolucao:
        st.subheader(" Evolução de Resoluções")
        try:
            # Agrupar por data_resolucao para mostrar quando os itens foram resolvidos
            df_res = df.copy()
            df_res['data_resolucao'] = pd.to_datetime(df_res['data_resolucao'])
            df_res['data_apenas'] = df_res['data_resolucao'].dt.date
            evolucao = df_res.groupby('data_apenas').size().reset_index(name='count')
            evolucao = evolucao.sort_values('data_apenas')

            import plotly.express as px

            fig = px.line(
                evolucao,
                x='data_apenas',
                y='count',
                title='Resoluções por Dia',
                markers=True
            )
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Número de Resoluções",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao gerar gráfico de evolução: {e}")


def renderizar_grafico_evolucao_temporal(df):
    """
    Renderiza gráfico de evolução temporal.
    
    Args:
        df (DataFrame): DataFrame com os dados
    """
    try:
        # Converter data_criacao para datetime
        df['data_criacao'] = pd.to_datetime(df['data_criacao'])
        df['data_apenas'] = df['data_criacao'].dt.date
        
        # Agrupar por data
        evolucao = df.groupby('data_apenas').size().reset_index(name='count')
        evolucao = evolucao.sort_values('data_apenas')
        
        # Gráfico com Plotly
        import plotly.express as px
        
        fig = px.line(
            evolucao, 
            x='data_apenas', 
            y='count',
            title='Registros por Dia',
            markers=True
        )
        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Número de Registros",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao gerar gráfico temporal: {e}")


def renderizar_chamados_resolvidos(data_inicio, data_fim):
    """
    Renderiza lista de chamados resolvidos.
    
    Args:
        data_inicio (date): Data inicial
        data_fim (date): Data final
    """
    resolvidos = buscar_resolvidos_periodo(data_inicio.isoformat(), data_fim.isoformat())
    
    if not resolvidos:
        st.info(f" Nenhum chamado foi resolvido no período de {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
        return
    
    # ======= FILTROS PARA A SEÇÃO RESOLVIDOS =======
    col_f1, col_f2, col_f3 = st.columns([2, 3, 2])

    with col_f1:
        buscar_cliente = st.text_input(" Buscar por cliente", value="", key="buscar_resolvidos_cliente")

    with col_f2:
        buscar_texto = st.text_input(" Buscar por texto (resolução/observação)", value="", key="buscar_resolvidos_texto")

    with col_f3:
        categorias_unicas = list(dict.fromkeys([r.get('categoria', '') for r in resolvidos]))
        filtro_categoria = st.multiselect(" Filtrar por Categoria", options=categorias_unicas, key="filtrar_resolvidos_categoria")

    # Aplica os filtros
    resolvidos_filtrados = [
        r for r in resolvidos
        if (not buscar_cliente or buscar_cliente.lower() in (r.get('cliente') or '').lower())
        and (not buscar_texto or buscar_texto.lower() in (r.get('resolucao') or '').lower() or buscar_texto.lower() in (r.get('observacao') or '').lower())
        and (not filtro_categoria or r.get('categoria') in filtro_categoria)
    ]

    st.markdown(f"** {len(resolvidos_filtrados)} chamados foram resolvidos no período**")

    # Exibir chamados resolvidos
    for resolvido in resolvidos_filtrados:
        with st.container():
            col_info, col_tempo, col_btn = st.columns([4, 1, 1])

            with col_info:
                st.markdown(f"### {resolvido['cliente']}")

                # Status original e atual
                if resolvido.get('status_original'):
                    st.markdown(f"**Status anterior:** {resolvido['status_original']}")
                st.markdown(status_badge(resolvido['status']), unsafe_allow_html=True)

                st.markdown(f"**Categoria:** {resolvido['categoria']}")

                if resolvido['resolucao']:
                    st.markdown(f"** Como foi resolvido:** {resolvido['resolucao']}")

                if resolvido['observacao']:
                    with st.expander(" Ver observações originais"):
                        st.markdown(resolvido['observacao'])

            with col_tempo:
                st.caption(f"**Aberto em:** {resolvido['data_criacao'][:10]}")
                st.caption(f"**Resolvido em:** {resolvido['data_resolucao']}")

                # Calcular tempo de resolução
                try:
                    data_abertura = datetime.strptime(resolvido['data_criacao'][:10], '%Y-%m-%d').date()
                    data_resolucao = datetime.strptime(resolvido['data_resolucao'], '%Y-%m-%d').date()
                    tempo_resolucao = (data_resolucao - data_abertura).days

                    if tempo_resolucao == 0:
                        st.success(" Resolvido no mesmo dia!")
                    elif tempo_resolucao == 1:
                        st.info(" Resolvido em 1 dia")
                    else:
                        st.info(f" Resolvido em {tempo_resolucao} dias")

                except Exception:
                    st.caption("Tempo não calculado")

            with col_btn:
                # Botão para excluir chamado resolvido
                from src.database.operations import excluir_chamado

                if st.button(" Excluir", key=f"excluir_res_{resolvido['chamado_id']}", type="secondary"):
                    try:
                        if excluir_chamado(resolvido['chamado_id']):
                            st.success("Chamado excluído com sucesso.")
                            st.rerun()
                        else:
                            st.error("Falha ao excluir o chamado.")
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")

            st.divider()


def exportar_relatorio(data_inicio, data_fim):
    """
    Exporta relatório do período para CSV.
    
    Args:
        data_inicio (date): Data inicial
        data_fim (date): Data final
    """
    try:
        historico = listar_historico_completo(data_inicio.isoformat(), data_fim.isoformat())
        
        if not historico:
            st.warning("Nenhum dado para exportar no período selecionado")
            return None
        
        df = pd.DataFrame(historico)
        
        # Preparar CSV
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        
        nome_arquivo = f"relatorio_{data_inicio.strftime('%Y%m%d')}_a_{data_fim.strftime('%Y%m%d')}.csv"
        
        return csv, nome_arquivo
        
    except Exception as e:
        st.error(f"Erro ao exportar relatório: {e}")
        return None