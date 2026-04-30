# 📦 SisStock - Gestão de Estoque PEPS & PDV

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)

O **SisStock** é um sistema desktop completo de gerenciamento de estoque e Frente de Caixa (PDV), projetado para atender pequenos comércios e e-commerces. O grande diferencial deste projeto é a implementação da lógica contábil **PEPS** (Primeiro a Entrar, Primeiro a Sair), garantindo que o custo das mercadorias vendidas e o lucro real sejam calculados com precisão cirúrgica.

## 🚀 Funcionalidades Principais

* **Lógica PEPS (FIFO):** Gestão de estoque baseada em lotes. O sistema rastreia o custo exato de cada entrada e abate o estoque começando pelo lote mais antigo.
* **Frente de Caixa (PDV):** Interface ágil para vendas com suporte a leitor de código de barras. Permite aplicar descontos e taxas (entrega/cartão) no momento da finalização.
* **Carrinho de Vendas:** Sistema de conferência antes da baixa, permitindo adicionar múltiplos itens e visualizar o total da venda em tempo real.
* **Entrada de Mercadorias com Conferência:** Área de transição para novos lotes, evitando erros de digitação antes da gravação definitiva no banco de dados.
* **Dashboard Inteligente:** Métricas instantâneas sobre capital imobilizado (estoque), produtos zerados e faturamento total.
* **Segurança de Dados:** Banco de dados SQLite local, garantindo que as informações da empresa fiquem seguras no computador do usuário.

## 🛠️ Tecnologias e Arquitetura

* **Linguagem:** Python 3.10+
* **Interface:** CustomTkinter para uma experiência moderna (Dark/Light mode).
* **Banco de Dados:** SQLite3 com relacionamentos entre Catálogo e Lotes.
* **Infraestrutura:** Empacotamento via PyInstaller para geração de executável standalone.

## 📂 Como Executar

### Para Usuários
1. Vá na aba **Releases** deste repositório.
2. Baixe o arquivo `SisStock.exe`.
3. Execute e comece a gerenciar seu estoque!

### Para Desenvolvedores
1. Clone o repositório: `git clone https://github.com/CarlosDecker/SisStock.git`
2. Instale as dependências: `pip install customtkinter`
3. Execute o script principal: `python main.py`

## 📝 Autor

Desenvolvido por **Carlos Decker**.
