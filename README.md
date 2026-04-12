# 📘 Assistente de Estudos Inteligente - Modern Dashboard

> [!NOTE]
> Este repositório é o **Frontend Moderno** do sistema de estudos de inglês. Para o servidor de processamento de inteligência artificial e transcrição, consulte o repositório do **[Backend - Agente de Estudos de Inglês](https://github.com/RenanFerreira0023/backend-agente-estudos-ingles)**.

Este projeto agora conta com uma interface gráfica (GUI) moderna e intuitiva que centraliza todo o fluxo de estudos, desde a seleção do vídeo até a leitura do relatório final.

## ✨ Novidades da Interface
- **🚀 Dashboard Moderno**: Visual limpo com tema escuro e barra de progresso.
- **🖥️ Terminal de Logs Integrado**: Acompanhe o que o robô está fazendo em tempo real sem precisar olhar para o console.
- **📂 Seletor Nativo**: Escolha seus vídeos usando o explorador de arquivos padrão do Windows.
- **🛠️ Ferramentas Rápidas**: Botão para apagar caches (Mock) e abrir o relatório com um clique.

---

## 🚀 Como Funciona?

1.  **Transcrição**: O sistema extrai o áudio e envia para um servidor remoto com GPU.
2.  **Processamento**: O texto é processado por um Agente de IA que organiza o conteúdo.
3.  **Resultado**: Um arquivo `relatorio_aula.md` é gerado e pode ser aberto direto pelo Dashboard.

---

## 🛠️ Pré-requisitos

1.  **Python 3.10+** instalado.
2.  **FFmpeg**: Necessário para extrair o áudio dos vídeos.
    *   *No Windows*: Baixe o executável e adicione à sua variável de ambiente PATH.
3.  **Servidor Backend**: O backend precisa estar rodando em uma máquina da sua rede.

---

## ⚙️ Configuração Inicial

1.  **Crie e ative um ambiente virtual:**
    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```
2.  **Instale as dependências:**
    ```powershell
    pip install -r requirements.txt
    ```
3.  **Configure o IP do Servidor**:
    Edite o arquivo `config.json` ou o arquivo `.env` na raiz do projeto:
    ```json
    {
      "LLM_API_BASE_URL": "http://192.168.0.X:8000"
    }
    ```

---

## 📖 Como Usar

### 🖥️ Opção 1: Interface Gráfica (Recomendado)
A forma mais fácil e completa de usar o assistente.
```powershell
python gui_main.py
```
- Clique em **NOVA TRANSCRIÇÃO** para escolher o vídeo.
- Acompanhe o progresso na barra azul.
- Ao final, clique em **ABRIR RELATÓRIO**.

### ⌨️ Opção 2: Linha de Comando (Legacy)
Se preferir o terminal puro:
```powershell
python main.py
```

---

## 🧹 Gestão de Cache e Mocks

No Dashboard, você tem botões dedicados para gerenciar esses arquivos:

*   **LIMPAR MOCK**: Apaga o arquivo `transcricao_mock.txt`. Use isso quando quiser processar um vídeo novo ignorando a última transcrição salva.
*   **ABRIR RELATÓRIO**: Abre instantaneamente o arquivo `relatorio_aula.md` no seu editor padrão.

---

## 📂 Estrutura de Scripts

*   `gui_main.py`: A nova interface moderna (KivyMD).
*   `main.py`: Orquestrador via linha de comando.
*   `scripts/transcrever_api.py`: Gerencia a comunicação com a API de transcrição.
*   `scripts/gerar_relatorio_api.py`: Envia o texto para a IA gerar o relatório.

> [!IMPORTANT]
> O servidor backend ([Repositório Backend](https://github.com/RenanFerreira0023/backend-agente-estudos-ingles)) precisa estar ligado e acessível para que as transcrições funcionem.