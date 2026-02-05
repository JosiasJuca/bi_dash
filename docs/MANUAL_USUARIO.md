# 📋 Manual do Usuário - BI Dashboard v2.0

## 🎯 Introdução

Este manual fornece instruções completas para uso do sistema BI Dashboard, uma ferramenta profissional para gestão de integrações e chamados técnicos.

## 🚀 Primeiros Passos

### Acesso ao Sistema

1. **Executar Aplicação**: `streamlit run app.py`
2. **Acessar Interface**: Abrir navegador em `http://localhost:8502`
3. **Autenticação**: Inserir senha configurada no primeiro acesso

### Configuração Inicial

- **Primeira vez**: Sistema solicitará criação de senha
- **Recuperação**: Use as opções alternativas disponíveis na tela de login
- **Administrativo**: Acesso à configurações via sidebar

---

## 📊 Dashboard Principal

### Visão Geral
- **KPIs em Tempo Real**: Total de clientes, chamados abertos, resolvidos
- **Gráficos Interativos**: Distribuição por status e categoria
- **Filtros Dinâmicos**: Por status, cliente e classificação

### Métricas Principais
- **Total de Clientes**: Clientes ativos no sistema
- **Chamados Abertos**: Problemas pendentes de resolução
- **Taxa de Resolução**: Percentual de chamados resolvidos
- **Clientes sem Integração**: Necessitam configuração

---

## ✅ Checklist de Integrações

### Funcionalidades
- **Visualização em Grades**: Status por cliente e módulo
- **Atualização Rápida**: Click para alterar status
- **Códigos de Cores**: Verde (OK), Vermelho (Problema), Cinza (N/A)

### Módulos Monitorados
- **Batida**: Integração de ponto eletrônico
- **Escala**: Sincronização de escalas de trabalho
- **Feriados**: Calendário de feriados
- **Funcionários**: Cadastro de colaboradores
- **PDV**: Pontos de venda
- **Venda**: Transações comerciais
- **SSO**: Single Sign-On

### Como Usar
1. Selecionar cliente na lista
2. Click no status desejado para cada módulo
3. Sistema atualiza automaticamente
4. Chamados são criados/resolvidos conforme necessário

---

## 🎫 Gestão de Chamados

### Criar Novo Chamado
1. **Expandir Formulário**: "➕ Adicionar Novo Chamado"
2. **Selecionar Cliente**: Existente ou criar novo
3. **Definir Categoria**: Batida, Escala, Funcionários, etc.
4. **Status Inicial**: "Implantado com problema" ou "Implantado refazendo"
5. **Adicionar Observação**: Descrição detalhada do problema
6. **Definir Previsão**: Data estimada para resolução

### Acompanhar Chamados
- **Lista Visual**: Cards com informações completas
- **Etapas do Processo**:
  - Não iniciado
  - Em análise
  - Aguardando cliente
  - Em desenvolvimento
  - Em teste
  - Aguardando deploy
  - Concluído

### Resolver Chamado
1. **Atualizar Etapa**: Conforme progresso
2. **Adicionar Observações**: Histórico de ações
3. **Finalizar**: Descrever resolução aplicada
4. **Sistema**: Automaticamente muda status para "Normal"

---

## 📚 Base de Conhecimento

### Estrutura
- **Categorias Organizadas**: Por tipo de problema
- **Soluções Passo-a-Passo**: Instruções detalhadas
- **Imagens Ilustrativas**: Capturas de tela e diagramas

### Categorias Disponíveis
- **Problemas de Batida**: Questões de ponto eletrônico
- **Questões de Escala**: Problemas de escalas
- **Erros de Funcionários**: Sincronização de cadastros
- **Problemas de Venda**: Transações e relatórios

---

## 📈 Histórico e Relatórios

### Filtros Temporais
- **Período Personalizado**: Data início e fim
- **Filtros Adicionais**: Por cliente e status
- **Métricas do Período**: Estatísticas automáticas

### Visualizações
- **Histórico Detalhado**: Lista cronológica completa
- **Gráficos Analíticos**: Pizza e evolução temporal
- **Chamados Resolvidos**: Tempo de resolução e eficiência

### Exportação
- **Formato CSV**: Dados estruturados para análise
- **Relatórios Personalizados**: Período específico

---

## 👥 Gerenciamento Administrativo

### Funcionalidades
- **Visualizar Todas as Abas**: Acesso unificado
- **Estatísticas Gerais**: Visão executiva
- **Controle de Sistema**: Configurações avançadas

### Acesso
- Apenas com autenticação válida
- Sidebar com configurações
- Interface administrativa completa

---

## 🔧 Configurações Avançadas

### Autenticação
- **Múltiplas Senhas**: Sistema flexível
- **Recuperação**: Opções alternativas
- **Segurança**: Validação robusta

### Personalização
- **Temas**: Cores e estilos
- **Filtros Padrão**: Configurações preferidas
- **Notificações**: Alertas personalizados

---

## ❓ Suporte e Dúvidas

### Solução de Problemas
1. **Verificar Conexão**: Internet e servidor
2. **Recarregar Página**: F5 ou Ctrl+R
3. **Limpar Cache**: Configurações do navegador
4. **Contato**: Equipe de suporte técnico

### Dicas de Performance
- **Navegadores Recomendados**: Chrome, Firefox, Edge
- **Filtros**: Use filtros para melhor performance
- **Atualizações**: Mantenha dados atualizados

