import argparse
import base64
import requests
import sys
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_api_base_url():
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("LLM_API_BASE_URL") or os.getenv("LLM_API_BASE_URL", "http://192.168.0.8:8000")
    except Exception:
        return os.getenv("LLM_API_BASE_URL", "http://192.168.0.8:8000")

def transcribe_via_api(video_path):
    base_url = get_api_base_url()
    api_url = f"{base_url}/uploadVideo"
    
    if not os.path.exists(video_path):
        print(f"Erro: Arquivo {video_path} não encontrado.", file=sys.stderr)
        return None

    # ======== NOVIDADE: EXTRAIR APENAS O ÁUDIO ========
    # O arquivo ficará salvo para você reutilizar se der erro na API, servindo de Mock.
    # Para forçar extrair de um novo arquivo de vídeo, você deleta esse arquivo .m4a.
    temp_audio = "mock_audio_extraido.m4a"
    
    try:
        import subprocess
        if os.path.exists(temp_audio):
            print(f">>> AVISO: Usando o arquivo '{temp_audio}' como Mock! Pulando extração ffmpeg. <<<", file=sys.stderr)
            print(f"Para extrair um NOVO vídeo, delete o '{temp_audio}' manualmente.", file=sys.stderr)
        else:
            print(f"Extraindo apenas o áudio do vídeo longo para agilizar o envio...", file=sys.stderr)
            # Extrai o áudio bem rápido, removendo o vídeo (-vn)
            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-c:a", "aac", temp_audio], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Áudio extraído com sucesso!", file=sys.stderr)
        
        print(f"Convertendo para Base64 (isso será bem rápido)...", file=sys.stderr)
        with open(temp_audio, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            
        # REMOVIDO: Não apaga mais o áudio para você poder reutilizar ele nos testes (Mock)
            
    except Exception as e:
        print(f"Erro ao ler/preparar arquivo: {e}", file=sys.stderr)
        return None

    payload = {
        "video_base64": encoded_string,
        "filename": os.path.basename(video_path) + "_audio.m4a"
    }

    print(f"Enviando para API Remota em {api_url}...", file=sys.stderr)
    try:
        # Timeout de 10 minutos (600s) para dar tempo de transcrever vídeos longos na GPU
        response = requests.post(api_url, json=payload, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        if "text" in result:
            return result["text"]
        else:
            print(f"Resposta da API não contém campo 'text'. Detalhes: {result}", file=sys.stderr)
            return None
            
    except requests.exceptions.Timeout:
        print(f"Erro: A API demorou demais para responder (Timeout). Verifique se o servidor remoto está processando.", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Erro na comunicação com a API: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envia vídeo via Base64 para transcrição remota em GPU.")
    parser.add_argument("file_path", help="Caminho para o arquivo de vídeo")
    args = parser.parse_args()
    
    result = transcribe_via_api(args.file_path)
    if result:
        # Imprime o resultado final para que o main.py possa capturar
        print(result)
    else:
        sys.exit(1)
