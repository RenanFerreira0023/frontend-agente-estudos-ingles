import subprocess
import argparse
import os
import sys
import tkinter as tk
from tkinter import filedialog

def main():
    parser = argparse.ArgumentParser(description="Offline Study Assistant - Transcribes video and generates notes.")
    parser.add_argument("video_file", nargs='?', help="Path to the MP4 video file (optional, opens a dialog if omitted)")
    args = parser.parse_args()
    
    video_file = args.video_file
    
    if not video_file:
        root = tk.Tk()
        root.withdraw() # Transforma a janela principal invisível
        video_file = filedialog.askopenfilename(
            title="Selecione o arquivo de vídeo para transcrever",
            filetypes=[("Arquivos de Vídeo ou Áudio", "*.mp4 *.mp3 *.mkv *.avi *.wav"), ("Todos os Arquivos", "*.*")]
        )
        
        if not video_file:
            print("Nenhum arquivo selecionado. Saindo.")
            return

    if not os.path.exists(video_file):
        print(f"Error: Video file not found: {video_file}")
        return
        
    print(f"Step 1: Transcribing {video_file}...")
    
    # Define env var to force utf-8 encoding in windows console for whisper verbose prints
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # MOCK TEMPORÁRIO PARA TESTES
    mock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcricao_mock.txt")
    if os.path.exists(mock_file):
        print(f">>> AVISO: Usando {mock_file} (Pulando transcrição real) <<<")
        with open(mock_file, "r", encoding="utf-8") as f:
            transcription_text = f.read()
    else:
        print(f"Step 1: Transcribing {video_file} via Remote GPU API...")
        transcribe_cmd = [sys.executable, "./scripts/transcrever_api.py", video_file]
        
        try:
            # Pega apenas o stdout, permitindo que stderr vá direto para o console e seja visto
            transcription_result = subprocess.run(transcribe_cmd, check=True, stdout=subprocess.PIPE, text=True, encoding='utf-8', env=env)
            transcription_text = transcription_result.stdout
            
            # SALVA PARA USO NAS PRÓXIMAS VEZES (MOCK)
            with open(mock_file, "w", encoding="utf-8") as f:
                f.write(transcription_text)
            print(f">>> SUCESSO: Transcrição salva em {mock_file} para testes futuros. <<<")
        except subprocess.CalledProcessError as e:
            print(f"Error during transcription:\n{e.stderr}")
            return
        
    print("Step 2: Generating report with Remote LLM Agent (Fast Mode)...")
    report_cmd = [sys.executable, "./scripts/gerar_relatorio_api.py"]
    
    try:
        # We don't pipe stderr here so we can see the progress (Loading model, chunks, etc) in real-time.
        report_result = subprocess.run(report_cmd, input=transcription_text, check=True, stdout=subprocess.PIPE, text=True, encoding='utf-8', env=env)
        report_text = report_result.stdout
    except subprocess.CalledProcessError:
        print(f"Error during report generation.")
        return
        
    print("Step 3: Saving report to relatorio_aula.md...")
    with open("relatorio_aula.md", "w", encoding="utf-8") as f:
        f.write(report_text)
        
    print("Done! Report saved to relatorio_aula.md")

if __name__ == "__main__":
    main()
