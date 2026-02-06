#!/bin/bash
# Inicialização do Git Repository

echo "📊 Inicializando repositório Git..."

# Verifica se já é um repositório git
if [ -d ".git" ]; then
    echo "⚠️  Repositório Git já existe"
    echo "✅ Status atual:"
    git status --short
else
    echo "🚀 Criando novo repositório Git..."
    git init
    git add .
    git commit -m "feat: projeto BI Dashboard - Sistema de Gestão de Integrações
    
- Dashboard analítico com KPIs e gráficos
- Sistema de gestão de chamados técnicos
- Base de conhecimento integrada
- Checklist de integrações
- Sistema de autenticação
- Arquitetura modular profissional"
    git branch -M main
    echo "✅ Repositório criado com sucesso"
    echo "📝 Para conectar a um repositório remoto:"
    echo "   git remote add origin https://github.com/SEU_USUARIO/bi-dashboard.git"
    echo "   git push -u origin main"
fi