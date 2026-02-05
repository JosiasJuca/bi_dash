"""
Componente de checklist de integração.
"""
import streamlit as st
from src.database.operations import (
    listar_clientes, adicionar_cliente, atualizar_classificacao,
    atualizar_cliente_checklist, excluir_cliente, get_db,
    deletar_chamados_por_status, deletar_chamados_por_cliente
)
from src.utils.constants import RESPONSAVEIS
from src.utils.helpers import adicionar_mensagem_sucesso


def renderizar_checklist():
    """Renderiza a aba de checklist de integração."""
    st.subheader("Gerenciar Checklist de Integração")
    st.markdown("""Use esta aba para gerenciar clientes **sem integração completa** (novos, parciais ou em construção).
    Para problemas em clientes já implantados, use a aba **Chamados Ativos**.""")
    
    # Buscar todos os clientes
    todos_clientes = listar_clientes()
    
    # Filtro de busca e botão adicionar
    col_search, col_add = st.columns([3, 1])
    with col_search:
        busca_checklist = st.text_input("🔍 Buscar cliente", placeholder="Digite o nome...", key="busca_checklist")
    with col_add:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Adicionar Cliente Novo", use_container_width=True):
            st.session_state['show_add_modal'] = True
    
    # Modal para adicionar cliente
    if st.session_state.get('show_add_modal', False):
        renderizar_modal_adicionar_cliente()
    
    # Seção de Administração
    renderizar_secao_administracao()
    
    st.divider()
    
    # Filtrar clientes
    if busca_checklist:
        clientes_filtrados = [c for c in todos_clientes if busca_checklist.lower() in c['nome'].lower()]
    else:
        clientes_filtrados = todos_clientes
    
    st.markdown(f"**{len(clientes_filtrados)} clientes encontrados**")
    
    # Renderizar cards dos clientes
    renderizar_cards_clientes(clientes_filtrados)


def renderizar_modal_adicionar_cliente():
    """Renderiza modal para adicionar novo cliente."""
    with st.form("form_add_cliente_checklist"):
        st.markdown("### ➕ Adicionar Novo Cliente")
        novo_nome = st.text_input("Nome do Cliente")
        nova_class = st.selectbox("Responsável", RESPONSAVEIS)
        
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


def renderizar_secao_administracao():
    """Renderiza seção de administração para apagar chamados."""
    with st.expander("⚙️ Administração - Apagar Chamados"):
        st.warning("⚠️ Cuidado! Esta ação não pode ser desfeita.")
        
        tab_adm1, tab_adm2 = st.tabs(["Por Status", "Por Cliente"])
        
        # Aba 1: Apagar por Status
        with tab_adm1:
            st.subheader("Apagar todos os chamados de um status")
            col_del1, col_del2 = st.columns([2, 1])
            
            with col_del1:
                status_para_apagar = st.selectbox(
                    "Selecione o status dos chamados a apagar:",
                    ["3. Novo cliente sem integração", "5. Implantado sem integração", 
                     "6. Integração Parcial", "8. Integração em construção"],
                    key="status_apagar"
                )
            
            with col_del2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Apagar por Status", use_container_width=True, key="btn_apagar_status"):
                    total_apagado = deletar_chamados_por_status(status_para_apagar)
                    st.success(f"✅ {total_apagado} chamados com status '{status_para_apagar}' foram apagados!")
                    st.rerun()
        
        # Aba 2: Apagar por Cliente
        with tab_adm2:
            st.subheader("Apagar todos os chamados de um cliente")
            col_del3, col_del4 = st.columns([2, 1])
            
            todos_clientes_lista = listar_clientes()
            nomes_clientes = [c['nome'] for c in todos_clientes_lista]
            
            with col_del3:
                cliente_para_apagar = st.selectbox(
                    "Selecione o cliente:",
                    nomes_clientes,
                    key="cliente_apagar"
                )
            
            with col_del4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Apagar por Cliente", use_container_width=True, key="btn_apagar_cliente"):
                    cliente_selecionado = next((c for c in todos_clientes_lista if c['nome'] == cliente_para_apagar), None)
                    if cliente_selecionado:
                        total_apagado = deletar_chamados_por_cliente(cliente_selecionado['id'])
                        st.success(f"✅ {total_apagado} chamados do cliente '{cliente_para_apagar}' foram apagados!")
                        st.rerun()


def renderizar_cards_clientes(clientes_filtrados):
    """
    Renderiza cards expansíveis para cada cliente.
    
    Args:
        clientes_filtrados (list): Lista de clientes filtrados
    """
    # Buscar chamados existentes para cada cliente
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
            
            # Se for chamado 'Geral', sempre define o status geral do cliente
            if row['categoria'] == 'Geral':
                chamados_por_cliente[cid]['status'] = row['status']
            else:
                # Define status de categoria apenas se ainda não houver um status geral definido
                if chamados_por_cliente[cid]['status'] is None:
                    if row['status'] in ['3. Novo cliente sem integração', '5. Implantado sem integração', 
                                        '6. Integração Parcial', '8. Integração em construção']:
                        chamados_por_cliente[cid]['status'] = row['status']
            
            # Guarda categoria e seu chamado_id
            chamados_por_cliente[cid]['categorias'][row['categoria']] = {
                'status': row['status'],
                'chamado_id': row['chamado_id']
            }
    
    # Renderizar cada cliente
    for cliente in clientes_filtrados:
        renderizar_card_cliente(cliente, chamados_por_cliente)


def renderizar_card_cliente(cliente, chamados_por_cliente):
    """
    Renderiza card individual de um cliente.
    
    Args:
        cliente (dict): Dados do cliente
        chamados_por_cliente (dict): Chamados organizados por cliente
    """
    cliente_id = cliente['id']
    cliente_nome = cliente['nome']
    cliente_class = cliente.get('classificacao', 'Guilherme')
    
    # Pegar dados existentes
    dados_cliente = chamados_por_cliente.get(cliente_id, {'status': None, 'categorias': {}})
    status_atual = dados_cliente['status'] or '3. Novo cliente sem integração'
    
    with st.expander(f"👤 {cliente_nome} • {cliente_class}", expanded=False):
        col_status, col_class = st.columns([2, 1])
        
        with col_status:
            novo_status = st.selectbox(
                "Status Geral do Cliente",
                ["3. Novo cliente sem integração", "5. Implantado sem integração", 
                 "6. Integração Parcial", "8. Integração em construção"],
                index=["3. Novo cliente sem integração", "5. Implantado sem integração", 
                       "6. Integração Parcial", "8. Integração em construção"].index(status_atual),
                key=f"status_{cliente_id}"
            )
        
        with col_class:
            nova_class = st.selectbox(
                "Responsável",
                RESPONSAVEIS,
                index=RESPONSAVEIS.index(cliente_class) if cliente_class in RESPONSAVEIS else 0,
                key=f"class_check_{cliente_id}"
            )
            if nova_class != cliente_class:
                if st.button("💾", key=f"save_class_{cliente_id}"):
                    if atualizar_classificacao(cliente_id, nova_class):
                        st.success("Responsável atualizado!")
                        st.rerun()
        
        # Grid de categorias
        renderizar_grid_categorias(cliente_id, dados_cliente)
        
        st.divider()
        
        # Botões de ação
        col_save, col_del = st.columns([3, 1])
        with col_save:
            if st.button("💾 Salvar Alterações", key=f"save_{cliente_id}", type="primary", use_container_width=True):
                try:
                    # Coletar dados das categorias
                    categorias_atualizadas = {}
                    categorias_integracoes = ["Batida", "Escala", "Feriados", "Funcionários", "PDV", "Venda", "SSO"]
                    
                    for categoria in categorias_integracoes:
                        if f"cat_{cliente_id}_{categoria}" in st.session_state:
                            categorias_atualizadas[categoria] = st.session_state[f"cat_{cliente_id}_{categoria}"]
                    
                    atualizar_cliente_checklist(
                        cliente_id=cliente_id,
                        status_geral=novo_status,
                        categorias=categorias_atualizadas
                    )
                    adicionar_mensagem_sucesso(f"✅ Checklist de {cliente_nome} atualizado!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar: {e}")
        
        with col_del:
            st.markdown("<br>", unsafe_allow_html=True)
            confirm = st.checkbox("Confirmar exclusão permanente deste cliente", key=f"confirm_excluir_{cliente_id}")
            if confirm:
                if st.button("🗑️ Excluir Cliente", key=f"btn_excluir_cliente_{cliente_id}", type="secondary", use_container_width=True):
                    try:
                        deleted = excluir_cliente(cliente_id)
                        if deleted:
                            adicionar_mensagem_sucesso(f"✅ Cliente '{cliente_nome}' e todos os registros vinculados foram excluídos!")
                            st.rerun()
                        else:
                            st.warning("Nenhum registro excluído. Verifique se o cliente ainda existe.")
                    except Exception as e:
                        st.error(f"❌ Erro ao excluir cliente: {e}")


def renderizar_grid_categorias(cliente_id, dados_cliente):
    """
    Renderiza grid de categorias de integração.
    
    Args:
        cliente_id (int): ID do cliente
        dados_cliente (dict): Dados existentes do cliente
    """
    st.markdown("#### Categorias de Integração")
    st.caption("Selecione o status de cada categoria de integração:")
    
    categorias_integracoes = ["Batida", "Escala", "Feriados", "Funcionários", "PDV", "Venda", "SSO"]
    
    # Organizar em 4 colunas
    cols = st.columns(4)
    
    for idx, categoria in enumerate(categorias_integracoes):
        col_idx = idx % 4
        with cols[col_idx]:
            # Determinar estado atual da categoria
            cat_info = dados_cliente['categorias'].get(categoria, {})
            cat_status = cat_info.get('status', '')
            observacao = ''
            
            # Busca a observação do chamado desta categoria
            if categoria in dados_cliente['categorias']:
                with get_db() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT observacao, status FROM chamados WHERE id = ?", (dados_cliente['categorias'][categoria]['chamado_id'],))
                    obs_result = cursor.fetchone()
                    if obs_result:
                        # Ignorar se for chamado de problema ativo
                        if obs_result['status'] in ['1. Implantado com problema', '2. Implantado refazendo']:
                            cat_status = ''  # Reset para tratar como OK
                        else:
                            observacao = obs_result['observacao'] or ''
            
            # Mapear para opção do selectbox
            opcoes = ["✓ OK", "✗ Problema", "🛠️ Em Construção", "N/A"]
            idx_atual = 0  # Default OK
            
            # Determina o índice baseado na observação N/A primeiro, depois status
            if observacao == 'N/A':
                idx_atual = 3  # N/A
            elif 'constru' in cat_status.lower() or cat_status == '8. Integração em construção':
                idx_atual = 2  # Em Construção
            elif cat_status in ['3. Novo cliente sem integração', '5. Implantado sem integração', '6. Integração Parcial']:
                idx_atual = 1  # Problema
            elif not cat_status or cat_status == '7. Status Normal':
                idx_atual = 0  # OK
            
            st.selectbox(
                categoria,
                opcoes,
                index=idx_atual,
                key=f"cat_{cliente_id}_{categoria}"
            )