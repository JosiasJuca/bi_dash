# 🏗️ Documentação Técnica - Arquitetura

## 📋 Visão Geral

O BI Dashboard v2.0 foi completamente reestruturado usando uma arquitetura modular profissional que segue as melhores práticas de desenvolvimento Python e Streamlit.

## 🏛️ Arquitetura do Sistema

### Padrão de Arquitetura
- **MVC Adaptado**: Model-View-Controller para Streamlit
- **Separação de Responsabilidades**: Cada módulo tem função específica
- **Componentização**: Interface dividida em componentes reutilizáveis
- **Camada de Dados**: Abstração completa do banco SQLite

### Estrutura de Diretórios

```
src/
├── components/     # 🎨 Componentes de Interface
├── database/       # 🗄️ Camada de Persistência  
└── utils/          # 🛠️ Utilitários Compartilhados
```

---

## 🎨 Componentes de Interface

### `dashboard.py` - Dashboard Principal
**Responsabilidade**: Renderização de KPIs, métricas e visão geral

**Funções Principais**:
- `renderizar_dashboard()`: Entry point principal
- `renderizar_metricas_kpi()`: Exibição de métricas em tempo real
- `renderizar_secao_chamados_problemas()`: Lista de problemas ativos

**Dependências**:
- `src.database.operations.obter_estatisticas()`
- `src.components.charts` para visualizações
- `src.components.tables` para listagens

### `charts.py` - Gráficos e Visualizações
**Responsabilidade**: Geração de gráficos interativos com Plotly

**Funções Principais**:
- `renderizar_grafico_status()`: Distribuição por status
- `renderizar_grafico_categorias()`: Análise por categoria
- `gerar_grafico_pizza()`: Gráficos de pizza personalizáveis

**Tecnologia**: Plotly Express para interatividade

### `tables.py` - Tabelas e Listagens
**Responsabilidade**: Renderização de dados tabulares

**Funções Principais**:
- `renderizar_tabela_chamados_problemas()`: Chamados ativos
- `renderizar_tabela_checklist()`: Status de integrações
- Filtros dinâmicos e paginação

### `chamados.py` - Gestão de Chamados
**Responsabilidade**: CRUD completo de chamados técnicos

**Funções Principais**:
- `renderizar_chamados()`: Interface principal
- `renderizar_formulario_novo_chamado()`: Criação
- `renderizar_card_chamado()`: Visualização individual
- `processar_novo_chamado()`: Lógica de criação

**Fluxo de Estados**:
1. Não iniciado → Em análise → Em desenvolvimento → Concluído

### `checklist.py` - Checklist de Integrações
**Responsabilidade**: Grid interativo para controle de integrações

**Funções Principais**:
- `renderizar_checklist()`: Grid principal
- `renderizar_controles_checklist()`: Ações em lote
- Atualização automática de chamados baseado em status

### `historico.py` - Histórico e Relatórios
**Responsabilidade**: Análise temporal e relatórios

**Funções Principais**:
- `renderizar_historico()`: Interface com filtros temporais
- `renderizar_estatisticas_periodo()`: Métricas por período
- `renderizar_graficos_historico()`: Visualizações analíticas
- `exportar_relatorio()`: Geração de CSV

### `gerenciamento.py` - Painel Administrativo
**Responsabilidade**: Acesso unificado para administradores

**Funções Principais**:
- `renderizar_gerenciamento()`: Dashboard administrativo
- Integração com todas as abas do sistema
- Controles avançados e estatísticas gerais

### `regras.py` - Base de Conhecimento
**Responsabilidade**: Documentação estruturada de soluções

**Estrutura**:
- Categorias organizadas por tipo de problema
- Soluções passo-a-passo com imagens
- Sistema de busca e navegação

---

## 🗄️ Camada de Persistência

### `models.py` - Modelos de Dados
**Responsabilidade**: Definição de esquemas e estruturas

**Entidades Principais**:
```sql
clientes: id, nome, ativo, classificacao, atualizado_em
chamados: id, cliente_id, status, categoria, observacao, data_abertura, data_resolucao
checklist: id, cliente_id, batida, escala, feriados, funcionarios, pdv, venda, sso
```

### `operations.py` - Operações CRUD
**Responsabilidade**: Interface com banco SQLite

**Categorias de Funções**:

#### Gestão de Clientes
- `listar_clientes()`: Listagem completa
- `buscar_cliente_por_nome()`: Busca específica
- `adicionar_cliente()`: Criação

#### Gestão de Chamados
- `listar_chamados_problemas()`: Chamados ativos
- `adicionar_chamado()`: Criação
- `atualizar_etapa_chamado()`: Progressão
- `excluir_chamado()`: Remoção

#### Checklist
- `obter_checklist_cliente()`: Status por cliente
- `atualizar_checklist_item()`: Mudança de status
- `criar_chamado_automatico()`: Geração automática

#### Estatísticas
- `obter_estatisticas()`: KPIs gerais
- `obter_estatisticas_periodo()`: Métricas temporais
- `listar_historico_completo()`: Dados históricos

#### Gestão de Banco
- `init_db()`: Inicialização
- `get_db()`: Context manager com transações

---

## 🛠️ Utilitários Compartilhados

### `constants.py` - Constantes do Sistema
**Conteúdo**:
- `STATUS_OPTIONS`: Lista de status possíveis
- `CATEGORIAS`: Categorias de chamados
- `ETAPAS_CHAMADO`: Fluxo de desenvolvimento
- `APP_CONFIG`: Configurações Streamlit
- `CSS_STYLES`: Estilos customizados

### `helpers.py` - Funções Auxiliares
**Funções Utilitárias**:
- `status_badge()`: Geração de badges coloridos
- `obter_estilos_etapa()`: Cores por etapa
- `exibir_mensagens_persistentes()`: Sistema de notificações

### `auth.py` - Sistema de Autenticação
**Responsabilidade**: Controle de acesso seguro

**Funções**:
- `verificar_autenticacao()`: Validação de sessão
- `renderizar_tela_login()`: Interface de login
- `renderizar_configuracao_senha()`: Gerenciamento de senhas

---

## 🔄 Fluxo de Dados

### 1. **Inicialização**
```
app.py → configurar_pagina() → init_db() → main()
```

### 2. **Autenticação**
```
auth.verificar_autenticacao() → renderizar_tela_login() → session_state
```

### 3. **Dashboard**
```
database.obter_estatisticas() → components.dashboard → charts + tables
```

### 4. **Gestão de Chamados**
```
User Input → chamados.processar_novo_chamado() → database.adicionar_chamado()
```

### 5. **Checklist**
```
User Click → checklist.atualizar_item() → database.criar_chamado_automatico()
```

---

## 📊 Padrões de Desenvolvimento

### Convenções de Nomenclatura
- **Funções**: `snake_case` com verbos descritivos
- **Componentes**: `renderizar_*()` para UI
- **Database**: `obter_*()`, `listar_*()`, `adicionar_*()`
- **Constantes**: `UPPER_CASE`

### Estrutura de Funções
```python
def renderizar_componente():
    """Docstring explicativa."""
    # 1. Obter dados
    dados = database.obter_dados()
    
    # 2. Processar
    dados_processados = processar(dados)
    
    # 3. Renderizar UI
    st.subheader("Título")
    for item in dados_processados:
        # render item
```

### Gestão de Estado
- **Session State**: Para dados temporários
- **Database**: Para persistência
- **Constants**: Para configurações

### Tratamento de Erros
```python
try:
    # operação
    resultado = operacao_database()
    st.success("✅ Sucesso")
except Exception as e:
    st.error(f"❌ Erro: {e}")
```

---

## 🔧 Configuração e Deploy

### Sistema de Autenticação
O sistema usa múltiplas formas de configuração de senha:
- Interface sidebar para desenvolvimento
- Variável de ambiente `DASH_SENHA` para produção
- Fallback padrão para testes

### Dependências Principais
- **streamlit**: Framework web
- **sqlite3**: Banco de dados (built-in Python)
- **plotly**: Visualizações interativas
- **pandas**: Manipulação de dados

---

## 🚀 Performance e Otimização

### Estratégias Implementadas
- **Context Managers**: Gestão automática de conexões
- **Lazy Loading**: Componentes carregados sob demanda
- **Caching**: Session state para dados temporários
- **Consultas Otimizadas**: Índices e joins eficientes

### Monitoramento
- **Logs**: Erros e operações críticas
- **Métricas**: Tempo de resposta das consultas
- **Recursos**: Uso de memória e CPU

---

*Versão: 2.0 | Documentação Técnica | Fevereiro 2026*