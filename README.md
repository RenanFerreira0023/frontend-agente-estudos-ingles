# 📘 Assistente de Estudos Inteligente - Cliente (Frontend)

> [!NOTE]
> Este repositório é parte integrante do sistema de estudos de inglês. Para o servidor de processamento de inteligência artificial e transcrição, consulte o repositório do **[Backend - Agente de Estudos de Inglês](https://github.com/RenanFerreira0023/backend-agente-estudos-ingles)**.

Este projeto é a interface de linha de comando (CLI) que atua como cliente para o sistema de estudos. Ele trabalha em conjunto com o backend para processar as transcrições e gerar os relatórios utilizando GPU e LLMs.

## 🚀 Como Funciona?

1.  **Transcrição**: O projeto envia o áudio para um servidor remoto com GPU para uma transcrição rápida.
2.  **Processamento**: O texto transcrito é enviado para um Agente de IA que organiza o conteúdo em tópicos facilitando o estudo.
3.  **Resultado**: Um arquivo `relatorio_aula.md` é gerado com todo o conteúdo formatado.

---

## 🛠️ Pré-requisitos

Para rodar este projeto, você precisará de:

1.  **Python 3.10+** instalado.
2.  **FFmpeg**: Necessário para extrair o áudio dos vídeos.
    *   *No Windows*: Você pode baixar o executável e adicionar à sua variável de ambiente PATH.
3.  **Uma API Remota**: O projeto está configurado para se conectar a um servidor de transcrição e geração de texto (configurado no IP da sua rede local).

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
    Edite o arquivo `config.json` ou o arquivo `.env` na raiz do projeto com o endereço IP do seu servidor de IA:
    ```json
    {
      "LLM_API_BASE_URL": "http://192.168.0.X:8000"
    }
    ```

---

## 📖 Como Usar

Existem duas formas de iniciar o assistente:

### Opção 1: Seleção via Janela (Mais fácil)
Basta rodar o comando abaixo e uma janela de seleção de arquivos abrirá:
```powershell
python main.py
```

### Opção 2: Linha de Comando (Direto)
Passe o caminho do vídeo diretamente no comando:
```powershell
python main.py "C:/Caminho/Para/Seu/Video.mp4"
```

---

## 🧹 Arquivos de Cache e Mock

Para agilizar os testes e economizar processamento, o sistema gera alguns arquivos temporários:

*   **`mock_audio_extraido.m4a`**: O sistema extrai apenas o áudio para enviar à API. Se você quiser processar um vídeo novo, certifique-se de apagar ou renomear este arquivo se ele for de uma aula anterior.
*   **`transcricao_mock.txt`**: Salva a última transcrição feita. Se este arquivo existir, o `main.py` irá usá-lo em vez de chamar a API novamente (útil para testar o formato do relatório sem gastar créditos/GPU).
*   **`relatorio_aula.md`**: É o resultado final pronto para ser lido no seu leitor de Markdown favorito.

---

## 📂 Estrutura de Scripts

*   `main.py`: O orquestrador principal.
*   `scripts/transcrever_api.py`: Gerencia o envio e recebimento de áudio via API.
*   `scripts/gerar_relatorio_api.py`: Envia o texto para a IA gerar o relatório.
*   *(Opcional)* `scripts/transcrever_local.py`: Versão para processamento direto na sua máquina (requer hardware robusto).

> [!IMPORTANT]
> O servidor backend ([Repositório Backend](https://github.com/RenanFerreira0023/backend-agente-estudos-ingles)) precisa estar ligado e acessível na sua rede local para que este cliente funcione corretamente. Certifique-se de que o IP em `config.json` ou `.env` corresponde ao IP da máquina que roda o backend.