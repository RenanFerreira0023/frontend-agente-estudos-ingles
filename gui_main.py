import os
import sys
import threading
import subprocess
import time
from datetime import datetime
from queue import Queue

from kivy.config import Config
# Desabilita o redimensionamento para manter o layout "moderno" e fixo se preferir, 
# ou deixa flexível. Vamos deixar flexível mas com tamanho inicial bom.
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '700')

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
import tkinter as tk
from tkinter import filedialog
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatButton, MDFlatButton
from kivymd.toast import toast

# KV Layout definition
KV = '''
<LogLabel@MDLabel>:
    size_hint_y: None
    height: self.texture_size[1]
    theme_text_color: "Custom"
    text_color: 0.9, 0.9, 0.9, 1
    font_style: "Caption"
    markup: True

MDScreen:
    md_bg_color: 0.1, 0.1, 0.12, 1

    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        # HEADER
        MDBoxLayout:
            size_hint_y: None
            height: "80dp"
            spacing: "15dp"
            
            MDIcon:
                icon: "robot-industrial"
                font_size: "48sp"
                theme_text_color: "Custom"
                text_color: 0, 0.7, 1, 1
                pos_hint: {"center_y": .5}

            MDBoxLayout:
                orientation: 'vertical'
                pos_hint: {"center_y": .5}
                MDLabel:
                    text: "English Study Agent"
                    font_style: "H5"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                MDLabel:
                    text: "Seu assistente moderno para transcrição e relatórios"
                    font_style: "Subtitle2"
                    theme_text_color: "Hint"

        # MAIN CONSOLE
        MDCard:
            orientation: 'vertical'
            padding: "10dp"
            md_bg_color: 0.15, 0.15, 0.18, 1
            radius: [15, 15, 15, 15]
            elevation: 2
            
            MDBoxLayout:
                size_hint_y: None
                height: "30dp"
                padding: ["10dp", 0]
                MDLabel:
                    text: "TERMINAL LOGS"
                    font_style: "Overline"
                    theme_text_color: "Custom"
                    text_color: 0.5, 0.5, 0.5, 1

            ScrollView:
                id: scroll_log
                bar_width: "4dp"
                MDBoxLayout:
                    id: log_box
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    padding: "10dp"
                    spacing: "5dp"

        # PROGRESS INFO
        MDBoxLayout:
            size_hint_y: None
            height: "40dp"
            spacing: "10dp"
            
            MDProgressBar:
                id: progress_bar
                value: 0
                max: 100
                pos_hint: {"center_y": .5}
                color: 0, 0.7, 1, 1
            
            MDLabel:
                id: status_label
                text: "Aguardando ação..."
                size_hint_x: None
                width: "150dp"
                font_style: "Caption"
                theme_text_color: "Secondary"
                halign: "right"
                pos_hint: {"center_y": .5}

        # BUTTONS ACTION
        MDBoxLayout:
            size_hint_y: None
            height: "60dp"
            spacing: "15dp"
            
            MDFillRoundFlatButton:
                text: "NOVA TRANSCRIÇÃO"
                icon: "plus"
                md_bg_color: 0, 0.5, 0.8, 1
                size_hint_x: 1
                on_release: app.open_file_manager()
                
            MDFillRoundFlatButton:
                text: "ABRIR RELATÓRIO"
                icon: "file-document"
                md_bg_color: 0.2, 0.6, 0.2, 1
                size_hint_x: 0.8
                on_release: app.open_report()

            MDFillRoundFlatButton:
                text: "LIMPAR MOCK"
                icon: "delete-sweep"
                md_bg_color: 0.7, 0.2, 0.2, 1
                size_hint_x: 0.6
                on_release: app.clear_mock()
'''

class EnglishStudyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        self.title = "English Study Agent Manager"
        
        self.log_queue = Queue()
        self.process_thread = None
        
        # Schedule log checking
        Clock.schedule_interval(self.check_logs, 0.1)
        
        return Builder.load_string(KV)

    def on_start(self):
        self.add_log("[color=00bfff][INFO][/color] Aplicação iniciada com sucesso.")
        self.add_log("[color=888888]Pronto para processar seus estudos.[/color]")

    def add_log(self, text):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[color=555555][{timestamp}][/color] {text}"
        
        # We need to use Builder to create the label to avoid threading issues 
        # but add_log is called from main thread mostly via check_logs
        from kivy.factory import Factory
        lbl = Factory.LogLabel(text=formatted)
        self.root.ids.log_box.add_widget(lbl)
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

    def scroll_to_bottom(self):
        self.root.ids.scroll_log.scroll_y = 0

    def check_logs(self, dt):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.add_log(msg)

    # --- ACTIONS ---

    def clear_mock(self):
        mock_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "transcricao_mock.txt")
        if os.path.exists(mock_file):
            os.remove(mock_file)
            self.add_log("[color=ff5555][SYSTEM][/color] Arquivo de mock removido.")
            toast("Mock apagado com sucesso")
        else:
            self.add_log("[color=ffff00][WARN][/color] Nenhum arquivo de mock encontrado.")
            toast("Nada para apagar")

    def open_report(self):
        report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relatorio_aula.md")
        if os.path.exists(report_file):
            self.add_log(f"[color=55ff55][SUCCESS][/color] Abrindo relatório: {report_file}")
            os.startfile(report_file)
        else:
            self.add_log("[color=ff5555][ERROR][/color] Relatório não encontrado. Processe um vídeo primeiro.")
            toast("Arquivo não encontrado")

    # --- FILE SELECTION (TRADITIONAL) ---

    def open_file_manager(self):
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo de vídeo",
            filetypes=[("Arquivos de Vídeo ou Áudio", "*.mp4 *.mp3 *.mkv *.avi *.wav"), ("Todos os Arquivos", "*.*")]
        )
        
        root.destroy()
        
        if file_path:
            self.start_process_thread(file_path)

    # --- BACKEND INTEGRATION ---

    def start_process_thread(self, video_path):
        if self.process_thread and self.process_thread.is_alive():
            toast("Um processo já está em execução")
            return
            
        self.root.ids.progress_bar.value = 5
        self.root.ids.status_label.text = "Processando..."
        
        self.process_thread = threading.Thread(target=self.run_backend, args=(video_path,))
        self.process_thread.daemon = True
        self.process_thread.start()

    def run_backend(self, video_path):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # Step 1: Transcrição
            self.log_queue.put(f"[color=00ffff]Etapa 1:[/color] Transcrevendo {os.path.basename(video_path)}...")
            
            mock_file = os.path.join(base_path, "transcricao_mock.txt")
            transcription_text = ""
            
            if os.path.exists(mock_file):
                self.log_queue.put("[color=ffff00]Aviso:[/color] Usando cache de transcrição.")
                with open(mock_file, "r", encoding="utf-8") as f:
                    transcription_text = f.read()
            else:
                self.log_queue.put("Iniciando API de transcrição remota...")
                cmd = [sys.executable, "./scripts/transcrever_api.py", video_path]
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', env=env, cwd=base_path)
                
                output = []
                for line in proc.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        self.log_queue.put(f"[color=888888]> {clean_line}[/color]")
                        output.append(line)
                proc.wait()
                
                if proc.returncode != 0:
                    self.log_queue.put("[color=ff0000]Falha na transcrição.[/color]")
                    return
                
                transcription_text = "".join(output)
                with open(mock_file, "w", encoding="utf-8") as f:
                    f.write(transcription_text)

            Clock.schedule_once(lambda dt: self.update_progress(50, "Gerando relatório..."))

            # Step 2: Relatório
            self.log_queue.put("[color=00ffff]Etapa 2:[/color] Gerando relatório com LLM...")
            cmd_rep = [sys.executable, "./scripts/gerar_relatorio_api.py"]
            proc_rep = subprocess.Popen(cmd_rep, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', env=env, cwd=base_path)
            
            # Envia a transcrição via stdin
            proc_rep.stdin.write(transcription_text)
            proc_rep.stdin.close()
            
            report_lines = []
            for line in proc_rep.stdout:
                clean_line = line.strip()
                if clean_line:
                    self.log_queue.put(f"[color=888888]> {clean_line}[/color]")
                    report_lines.append(line)
            proc_rep.wait()
            
            if proc_rep.returncode != 0:
                self.log_queue.put("[color=ff0000]Falha na geração do relatório.[/color]")
                return
            
            report_text = "".join(report_lines)
            
            # Step 3: Salvar
            report_file = os.path.join(base_path, "relatorio_aula.md")
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_text)
            
            self.log_queue.put("[color=00ff00]Sucesso![/color] Relatório salvo.")
            Clock.schedule_once(lambda dt: self.update_progress(100, "Concluído!"))
            
        except Exception as e:
            self.log_queue.put(f"[color=ff0000]Erro Crítico:[/color] {str(e)}")
            Clock.schedule_once(lambda dt: self.update_progress(0, "Erro"))

    def update_progress(self, val, status):
        self.root.ids.progress_bar.value = val
        self.root.ids.status_label.text = status

if __name__ == "__main__":
    EnglishStudyApp().run()
