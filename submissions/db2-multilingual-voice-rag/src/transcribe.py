"""Transcribe audio/*.mp3 with local Whisper and save timestamped segments to transcripts/<name>.json.
Needs ffmpeg on PATH. The committed transcripts let index.py run without this step."""
import json, pathlib, sys
import whisper

root = pathlib.Path(__file__).resolve().parent
LANG = {"talk_en": "en", "talk_hi": "hi"}
model = whisper.load_model(sys.argv[1] if len(sys.argv) > 1 else "small")

for name, lang in LANG.items():
    r = model.transcribe(str(root / "audio" / f"{name}.mp3"), language=lang)
    out = {"source": f"audio/{name}.mp3", "language": lang,
           "segments": [{"start": round(s["start"], 1), "end": round(s["end"], 1), "text": s["text"].strip()}
                        for s in r["segments"]]}
    (root / "transcripts" / f"{name}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(name, len(out["segments"]), "segments")
