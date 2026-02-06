# 📊 BI Dashboard - Sistema de Gestão de Integrações

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![Streamlit Version](https://img.shields.io/badge/streamlit-1.28%2B-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Produção-brightgreen.svg)]()

## 🎯 Sobre o Projeto

Sistema profissional de **Business Intelligence** para gestão completa de integrações e chamados técnicos. Desenvolvido com arquitetura modular moderna usando **Streamlit** e **SQLite**, oferece interface intuitiva para dashboards analíticos, controle de clientes e gerenciamento eficiente de chamados.

**🚀 Versão 2.0** - Completamente reestruturada com arquitetura profissional e desenvolvimento colaborativo.

### ✨ Principais Funcionalidades

- **📊 Dashboard Analítico**: Métricas em tempo real, gráficos interativos e KPIs empresariais
- **✅ Checklist Inteligente**: Controle visual e automático do status de cada integração
- **🎫 Gestão de Chamados**: Ciclo completo de abertura, acompanhamento e resolução com SLA
- **📚 Histórico e Relatórios**: Rastreabilidade completa com exportação e análise temporal
- **📖 Base de Conhecimento**: Passo a passo estruturado para resolução de problemas
- **👥 Gerenciamento de Equipe**: Controle de acesso e distribuição de responsabilidades
- **🔒 Autenticação Robusta**: Sistema seguro com controle granular de permissões

## 🏗️ Arquitetura

```
bi_dash/
├── app.py                   # Aplicação principal Streamlit
├── requirements.txt         # Dependências do projeto
├── src/                     # Código fonte modular
│   ├── components/          # Componentes UI reutilizáveis
│   │   ├── dashboard.py     # Dashboard principal e KPIs
│   │   ├── charts.py        # Gráficos e visualizações
│   │   ├── tables.py        # Tabelas e listagens
│   │   ├── regras.py        # Base de conhecimento
│   │   ├── chamados.py      # Gestão de chamados ativos
│   │   ├── historico.py     # Histórico e relatórios
│   │   ├── gerenciamento.py # Painel administrativo
│   │   └── checklist.py     # Checklist de integrações
│   ├── database/            # Camada de persistência
│   │   ├── models.py        # Modelos e esquemas SQLite
│   │   └── operations.py    # Operações CRUD e consultas
│   └── utils/               # Utilitários compartilhados
│       ├── constants.py     # Constantes e configurações
│       ├── helpers.py       # Funções auxiliares
│       └── auth.py          # Sistema de autenticação
├── tests/                   # Suíte de testes automatizados
├── docs/                    # Documentação técnica
├── img/                     # Imagens e recursos visuais
└── scripts/                 # Scripts úteis
```

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.9 ou superior
- Git

### 📦 Instalação Local

```bash
# 1. Navegar para o diretório do projeto
cd bi_dash

# 2. Criar ambiente virtual (recomendado)
python -m venv venv

# 3. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Executar aplicação
streamlit run app.py
```

### 🔧 Configuração de Senha

O sistema oferece formas de configurar a senha administrativa:

1. **Interface Web** (recomendado para desenvolvimento):
   - Use a sidebar para definir senha temporária

2. **Variável de Ambiente** (para produção):
   ```bash
   set DASH_SENHA=suasenhasecreta
   ```

3. **Fallback Padrão** (apenas para testes):
   - Senha: `admin123`

## 📱 Como Usar

### 🏠 Dashboard Principal
- **Métricas**: Total de clientes, chamados abertos/resolvidos, taxa de implantação
- **Gráficos**: Distribuição por status, chamados por categoria
- **Filtros**: Status, cliente, responsável
- **Tabelas**: Chamados críticos e checklist de integração

### 🎫 Gerenciamento de Chamados
1. **Criar Chamado**: Cliente + Status + Categoria + Observações
2. **Acompanhar**: Etapas do ciclo de vida (Não iniciado → Resolvido)
3. **Resolver**: Documentar solução e fechar chamado
4. **Reabrir**: Se necessário, reativar chamado resolvido

### ✅ Checklist de Integração
- **Status Visual**: ✓ (OK), ✗ (Problema), 🛠️ (Em Construção), N/A
- **Categorias**: Batida, Escala, Feriados, Funcionários, PDV, Venda, SSO
- **Gerenciamento**: Adicionar/editar clientes e status das integrações

### 📖 Base de Conhecimento
- **Fluxo de Investigação**: Site → SFTP → Conformidade
- **Formatos de Arquivo**: AFD, AFDT, Tipo Moavi
- **Templates**: E-mails para notificação de problemas
- **Documentação Visual**: Screenshots e exemplos

## 🛠️ Desenvolvimento

### 🤝 Contribuindo

1. **Fork** o projeto
2. **Clone** seu fork: `git clone https://github.com/SEUUSERNAME/bi-dashboard.git`
3. **Branch**: `git checkout -b feature/nova-funcionalidade`
4. **Commit**: `git commit -m 'feat: adicionar nova funcionalidade'`
5. **Push**: `git push origin feature/nova-funcionalidade`
6. **Pull Request**: Abra um PR com descrição detalhada

### 📋 Padrões de Código

- **Nomenclatura**: `snake_case` para funções e variáveis
- **Docstrings**: Documentar todas as funções públicas
- **Imports**: Organizados em ordem (stdlib, third-party, local)
- **Commits**: Seguir [Conventional Commits](https://conventionalcommits.org/)

### 🧪 Testes

```bash
# Verificar sintaxe
python -m py_compile app.py

# Executar aplicação localmente
streamlit run app.py

# Verificar linting (opcional)
flake8 . --max-line-length=127
```

### 🚢 Deploy

#### Deploy no Streamlit Cloud
1. Conecte seu repositório GitHub
2. Configure as variáveis de ambiente
3. Deploy automático a cada push na main

#### Deploy no Heroku
```bash
# Adicionar arquivos de configuração
echo "streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
echo "python-3.9.16" > runtime.txt

# Deploy
git add .
git commit -m "feat: preparar para deploy"
git push heroku main
```

## 📊 Métricas e Analytics

### KPIs Principais
- **Taxa de Implantação**: % de clientes com integração completa
- **Tempo Médio de Resolução**: Eficiência na resolução de chamados
- **Distribuição por Status**: Visão geral da saúde das integrações
- **Chamados por Responsável**: Balanceamento de carga de trabalho

### Relatórios Disponíveis
- Chamados por período
- Clientes sem integração
- Histórico de resoluções
- Performance por categoria

## 🔒 Segurança

- **Autenticação**: Controle de acesso à área administrativa
- **Validação**: Sanitização de entradas do usuário
- **Auditoria**: Log de todas as ações importantes
- **Backup**: Funcionalidade de download do banco de dados

## 📞 Suporte

### 🐛 Problemas e Bugs
- Abra uma [Issue](../../issues/new) descrevendo o problema
- Use o template de bug report
- Inclua prints quando possível

### 💡 Sugestões e Melhorias
- Abra uma [Feature Request](../../issues/new)
- Descreva o problema que a feature resolve
- Inclua mockups se tiver

### 📖 Documentação
- [Guia de Contribuição](docs/CONTRIBUTING.md)
- [Documentação da API](docs/API.md)
- [Guia de Deploy](docs/DEPLOYMENT.md)

## 🏆 Equipe

### 👨‍💻 Desenvolvedores
- **[Seu Nome]** - Desenvolvedor Principal
- **[Nome do Colega]** - Desenvolvedor

### 🙏 Agradecimentos
- Comunidade Streamlit
- Equipe de Integrações
- Colaboradores do projeto

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Links Úteis

- [Documentação Streamlit](https://docs.streamlit.io)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Plotly Python](https://plotly.com/python/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

<p align="center">
  Desenvolvido com ❤️ pela Equipe de Integrações<br>
  <strong>BI Dashboard v2.0</strong> - Sistema Profissional de Gestão
</p>