import argparse
import sys
import re
import requests
import json
import time
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

def clean_transcription(text):
    """Removes timestamps and extra noise from whisper transcription."""
    # Remove [00:00.000 --> 00:07.000] patterns
    text = re.sub(r'\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]', '', text)
    
    # Remove repetitive filler words and greeting noise to focus the context
    text = re.sub(r'(?i)\b(I\'m sorry|Hi|Hello|Hi teacher|How are you today|I\'m fine)\b', '', text)
    
    # Remove extra whitespace and lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return ' '.join(lines)

def chunk_text(text, chunk_size=2500, overlap=300):
    """Splits a long text into smaller chunks with some overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def format_time(seconds):
    if seconds is None:
        return "Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

def call_remote_api(prompt, url=None):
    if url is None:
        base_url = get_api_base_url()
        url = f"{base_url}/chat"
        
    try:
        response = requests.post(url, json={"prompt": prompt}, timeout=600)
        response.raise_for_status()
        # assuming the API returns a JSON with a 'response' or similar field, 
        # but based on common patterns it might just return the text or a specific field.
        # If it returns raw text, we use response.text.
        # Given the user's prompt structure, I'll try to parse JSON first.
        try:
            return response.json().get("response", response.text)
        except:
            return response.text
    except Exception as e:
        print(f"Error calling API: {e}", file=sys.stderr)
        return f"ERROR: Could not get response from LLM API. {e}"

def generate_report(transcription):
    base_url = get_api_base_url()
    api_url = f"{base_url}/chat"
    print(f"Connecting to remote LLM Agent at {api_url}...", file=sys.stderr)

    print("Cleaning transcription (removing timestamps)...", file=sys.stderr)
    transcription = clean_transcription(transcription)

    chunks = chunk_text(transcription)
    intermediate_summaries = []
    
    # Process each chunk individually (Now in Parallel!)
    print(f"Splitting transcription into {len(chunks)} chunks...")
    print(f"Processing in PARALLEL via Remote API...", file=sys.stderr)
    print("---------------------------------------", file=sys.stderr)
    
    start_time_all = time.time()
    
    from concurrent.futures import ThreadPoolExecutor
    
    total_chunks = len(chunks)
    def process_chunk(idx_chunk):
        i, chunk = idx_chunk
        print(f"⏳ Processando chunk {i+1} de {total_chunks}...", file=sys.stderr)
        prompt_chunk = f"""Instruction: You are an English Teacher's assistant. Summarize this part of an English class.
Focus strictly on:
- The main theme or grammar point.
- Specific words mentioned for pronunciation practice.
- Vocabulary translations and tricky meanings.
- Teacher's tips for learning.

Class excerpt:
{chunk}

Summary of this part (English):
"""
        return i, call_remote_api(prompt_chunk, api_url)

    # Reduzido para 1 para evitar erro 'ConnectionResetError' no servidor remoto.
    # Se o seu servidor suportar mais, você pode aumentar este número.
    with ThreadPoolExecutor(max_workers=1) as executor:
        results = list(executor.map(process_chunk, enumerate(chunks)))
    
    # Sort results to keep order
    results.sort(key=lambda x: x[0])
    intermediate_summaries = [res[1] for res in results]
    
    total_time = time.time() - start_time_all
    print(f"All chunks summarized by remote API in {format_time(total_time)} (PARALLEL MODE)", file=sys.stderr)
    print("---------------------------------------", file=sys.stderr)
    
    combined_summaries = "\n\n".join(intermediate_summaries)
    
    prompt_template = """System: You are an education assistant. Use the summaries below to write a study report in BRAZILIAN PORTUGUESE.

Class Summaries:
{summaries}

### Instruction:
Write a study report in PORTUGUESE about the lesson above. 
Use these exact headers:
- **Tema da Aula**
- **Resumo da Aula**
- **Pronúncia e Fonética**
- **Dicas e Traduções**

Do NOT repeat the instructions. Start directly with the report.

Study Report in Portuguese:
"""
    print(f"\nGenerating final structured report...", file=sys.stderr)
    final_prompt = prompt_template.format(summaries=combined_summaries)
    output = call_remote_api(final_prompt, api_url)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processes transcription using a remote API to generate a structured report.")
    parser.add_argument("--text", help="The transcribed text. If not provided, reads from stdin.")
    args = parser.parse_args()
    
    text = args.text
    if not text:
        text = sys.stdin.read()
        
    if not text.strip():
        print("Error: Empty input text.", file=sys.stderr)
        sys.exit(1)
        
    report = generate_report(text)
    print(report)
