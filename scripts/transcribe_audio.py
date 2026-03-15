#!/usr/bin/env python3
import sys
from faster_whisper import WhisperModel


def main():
    if len(sys.argv) < 2:
        print("usage: transcribe_audio.py <audio_path> [model]", file=sys.stderr)
        raise SystemExit(2)

    audio_path = sys.argv[1]
    model_name = sys.argv[2] if len(sys.argv) > 2 else "tiny"

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, vad_filter=True, beam_size=1, language="zh")

    print(f"language={info.language} prob={info.language_probability:.3f}")
    for seg in segments:
        text = seg.text.strip()
        if text:
            print(text)


if __name__ == "__main__":
    main()
