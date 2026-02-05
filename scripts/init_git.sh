# Inicialização do Git Repository

echo "# 📊 BI Dashboard - Sistema de Gestão de Integrações" > README.md
git init
git add .
git commit -m "feat: estrutura inicial do projeto profissional

- Arquitetura modular com separação de responsabilidades
- Sistema de autenticação seguro
- Componentes reutilizáveis
- Templates para GitHub (PRs, Issues)  
- Pipeline CI/CD
- Documentação completa
- Testes básicos
- Configuração de ambiente

BREAKING CHANGE: Reestruturação completa do projeto"
git branch -M main
git remote add origin https://github.com/SEUUSERNAME/bi-dashboard.git
git push -u origin main