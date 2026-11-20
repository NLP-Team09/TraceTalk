"""Start the bundled TraceTalk web app with the local Windows Ollama service."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
MODEL = "tracetalk-student-v1"
BASE = "http://127.0.0.1:11434"


def register(ollama):
    manifest = json.loads((ROOT / "model/MANIFEST.json").read_text(encoding="utf-8"))
    name = MODEL + ".gguf"
    print("첫 실행입니다. 모델 두 조각을 합치고 확인합니다.", flush=True)
    with tempfile.TemporaryDirectory(prefix="tracetalk-") as work:
        folder = Path(work)
        digest = hashlib.sha256()
        with (folder / name).open("wb") as output:
            for suffix in ("aa", "ab"):
                with (ROOT / "release" / (name + ".part-" + suffix)).open("rb") as part:
                    for chunk in iter(lambda: part.read(1024 * 1024), b""):
                        digest.update(chunk)
                        output.write(chunk)
        if digest.hexdigest() != manifest["files"][name]:
            raise ValueError("모델 파일 지문이 다릅니다. ZIP의 release 폴더를 다시 확인하세요.")
        shutil.copyfile(ROOT / "model/Modelfile", folder / "Modelfile")
        subprocess.run([ollama, "create", MODEL, "-f", "Modelfile"], cwd=folder,
                       env={**os.environ, "OLLAMA_HOST": BASE}, check=True)


def main():
    ollama = shutil.which("ollama") or Path(os.environ["LOCALAPPDATA"]) / "Programs/Ollama/ollama.exe"
    if not Path(ollama).is_file():
        raise RuntimeError("Windows용 Ollama를 설치한 뒤 다시 실행하세요. https://ollama.com/download/windows")
    try:
        with urllib.request.urlopen(BASE + "/api/tags", timeout=5) as response:
            models = {row["name"] for row in json.load(response)["models"]}
    except OSError as exc:
        raise RuntimeError("시작 메뉴에서 Ollama를 켠 뒤 다시 실행하세요.") from exc
    if not models.intersection({MODEL, MODEL + ":latest"}):
        register(ollama)
    args = [sys.executable, "-m", "tracetalk.web.run", "--model", MODEL,
            "--base-url", BASE, "--retriever", "auto"]
    for version in ("v4", "v2", "v1"):
        draft = ROOT / "data/db/lexicon" / f"easy_draft_{version}.jsonl"
        if draft.is_file():
            args.extend(["--easy-draft", str(draft)])
            break
    return subprocess.call(args, cwd=ROOT)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        sys.exit(str(exc))
