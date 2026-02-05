# 🤝 Contribuindo para o BI Dashboard v2.0

Obrigado pelo seu interesse em contribuir! Este documento fornece diretrizes para colaboração no desenvolvimento do sistema.

## 🎥 Visão Geral

O BI Dashboard utiliza uma arquitetura modular profissional com Streamlit e SQLite. Todas as contribuições devem seguir os padrões estabelecidos e passar pelo processo de code review.

### 📜 Documentação Obrigatória
Antes de contribuir, leia:
- [`DESENVOLVIMENTO.md`](DESENVOLVIMENTO.md) - Guia técnico detalhado
- [`ARQUITETURA.md`](ARQUITETURA.md) - Estrutura do sistema
- [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) - Funcionalidades do sistema

## 🚀 Como Contribuir

### 1. **Fork e Clone**
```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEUUSERNAME/bi-dashboard.git
cd bi-dashboard
```

### 2. **Configurar Ambiente de Desenvolvimento**
```bash
# Criar e ativar ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
copy .env.example .env
# Edite o .env conforme necessário

# Verificar se tudo funciona
streamlit run app.py
```

### 3. **Criar Branch**
```bash
# Sempre partir da main atualizada
git checkout main
git pull origin main

# Criar branch descritiva
git checkout -b feature/nome-da-funcionalidade
# ou
git checkout -b fix/correcao-do-problema
# ou  
git checkout -b docs/atualizacao-documentacao
```

### 4. **Desenvolvimento**
- Faça suas alterações
- Teste localmente: `streamlit run app.py`
- Siga os padrões de código existentes
- Adicione comentários quando necessário

### 5. **Commit e Push**
```bash
# Adicionar arquivos
git add .

# Commit com mensagem descritiva
git commit -m "feat: adicionar gráfico de vendas por região

- Implementar gráfico de pizza para vendas
- Adicionar filtro por período  
- Incluir tabela de top vendedores

Closes #15"

# Push da branch
git push origin feature/nome-da-funcionalidade
```

### 6. **Pull Request**
- Abra PR no GitHub
- Preencha o template completamente
- Aguarde review e feedback

## 📝 Padrões de Código

### **Convenções de Nomenclatura:**
- **Variáveis:** `snake_case` (ex: `dados_cliente`)
- **Funções:** `snake_case` (ex: `obter_estatisticas`)
- **Classes:** `PascalCase` (ex: `DatabaseManager`)
- **Constantes:** `UPPER_SNAKE_CASE` (ex: `STATUS_OPTIONS`)

### **Estrutura de Arquivos:**
```python
# Imports organizados
import streamlit as st
import pandas as pd
from datetime import date

# Imports locais
from src.database.operations import obter_dados
from src.utils.helpers import formatar_data

# Constantes
OPCOES_STATUS = [...]

# Funções
def minha_funcao():
    """Docstring explicando a função."""
    pass

# Código principal
if __name__ == "__main__":
    main()
```

### **Comentários:**
```python
# ==================== SEÇÃO PRINCIPAL ====================
# Comentário explicativo sobre o bloco

def funcao_complexa():
    """
    Descrição da função.
    
    Args:
        param1: Descrição do parâmetro
        
    Returns:
        Descrição do retorno
    """
    # Comentário inline quando necessário
    resultado = fazer_algo()
    return resultado
```

## 📋 Padrões de Commit

Use o formato: `tipo: descrição`

### **Tipos:**
- `feat:` Nova funcionalidade
- `fix:` Correção de bug  
- `docs:` Mudanças na documentação
- `style:` Formatação, espaços em branco, etc.
- `refactor:` Refatoração sem mudança de funcionalidade
- `test:` Adicionar ou modificar testes
- `chore:` Tarefas de manutenção, build, dependências

### **Exemplos:**
```bash
feat: adicionar filtro por data no dashboard
fix: corrigir erro de autenticação
docs: atualizar README com instruções de instalação
style: formatar código seguindo PEP8
refactor: extrair lógica de gráficos para módulo separado
test: adicionar testes para função de estatísticas  
chore: atualizar dependências do Streamlit
```

## 🧪 Testes

### **Executar Testes Locais:**
```bash
# Verificar sintaxe
python -m py_compile app.py
python -m py_compile src/database/*.py

# Executar aplicação
streamlit run app.py

# Verificar se não há erros no console
# Testar todas as funcionalidades principais
```

### **Checklist de Teste:**
- [ ] Aplicação inicia sem erros
- [ ] Dashboard carrega todos os gráficos
- [ ] Autenticação funciona
- [ ] Checklist permite adicionar/editar clientes
- [ ] Chamados podem ser criados e resolvidos
- [ ] Histórico exibe dados corretos
- [ ] Regras e documentação aparecem
- [ ] Responsivo em diferentes tamanhos de tela

## 🔍 Process de Review

### **O que Verificamos:**
1. **Funcionalidade:** Funciona conforme esperado?
2. **Código:** Segue padrões e está limpo?
3. **Performance:** Não degrada a aplicação?
4. **Segurança:** Não introduz vulnerabilidades?
5. **UX:** Melhora a experiência do usuário?

### **Como Responder a Feedback:**
```bash
# Fazer correções solicitadas
git add .
git commit -m "fix: aplicar feedback do code review"
git push origin sua-branch
```

## 🚨 Diretrizes Importantes

### **❌ Não Fazer:**
- Commits diretos na branch `main`
- Senhas hardcoded no código
- Arquivos grandes (>10MB) no repositório
- Mudanças que quebram funcionalidades existentes
- Commits sem testes locais

### **✅ Sempre Fazer:**
- Testar localmente antes do commit
- Usar mensagens de commit descritivas
- Manter PRs pequenos e focados
- Documentar mudanças significativas
- Respeitar o code review

## 📞 Precisa de Ajuda?

- 🐛 **Bug encontrado?** Abra uma [Issue](../../issues/new)
- 💡 **Sugestão?** Abra uma [Feature Request](../../issues/new)
- 💬 **Dúvidas?** Comente no PR ou Issue relacionada

## 🏆 Reconhecimento

Contribuidores são listados no README.md. Obrigado por ajudar a melhorar o projeto!