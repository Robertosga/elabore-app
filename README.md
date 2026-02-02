#  Sistema de Orçamentos & O.S. - Elabore Toldos

Sistema web desenvolvido em Python com a biblioteca **Streamlit** para automação de orçamentos e ordens de serviço da empresa **Elabore Toldos**.

## 📋 Funcionalidades

- 🔐 **Acesso Restrito:** Proteção por senha via Streamlit Secrets.
- 🛠 **Multi-Serviços:** Adição dinâmica de múltiplos itens em um único orçamento (botão +).
- 💰 **Cálculos Automáticos:** Soma total, aplicação de desconto, cálculo de entrada e valor restante.
- 📄 **Geração de PDF:** Exportação profissional com logo da empresa, dados do cliente e condições de pagamento.
- 🇧🇷 **Formatação BR:** Valores monetários exibidos no padrão brasileiro (R$ 1.000,00).

## 🛠️ Tecnologias Utilizadas

- [Python 3.12+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) - Interface Web.
- [FPDF](https://pyfpdf.github.io/fpdf2/) - Geração de documentos PDF.
- [Pillow (PIL)](https://python-pillow.org/) - Tratamento de imagens e logomarcas.

## 🚀 Como Rodar o Projeto

### 1. Requisitos
Certifique-se de ter o Python instalado. Instale as bibliotecas necessárias:
```bash
pip install streamlit fpdf Pillow

## ⚙️ Configuração da Senha (IMPORTANTE)
Como o sistema possui proteção de acesso, você deve configurar a senha no **Streamlit Cloud**:
1. Vá em **Settings** (Configurações) no painel do seu App.
2. Acesse a aba **Secrets**.
3. Cole o seguinte código e salve:
   ```toml
   [credentials]
   password = "SUA_SENHA_AQUI"
