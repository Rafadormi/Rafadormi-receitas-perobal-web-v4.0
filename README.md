# 🏥 ReceitasPerobal v4.0

**Sistema de Receitas Médicas - Secretaria Municipal de Saúde de Perobal**

Uma aplicação web moderna e offline para gestão de pacientes, medicamentos e geração de receitas médicas em PDF.

## ✨ Novidades da Versão 4.0

- 🖱️ **Botão de Fechar/Sair** no canto superior direito
- 🖥️ **Script de Atalho** para área de trabalho
- 🚀 **Inicialização Automática** do navegador
- 💾 **Confirmação de Saída** com encerramento do servidor
- 📱 **Interface Responsiva** aprimorada

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.8 ou superior
- Windows 10/11 (recomendado)

### Instalação Rápida

1. **Extraia** o arquivo `receitas-perobal-web-v4.0.zip`
2. **Duplo clique** em `Iniciar_ReceitasPerobal.bat`
3. **Aguarde** o sistema inicializar automaticamente
4. **Acesse** http://localhost:5001 (abre automaticamente)

### Criar Atalho na Área de Trabalho

Consulte o arquivo `COMO_CRIAR_ATALHO.md` para instruções detalhadas.

## 📋 Funcionalidades

### 👥 Gestão de Pacientes
- ✅ Cadastro com nome, CPF e data de nascimento
- ✅ Busca e edição de pacientes
- ✅ Importação/exportação CSV
- ✅ Validação de dados

### 💊 Gestão de Medicamentos
- ✅ Cadastro com denominação, concentração e apresentação
- ✅ Lista pré-populada com medicamentos comuns
- ✅ Importação/exportação CSV
- ✅ Busca e filtros

### 📄 Geração de Receitas
- ✅ Seleção de 1 a 6 receitas mensais
- ✅ Data inicial editável (+30 dias automático)
- ✅ Lista suspensa de posologia (1x ao dia, 2x ao dia, etc.)
- ✅ Instruções opcionais
- ✅ Supressão de campos vazios
- ✅ PDF consolidado (uma página por receita)
- ✅ Abertura automática para impressão
- ✅ Layout oficial da SMS Perobal

### 🔧 Sistema
- ✅ 100% offline (banco SQLite local)
- ✅ Interface web moderna
- ✅ Backup/restauração de dados
- ✅ Botão de fechar com confirmação
- ✅ Script de atalho para área de trabalho

## 🖥️ Como Usar

### Iniciar o Sistema
1. **Duplo clique** no atalho da área de trabalho
2. **Ou execute** `Iniciar_ReceitasPerobal.bat`
3. **Aguarde** a mensagem "Sistema iniciando..."
4. **O navegador abrirá automaticamente**

### Fechar o Sistema
1. **Clique no botão ✕** no canto superior direito
2. **Confirme** quando perguntado
3. **O servidor será encerrado automaticamente**

## 📁 Estrutura do Projeto

```
receitas-perobal-web-v4.0/
├── src/                          # Código-fonte
│   ├── static/                   # Interface web
│   ├── models/                   # Modelos de dados
│   ├── routes/                   # APIs REST
│   ├── utils/                    # Utilitários (PDF)
│   └── main.py                   # Servidor Flask
├── venv/                         # Ambiente virtual Python
├── Iniciar_ReceitasPerobal.bat   # Script de inicialização
├── COMO_CRIAR_ATALHO.md          # Instruções de atalho
└── README.md                     # Este arquivo
```

## 🔧 Dependências

- Flask 3.0+
- Flask-SQLAlchemy 3.0+
- Flask-CORS 4.0+
- ReportLab 4.0+
- Pandas 2.0+

## 📞 Suporte

**Desenvolvido para:**
Secretaria Municipal de Saúde de Perobal
Rua Jaracatiá, 1060 - Perobal/PR
CEP: 87538-000

**Versão:** 4.0
**Data:** Dezembro 2024
**Compatibilidade:** Windows 10/11, Python 3.8+

