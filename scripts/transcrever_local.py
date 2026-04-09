import argparse
import whisper
import sys
import os
import ffmpeg
import time

def get_audio_duration(file_path):
    try:
        probe = ffmpeg.probe(file_path)
        format_info = probe.get('format', {})
        duration = format_info.get('duration')
        if duration:
            return float(duration)
    except Exception as e:
        print(f"Warning: Could not get video duration ({e})", file=sys.stderr)
    return None

def format_time(seconds):
    if seconds is None:
        return "Unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

def transcribe_video(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
        
    duration = get_audio_duration(file_path)
    if duration:
        print(f"=======================================", file=sys.stderr)
        print(f"Video Duration: {format_time(duration)}", file=sys.stderr)
        print(f"Estimated Transcription Time: {format_time(duration * 0.2)} to {format_time(duration * 0.5)} (depending on hardware)", file=sys.stderr)
        print(f"=======================================\n", file=sys.stderr)
        
    print(f"Loading Whisper model (base)...", file=sys.stderr)
    start_time = time.time()
    model = whisper.load_model("base") # using base for speed and decent accuracy
    load_time = time.time() - start_time
    print(f"Model loaded in {format_time(load_time)}", file=sys.stderr)
    
    print(f"\nTranscribing video: {file_path}", file=sys.stderr)
    print(f"Progress will be printed below as the audio is transcribed:\n", file=sys.stderr)
    
    start_time = time.time()
    # Verbose = True will print the transcription as it goes
    result = model.transcribe(file_path, verbose=True)
    transcribe_time = time.time() - start_time
    
    print(f"\n=======================================", file=sys.stderr)
    print(f"Transcription Finished in {format_time(transcribe_time)}", file=sys.stderr)
    print(f"=======================================\n", file=sys.stderr)
    
    return result["text"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extracts audio from an MP4 file and converts it to text using OpenAI Whisper.")
    parser.add_argument("file_path", help="Path to the local MP4 file")
    args = parser.parse_args()
    
    transcription = transcribe_video(args.file_path)
    # Print the final raw text to stdout so it can be piped
    print(transcription)
