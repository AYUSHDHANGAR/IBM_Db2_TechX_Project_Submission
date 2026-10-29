"""Developer tool (needs network + `pip install gTTS`): turns scripts/talk_*.txt into audio/talk_*.mp3.
The generated mp3 files are committed, so running the demo does not need this script."""
import pathlib
from gtts import gTTS

root = pathlib.Path(__file__).resolve().parent.parent
for lang in ("en", "hi"):
    text = (root / "scripts" / f"talk_{lang}.txt").read_text(encoding="utf-8")
    gTTS(text, lang=lang).save(str(root / "audio" / f"talk_{lang}.mp3"))
    print("wrote", f"audio/talk_{lang}.mp3")
