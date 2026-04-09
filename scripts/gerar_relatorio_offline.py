import argparse
import sys
import re
from gpt4all import GPT4All

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

import time

def format_time(seconds):
    if seconds is None:
        return "Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

def generate_report(transcription):
    print("Loading GPT4All model (CPU Mode)...", file=sys.stderr)
    model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf", n_threads=8, device='cpu')

    print("Cleaning transcription (removing timestamps)...", file=sys.stderr)
    transcription = clean_transcription(transcription)

    chunks = chunk_text(transcription)
    intermediate_summaries = []
    
    # Process each chunk individually
    print(f"Splitting transcription into {len(chunks)} chunks to fit context window...", file=sys.stderr)
    print("---------------------------------------", file=sys.stderr)
    
    start_time_all = time.time()
    for i, chunk in enumerate(chunks):
        if i > 0:
            elapsed = time.time() - start_time_all
            avg_time = elapsed / i
            remaining = avg_time * (len(chunks) - i)
            print(f"Processing chunk {i+1}/{len(chunks)}... (ETA: {format_time(remaining)})", file=sys.stderr)
        else:
            print(f"Processing chunk {i+1}/{len(chunks)}... (calculating ETA...)", file=sys.stderr)
            
        # Using English prompts internally is much more accurate for a 3B model processing an English transcript.
        prompt_chunk = f"""Instruction: You are an English Teacher's assistant. Summarize this part of an English class.
Focus strictly on:
- The main theme or grammar point.
- Specific words mentioned for pronunciation practice ("how to say...", "pronounce as...").
- Vocabulary translations and tricky meanings.
- Teacher's tips for learning.

Class excerpt:
{chunk}

Summary of this part (English):
"""
        chunk_output = model.generate(prompt_chunk, max_tokens=128) # even smaller for safety
        print(f"  > Summary {i+1} generated ({len(chunk_output)} chars)", file=sys.stderr)
        intermediate_summaries.append(chunk_output)
        
    total_time = time.time() - start_time_all
    print(f"All chunks summarized in {format_time(total_time)}", file=sys.stderr)
    print("---------------------------------------", file=sys.stderr)
    
    combined_summaries = "\n\n".join(intermediate_summaries)
    
    # Now generate the final report from the combined summaries
    # Simplify template to prevent the AI from echoing instructions
    prompt_template = """System: You are an education assistant. Use the summaries below to write a study report in BRAZILIAN PORTUGUESE.

Class Summaries:
{transcription}

### Instruction:
Write a study report in PORTUGUESE about the lesson above. 
Use these exact headers:
- **Tema da Aula** (The main topic)
- **Resumo da Aula** (Detailed summary of what happened)
- **Pronúncia e Fonética** (List words discussed and how to say them)
- **Dicas e Traduções** (Vocabulary and teacher tips)

Do NOT repeat the instructions. Start directly with the report.

Study Report in Portuguese:
"""
    print(f"\nGenerating final structured report...", file=sys.stderr)
    prompt = prompt_template.format(transcription=combined_summaries)
    print(f"  > Final prompt length: {len(prompt)} chars", file=sys.stderr)
    output = model.generate(prompt, max_tokens=1024)
    return output

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processes transcription using GPT4All to generate a structured report.")
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
