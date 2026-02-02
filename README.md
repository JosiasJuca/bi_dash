# 📊 BI de Integrações - v2.0

Sistema **simplificado e robusto** para gestão de integrações de clientes, usando SQLite ao invés de múltiplos CSVs.

## ✨ Novidades da v2.0

### 🎯 Vantagens sobre a versão anterior

| Antes (CSVs) | Agora (SQLite) |
|--------------|----------------|
| ❌ Múltiplos CSVs desincronizados | ✅ Banco de dados único e consistente |
| ❌ Merges complexos e lentos | ✅ Consultas SQL rápidas e simples |
| ❌ Fácil corromper dados | ✅ Transações atômicas (tudo ou nada) |
| ❌ Difícil fazer backups | ✅ 1 arquivo = backup completo |
| ❌ 600+ linhas de código | ✅ 400+ linhas limpas e organizadas |
| ❌ Bugs de encoding e parsing | ✅ Tipos de dados garantidos pelo BD |

### 🚀 Funcionalidades Principais

- ✅ **Dashboard Executivo** com KPIs e gráficos interativos
- ✅ **Gestão Separada**: Checklist manual independente de chamados de problemas
- ✅ **Chamados Ativos** com previsão de resolução e tracking completo
- ✅ **Histórico Completo** de resoluções com possibilidade de reabertura
- ✅ **Busca Inteligente** por clientes e filtros avançados
- ✅ **Sistema de Categorias** para 7 tipos de integração
- ✅ **Interface Responsiva** com layout organizado verticalmente

### 📋 **Novos Recursos da Interface**

#### **Layout Reorganizado**
- **Chamados**: Primeira tabela com data de abertura e previsão de resolução
- **Checklist de Integração**: Segunda tabela com status manual por categoria
- **Separação Total**: Problemas ativos não impactam o checklist manual

#### **Gestão de Previsões**
- **Previsão Automática**: 7 dias a partir da data de abertura
- **Previsão Manual**: Definível no formulário de criação
- **Tracking Visual**: Acompanhamento direto na tabela principal

#### **Checklist Independente**
- **Controle Manual**: Configuração por categoria (Batida, Escala, Feriados, etc.)
- **Estados**: ✓ OK, ✗ Problema, 🛠️ Em Construção, N/A
- **Preservação**: Estado atual mantido entre edições

---

## 📦 Instalação e Execução

### 1. Pré-requisitos

```powershell
# Instalar dependências
pip install streamlit pandas plotly
```

### 2. Execução

```powershell
# Navegar até a pasta do projeto
cd "caminho/para/bi_dash"

# Executar o dashboard
streamlit run bi_v2.py
```

### 3. Acesso

- **URL Local**: http://localhost:8501
- **Interface**: Navegador web (Chrome, Firefox, Edge)

---

## 🏗️ Estrutura do Projeto

### **Arquivos Principais**
```
bi_v2.py          # Interface principal (Streamlit)
database.py       # Camada de dados (SQLite)
integracoes.db    # Banco de dados
requirements.txt  # Dependências Python
README.md         # Este arquivo
```

### **Scripts Auxiliares**
```
scripts/
  └── rename_statuses_simple.py  # Utilitário para renomear status
```

---

## 🎭 Guia de Uso

### **1. Dashboard** 
- **KPIs**: Visão geral dos números principais
- **Gráficos**: Distribuição por status e categoria
- **Tabelas**: Chamados ativos e checklist de integração
- **Filtros**: Por status, cliente e responsável

### **2. Checklist** 
- **Gerenciamento**: Configuração manual por cliente
- **Estados**: Definição do status de cada categoria
- **Responsáveis**: Atribuição (Guilherme, Eduardo, Marcelo)
- **Administração**: Ferramentas de limpeza em lote

### **3. Chamados Ativos**
- **Criação**: Formulário completo com previsão
- **Gestão**: Resolução e acompanhamento
- **Status**: Apenas problemas ativos (status 1 e 2)
- **Tracking**: Data de abertura e previsão visíveis

### **4. Histórico**
- **Consulta**: Todos os chamados resolvidos
- **Reabertura**: Possibilidade de reativar chamados
- **Busca**: Filtro por cliente

---

## 🔧 Status e Categorias

### **Status de Checklist (Manual)**
- `3. Novo cliente sem integração`
- `5. Implantado sem integração` 
- `6. Integração Parcial`
- `8. Integração em construção`

### **Status de Problemas (Chamados Ativos)**
- `1. Implantado com problema`
- `2. Implantado refazendo`

### **Categorias de Integração**
- **Batida**: Controle de ponto
- **Escala**: Gerenciamento de horários
- **Feriados**: Calendário corporativo
- **Funcionários**: Cadastro de pessoal
- **PDV**: Pontos de venda
- **Venda**: Sistema comercial
- **SSO**: Single Sign-On

---

## 💾 Backup e Manutenção

### **Backup Automático**
- **Download**: Botão no rodapé para baixar integracoes.db
- **Frequência**: Recomendado semanalmente
- **Localização**: Arquivo único contém todos os dados

### **Manutenção**
- **Limpeza**: Ferramentas na aba Checklist para remoção em lote
- **Scripts**: Pasta `scripts/` com utilitários diversos
- **Logs**: Sistema auto-contido sem logs externos

---

## 🎯 Melhorias da v2.0

### **Separação Inteligente**
- **Checklist Manual**: Não é afetado por chamados de problema
- **Chamados Ativos**: Sistema independente para problemas técnicos
- **Dados Limpos**: Cada área tem propósito específico

### **Interface Aprimorada**
- **Layout Vertical**: Tabelas organizadas uma embaixo da outra
- **Colunas Novas**: Data de abertura e previsão de resolução
- **Performance**: Consultas otimizadas e interface responsiva

### **Funcionalidades Avançadas**
- **Previsão Inteligente**: Cálculo automático ou manual
- **Estado Preservado**: Configurações mantidas entre sessões
- **Filtros Avançados**: Múltiplas dimensões de busca

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar este README.md
2. Consultar documentação técnica em `/docs`
3. Contatar a equipe de desenvolvimento

**Versão**: 2.0  
**Data**: Fevereiro 2026  
**Desenvolvido por**: Moavi © 2026
- ✅ Criar o banco de dados SQLite
- ✅ Importar todos os clientes de `todos_clientes.csv`
- ✅ Importar todos os chamados de `integracoes.csv`
- ✅ Criar os checklists automaticamente
- ✅ Preservar datas de abertura e resolução

**IMPORTANTE:** Os arquivos antigos **não serão modificados**. O sistema v2 é totalmente independente.

---

## 🚀 Como Usar

### Executar o Dashboard

```powershell
cd "Bi_integracao_v2"
streamlit run bi_v2.py
```

O sistema abrirá automaticamente em `http://localhost:8501`

### Interface

#### 📈 **Aba Dashboard**
- Visualize KPIs: Total de clientes, chamados abertos/resolvidos, taxa de implantação
- Gráficos de distribuição por status e categoria
- Visão geral do sistema

#### 🎫 **Aba Chamados Ativos**
- Crie novos chamados
- Adicione clientes novos ou selecione existentes
- Resolva chamados com um clique
- Filtre por status e busque por nome

#### ✅ **Aba Histórico**
- Veja todos os chamados resolvidos
- Reabra chamados se necessário
- Busque por cliente ou categoria

#### 👥 **Aba Gerenciar Clientes**
- Adicione novos clientes
- Visualize lista completa
- Busque por nome

---

## 🗄️ Estrutura do Banco de Dados

### Tabelas

#### `clientes`
```sql
id, nome, ativo, criado_em
```

#### `chamados`
```sql
id, cliente_id, status, categoria, observacao, 
data_abertura, data_resolucao, criado_em, atualizado_em
```

#### `checklist`
```sql
id, cliente_id, batida, escala, feriados, 
funcionarios, pdv, venda, sso, atualizado_em
```

---

## 📊 Status Disponíveis

| Status | Descrição |
|--------|-----------|
| 1. Implantado com problema | Cliente integrado mas com erros técnicos |
| 2. Implantado refazendo | Reprocessando a integração |
| 3. Novo cliente sem integração | Cliente novo aguardando setup inicial |
| 5. Implantado sem integração | Cliente ativo mas sem integrações |
| 7. Status Normal | ✅ Tudo funcionando corretamente |

---

## 📂 Categorias

- **Batida** - Sistema de registro de ponto
- **Escala** - Gestão de escalas de trabalho
- **Feriados** - Calendário de feriados
- **Funcionários** - Cadastro de colaboradores
- **PDV** - Integração de pontos de venda
- **Venda** - Dados e relatórios de vendas
- **SSO** - Single Sign-On
- **Geral** - Outros assuntos

---

## 💾 Backup e Manutenção

### Fazer Backup

```powershell
# Copie o arquivo do banco de dados
copy integracoes.db integracoes_backup_$(Get-Date -Format "yyyyMMdd").db
```

### Restaurar Backup

```powershell
# Substitua o banco atual pelo backup
copy integracoes_backup_20260123.db integracoes.db
```

### Ver Estrutura do Banco (Opcional)

```powershell
# Instale o SQLite (opcional)
# Download: https://www.sqlite.org/download.html

# Ou use Python
python -c "import sqlite3; conn=sqlite3.connect('integracoes.db'); print(conn.execute('SELECT * FROM clientes').fetchall())"
```

---

## 🔧 Arquivos do Projeto

```
Bi_integracao_v2/
├── bi_v2.py              # Dashboard principal (Streamlit)
├── database.py           # Funções de banco de dados
├── migrar_dados.py       # Script de migração (rodar 1x)
├── integracoes.db        # Banco de dados (criado automaticamente)
└── README.md             # Este arquivo
```

---

## 🐛 Troubleshooting

### Problema: "Erro ao conectar no banco"
**Solução:** Execute primeiro `python migrar_dados.py`

### Problema: "Cliente já existe"
**Solução:** Normal. O sistema ignora duplicatas automaticamente.

### Problema: "Nenhum dado aparece no dashboard"
**Solução:** Verifique se a migração foi executada. Adicione dados manualmente pela aba "Gerenciar".

### Problema: "Gráficos não aparecem"
**Solução:** Atualize a página (F5). Se persistir, reinstale plotly: `pip install --upgrade plotly`

---

## 🆚 Comparação com Versão Antiga

### Código

**Antes:**
```python
# 606 linhas de código complexo
# Múltiplos merges, pivots, fillna
df_merge = pd.merge(df_todos_base, df_final_int, on="Cliente", how="outer")
df_pivot = df_int.pivot_table(index='Cliente', columns='Categoria', aggfunc='size', fill_value=0)
# ... mais 50 linhas de transformações
```

**Agora:**
```python
# 300 linhas limpas e diretas
chamados = listar_chamados_abertos()  # Pronto!
stats = obter_estatisticas()  # Tudo calculado
```

### Performance

- **Antes:** ~2-3 segundos para carregar (parsing de múltiplos CSVs)
- **Agora:** ~0.1 segundo (query SQL otimizada)

### Confiabilidade

- **Antes:** Fácil corromper dados editando CSV no Excel
- **Agora:** Dados protegidos por constraints do banco

---

## 📚 Para Desenvolvedores

### Adicionar Nova Funcionalidade

1. Adicione função em `database.py`
2. Use a função em `bi_v2.py`
3. Teste localmente

### Exemplo: Adicionar campo novo

```python
# 1. Em database.py, adicione migração
with get_db() as conn:
    conn.execute("ALTER TABLE chamados ADD COLUMN prioridade TEXT")

# 2. Em bi_v2.py, use o campo
prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta"])
```

---
