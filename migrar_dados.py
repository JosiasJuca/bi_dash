"""
Script de Migração dos CSVs Antigos para SQLite
Converte os dados do sistema antigo para o novo banco de dados
"""
import pandas as pd
import os
import sys
from database import init_db, adicionar_cliente, adicionar_chamado, atualizar_checklist, buscar_cliente_por_nome

# Caminhos dos arquivos antigos
PASTA_ANTIGA = os.path.join(os.path.dirname(__file__), "..", "Bi_integracao")
CSV_INTEGRACOES = os.path.join(PASTA_ANTIGA, "integracoes.csv")
CSV_TODOS_CLIENTES = os.path.join(PASTA_ANTIGA, "todos_clientes.csv")

def migrar():
    """Executa a migração completa"""
    print("🚀 Iniciando migração dos dados...")
    
    # 1. Inicializa o banco
    print("\n1️⃣ Inicializando banco de dados...")
    init_db()
    
    # 2. Migra clientes
    print("\n2️⃣ Migrando clientes...")
    if not os.path.exists(CSV_TODOS_CLIENTES):
        print(f"⚠️  Arquivo não encontrado: {CSV_TODOS_CLIENTES}")
        print("Continuando sem a lista de clientes...")
        clientes_migrados = 0
    else:
        df_clientes = pd.read_csv(CSV_TODOS_CLIENTES, encoding='utf-8')
        df_clientes.columns = df_clientes.columns.str.strip()
        col_cliente = df_clientes.columns[0]
        df_clientes[col_cliente] = df_clientes[col_cliente].str.strip().str.title()
        
        clientes_migrados = 0
        for nome in df_clientes[col_cliente].dropna().unique():
            try:
                adicionar_cliente(nome)
                clientes_migrados += 1
                print(f"   ✅ {nome}")
            except Exception as e:
                print(f"   ⚠️  {nome} - Já existe ou erro: {e}")
        
        print(f"✅ {clientes_migrados} clientes migrados")
    
    # 3. Migra integrações e chamados
    print("\n3️⃣ Migrando chamados e integrações...")
    if not os.path.exists(CSV_INTEGRACOES):
        print(f"❌ Arquivo não encontrado: {CSV_INTEGRACOES}")
        print("Sem dados de integrações para migrar.")
        return
    
    df_int = pd.read_csv(CSV_INTEGRACOES, sep=';', encoding='utf-8', dtype=str, on_bad_lines='skip')
    df_int.columns = df_int.columns.str.strip()
    df_int["Cliente"] = df_int["Cliente"].str.strip().str.title()
    
    # Garante que colunas existem
    for col in ["Status_Implantacao", "Categoria", "Observacao", "Data_Chegada", "Data_Resolucao"]:
        if col not in df_int.columns:
            df_int[col] = ""
    
    df_int["Observacao"] = df_int["Observacao"].fillna("")
    df_int["Data_Resolucao"] = df_int["Data_Resolucao"].fillna("")
    
    chamados_migrados = 0
    clientes_novos = 0
    
    for _, row in df_int.iterrows():
        nome_cliente = row["Cliente"]
        
        # Busca ou cria o cliente
        cliente = buscar_cliente_por_nome(nome_cliente)
        if not cliente:
            try:
                cliente_id = adicionar_cliente(nome_cliente)
                clientes_novos += 1
                print(f"   ➕ Novo cliente: {nome_cliente}")
            except:
                continue
        else:
            cliente_id = cliente['id']
        
        # Adiciona o chamado
        try:
            status = row.get("Status_Implantacao", "5. Status Normal")
            categoria = row.get("Categoria", "Geral")
            obs = row.get("Observacao", "")
            data_abertura = row.get("Data_Chegada", None)
            data_resolucao = row.get("Data_Resolucao", None)
            
            # Remove valores vazios
            if not data_abertura or data_abertura == "-":
                data_abertura = None
            if not data_resolucao or data_resolucao == "-":
                data_resolucao = None
            
            chamado_id = adicionar_chamado(
                cliente_id=cliente_id,
                status=status,
                categoria=categoria,
                observacao=obs,
                data_abertura=data_abertura
            )
            
            # Se tinha data de resolução, resolve o chamado
            if data_resolucao:
                from database import get_db
                with get_db() as conn:
                    cursor = conn.cursor()
                    # preserva o status original na coluna status_original
                    cursor.execute("""
                        UPDATE chamados 
                        SET data_resolucao = ?, status = '5. Status Normal', status_original = ?
                        WHERE id = ?
                    """, (data_resolucao, status, chamado_id))
            
            chamados_migrados += 1
            
        except Exception as e:
            print(f"   ⚠️  Erro ao migrar chamado de {nome_cliente}: {e}")
    
    print(f"✅ {chamados_migrados} chamados migrados")
    if clientes_novos > 0:
        print(f"✅ {clientes_novos} novos clientes adicionados durante a migração")
    
    # 4. Cria checklists baseado nas categorias
    print("\n4️⃣ Criando checklists...")
    df_pivot = df_int.pivot_table(
        index='Cliente',
        columns='Categoria',
        aggfunc='size',
        fill_value=0
    ).reset_index()
    
    checklists_criados = 0
    for _, row in df_pivot.iterrows():
        cliente = buscar_cliente_por_nome(row["Cliente"])
        if cliente:
            checklist_data = {
                'batida': 1 if row.get('Batida', 0) > 0 else 0,
                'escala': 1 if row.get('Escala', 0) > 0 else 0,
                'feriados': 1 if row.get('Feriados', 0) > 0 else 0,
                'funcionarios': 1 if row.get('Funcionários', 0) > 0 or row.get('Funcionarios', 0) > 0 else 0,
                'pdv': 1 if row.get('PDV', 0) > 0 or row.get('Pdv', 0) > 0 else 0,
                'venda': 1 if row.get('Venda', 0) > 0 else 0,
                'sso': 1 if row.get('SSO', 0) > 0 or row.get('Sso', 0) > 0 else 0,
            }
            
            try:
                atualizar_checklist(cliente['id'], **checklist_data)
                checklists_criados += 1
            except Exception as e:
                print(f"   ⚠️  Erro ao criar checklist para {row['Cliente']}: {e}")
    
    print(f"✅ {checklists_criados} checklists criados")
    
    print("\n" + "="*50)
    print("✨ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*50)
    print(f"📊 Resumo:")
    print(f"   • Clientes: {clientes_migrados + clientes_novos}")
    print(f"   • Chamados: {chamados_migrados}")
    print(f"   • Checklists: {checklists_criados}")
    print("\n🚀 Você pode agora executar: streamlit run bi_v2.py")

if __name__ == "__main__":
    try:
        migrar()
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
