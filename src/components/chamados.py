"""
Componente de gestão de chamados ativos.
"""
import streamlit as st
from datetime import date, timedelta
from src.database.operations import (
    listar_clientes, buscar_cliente_por_nome, adicionar_cliente,
    adicionar_chamado, listar_chamados_problemas, atualizar_etapa_chamado,
    excluir_chamado, get_db
)
from src.utils.constants import CATEGORIAS, ETAPAS_CHAMADO
from src.utils.helpers import status_badge, obter_estilos_etapa


def renderizar_chamados():
    """Renderiza a aba de gestão de chamados ativos."""
    st.subheader(" Gerenciar Chamados Ativos")
    
    # Formulário para novo chamado
    renderizar_formulario_novo_chamado()
    
    st.divider()
    
    # Lista de chamados abertos
    renderizar_lista_chamados()


def renderizar_formulario_novo_chamado():
    """Renderiza formulário para criação de novo chamado."""
    with st.expander(" Adicionar Novo Chamado", expanded=False):
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
                
                categoria_sel = st.selectbox("Categoria", CATEGORIAS)
        
            with col_f2:
                data_abertura = st.date_input("Data de Abertura", value=date.today())
                
                # Campo para previsão de resolução
                previsao_default = date.today() + timedelta(days=7)
                previsao_resolucao = st.date_input("Previsão de Resolução", value=previsao_default)
                
                # Seleção de etapa
                etapa_sel = st.selectbox("Etapa", ETAPAS_CHAMADO)
                
                observacao = st.text_area("Observação")
            
            if st.form_submit_button(" Criar Chamado", use_container_width=True):
                processar_novo_chamado(
                    cliente_sel, novo_cliente_nome if cliente_sel == "+ Novo Cliente" else None,
                    status_sel, categoria_sel, data_abertura, previsao_resolucao,
                    etapa_sel, observacao
                )


def processar_novo_chamado(cliente_sel, novo_cliente_nome, status_sel, categoria_sel, 
                          data_abertura, previsao_resolucao, etapa_sel, observacao):
    """
    Processa a criação de um novo chamado.
    
    Args:
        cliente_sel: Cliente selecionado
        novo_cliente_nome: Nome do novo cliente (se aplicável)
        status_sel: Status selecionado
        categoria_sel: Categoria selecionada
        data_abertura: Data de abertura
        previsao_resolucao: Data de previsão
        etapa_sel: Etapa selecionada
        observacao: Observação
    """
    try:
        # Adiciona ou busca cliente
        if cliente_sel == "+ Novo Cliente":
            if novo_cliente_nome:
                cliente_id = adicionar_cliente(novo_cliente_nome)
                st.success(f" Cliente '{novo_cliente_nome}' criado!")
            else:
                st.error(" Digite o nome do novo cliente")
                st.stop()
        else:
            cliente = buscar_cliente_por_nome(cliente_sel)
            cliente_id = cliente['id']
        
        # Adiciona observação com previsão de resolução
        observacao_completa = observacao
        if previsao_resolucao:
            previsao_str = previsao_resolucao.strftime('%d/%m/%Y')
            if observacao_completa:
                observacao_completa += f" | Previsão: {previsao_str}"
            else:
                observacao_completa = f"Previsão: {previsao_str}"
        
        # Adiciona chamado
        adicionar_chamado(
            cliente_id=cliente_id,
            status=status_sel,
            categoria=categoria_sel,
            observacao=observacao_completa,
            data_abertura=data_abertura.isoformat(),
            etapa=etapa_sel
        )
        
        st.success("✅ Chamado criado com sucesso!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Erro: {e}")


def renderizar_lista_chamados():
    """Renderiza lista de chamados ativos."""
    chamados = listar_chamados_problemas()
    
    if not chamados:
        st.info(" Nenhum chamado aberto! Tudo funcionando perfeitamente.")
        return
    
    # Filtros
    renderizar_filtros_chamados(chamados)
    
    # Lista filtrada
    chamados_filtrados = aplicar_filtros_chamados(chamados)
    
    st.markdown(f"**{len(chamados_filtrados)} chamados encontrados**")

    # Exibe chamados em cards
    for chamado in chamados_filtrados:
        renderizar_card_chamado(chamado)


def renderizar_filtros_chamados(chamados):
    """
    Renderiza filtros para a lista de chamados.
    
    Args:
        chamados (list): Lista de chamados
    """
    col_filtro1, col_filtro2 = st.columns(2)
    
    with col_filtro1:
        st.multiselect(
            "Filtrar por Status",
            options=list(set([c['status'] for c in chamados])),
            default=list(set([c['status'] for c in chamados])),
            key="status_filtro_chamados"
        )
    
    with col_filtro2:
        st.text_input(" Buscar por cliente", placeholder="Digite o nome...", key="busca_nome_chamados")


def aplicar_filtros_chamados(chamados):
    """
    Aplica filtros aos chamados.
    
    Args:
        chamados (list): Lista de chamados
        
    Returns:
        list: Chamados filtrados
    """
    status_filtro = st.session_state.get("status_filtro_chamados", [])
    busca_nome = st.session_state.get("busca_nome_chamados", "")
    
    return [
        c for c in chamados 
        if c['status'] in status_filtro and (
            not busca_nome or busca_nome.lower() in c['cliente'].lower()
        )
    ]


def renderizar_card_chamado(chamado):
    """
    Renderiza card individual de um chamado.
    
    Args:
        chamado (dict): Dados do chamado
    """
    with st.container():
        col_info, col_acoes = st.columns([4, 1])
        
        with col_info:
            st.markdown(f"### {chamado['cliente']}")
            st.markdown(status_badge(chamado['status']), unsafe_allow_html=True)
            st.markdown(f"**Categoria:** {chamado['categoria']}")
            
            # Exibir etapa atual com destaque
            etapa_atual = chamado.get('etapa', 'Não iniciado')
            etapa_bg = obter_estilos_etapa(etapa_atual)
            st.markdown(
                f'**Etapa atual:** <span style="background-color: {etapa_bg}; padding: 4px 8px; border-radius: 4px; font-weight: 500;">{etapa_atual}</span>',
                unsafe_allow_html=True
            )
            
            if chamado['observacao']:
                st.markdown(f"**Obs:** {chamado['observacao']}")
            st.caption(f"Aberto em: {chamado['data_abertura']}")

        with col_acoes:
            renderizar_acoes_chamado(chamado, etapa_atual)
        
        st.divider()


def renderizar_acoes_chamado(chamado, etapa_atual):
    """
    Renderiza ações disponíveis para um chamado.
    
    Args:
        chamado (dict): Dados do chamado
        etapa_atual (str): Etapa atual do chamado
    """
    # Seção para atualizar etapa
    with st.expander(" Atualizar Etapa"):
        nova_etapa = st.selectbox(
            "Nova etapa",
            ETAPAS_CHAMADO,
            index=ETAPAS_CHAMADO.index(etapa_atual) if etapa_atual in ETAPAS_CHAMADO else 0,
            key=f"etapa_{chamado['chamado_id']}"
        )
        if st.button(" Atualizar Etapa", key=f"btn_etapa_{chamado['chamado_id']}", use_container_width=True):
            try:
                atualizar_etapa_chamado(chamado['chamado_id'], nova_etapa)
                st.success(f"Etapa atualizada para: {nova_etapa}")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar etapa: {e}")
    
    # Seção para editar observação
    with st.expander(" Editar Observação"):
        texto_atual = chamado.get('observacao', '') or ''
        novo_texto = st.text_area("Observação", value=texto_atual, key=f"edit_obs_{chamado['chamado_id']}")
        if st.button(" Salvar Observação", key=f"save_obs_{chamado['chamado_id']}", use_container_width=True):
            try:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE chamados SET observacao = ?, atualizado_em = CURRENT_TIMESTAMP WHERE id = ?",
                        (novo_texto, chamado['chamado_id'])
                    )
                st.success("Observação atualizada!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar observação: {e}")
    
    # Seção para resolver chamado
    with st.form(f"form_resolver_{chamado['chamado_id']}"):
        resolucao_txt = st.text_area("O que foi resolvido?", key=f"resolucao_{chamado['chamado_id']}")
        if st.form_submit_button(" Resolver", use_container_width=True):
            if not resolucao_txt.strip():
                st.warning("Descreva o que foi resolvido!")
                st.stop()
            
            # Atualiza o chamado com a resolução
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE chamados SET 
                        resolucao = ?, 
                        status_original = COALESCE(status_original, status), 
                        status = '7. Status Normal', 
                        data_resolucao = CURRENT_DATE, 
                        atualizado_em = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (resolucao_txt, chamado['chamado_id']))
            st.success("Resolvido!")
            st.rerun()
    
    # Botão de exclusão
    if st.button(" Excluir", key=f"excluir_ch_{chamado['chamado_id']}", type="secondary"):
        if excluir_chamado(chamado['chamado_id']):
            st.success("❌ Chamado excluído!")
            st.rerun()