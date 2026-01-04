#!/usr/bin/env python3

import subprocess
import sys
import tarfile
import hashlib
from pathlib import Path

import requests
from tqdm import tqdm

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
CATEGORIES = [
    (
        "baroque",
        "heRJbiin",
        "sha256:851332a261718877d50a9caae3703417d4c91667c52d8cdd25c3a4d8cf8c5a15",
    ),
    (
        "impressionist",
        "6Ju71xWo",
        "sha256:4164e80bc69b47179768b43e127ba85aaa80425c5e62f762ada242428567a81e",
    ),
    (
        "romantic",
        "PmKL8X81",
        "sha256:d6a4f3c5980bddeda5ac63b888a627ab7a811e3ca7604a1f652965aad91ff1e7",
    ),
    (
        "general",
        "ahiL5QGu",
        "sha256:7648cc81e7f7c90569c511b7eb5b03fbfe8123073b556415e6f1f043bdb89ad4",
    ),
    (
        "pcc0",
        "hjZAnHoV",
        "sha256:17185d544d1c91e982b7616c019f13410042b5a341051a9ac0ce6284cc4817a2",
    ),
]
PDL = "https://pixeldrain.com/api/file/{fid}?download=1"
WORK_DIR = Path.cwd() / "wallpapers"
THEMES = ["nord", "dracula", "gruvbox"]
CHUNK = 1024 * 1024  # 1 MiB
IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")
SKIP_EXISTING = True
ORIGINAL_DIR = "origin"

CHECK = "✔"
CROSS = "❌"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def die(msg: str) -> None:
    print(msg, file=sys.stderr)
    sys.exit(1)


def download(url: str, dest: Path, digest: str) -> None:
    """Resume-friendly downloader with progress bar."""
    headers = {}
    downloaded = dest.stat().st_size if dest.exists() else 0
    headers["Range"] = f"bytes={downloaded}-"
    digest_kind, digest = digest.split(":")
    if dest.is_file() and SKIP_EXISTING:
        print(f"{dest.name} exists and SKIP_EXISTING set, skipping...", file=sys.stderr)
    else:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            if r.status_code == 416:  # Range not satisfiable → file complete
                print(f"{dest.name} already fully downloaded")
                return
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0)) + downloaded
            with open(dest, "ab") as f, tqdm(
                desc=dest.name,
                total=total,
                initial=downloaded,
                unit="B",
                unit_scale=True,
            ) as bar:
                for chunk in r.iter_content(chunk_size=CHUNK):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

    with open(dest, "rb") as f:
        print("Verifying digest...", end="", file=sys.stderr)
        got_digest: str = hashlib.file_digest(f, digest_kind).hexdigest()
        if got_digest != digest:
            die(
                f" {CROSS} mismatch!\n"
                f"Received {digest_kind}:{got_digest}\n"
                f"Expected {digest_kind}:{digest}\n"
            )
        else:
            print(" " + CHECK, file=sys.stderr)


def extract(archive: Path, extract_to: Path) -> None:
    """Extract and flatten .tar.xz"""
    with tarfile.open(archive, "r:xz") as tf:
        for member in tf.getmembers():
            if member.isreg():
                member.name = Path(member.name).name
                tf.extract(member, extract_to, filter="data")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> None:
    WORK_DIR.mkdir(exist_ok=True)
    dl_dir = WORK_DIR / ".downloads"
    dl_dir.mkdir(exist_ok=True)

    for cat, fid, digest in CATEGORIES:
        tarball: Path = (dl_dir / fid).with_suffix(".tar.xz")
        cat_dir: Path = WORK_DIR / cat
        org_dir: Path = cat_dir / ORIGINAL_DIR

        download(PDL.format(fid=fid), tarball, digest)
        cat_dir.mkdir(exist_ok=True)
        org_dir.mkdir(exist_ok=True)
        extract(tarball, org_dir)

    for cat, _, _ in CATEGORIES:
        for theme in THEMES:
            cat_dir: Path = WORK_DIR / cat
            theme_dir: Path = cat_dir / theme
            theme_dir.mkdir(exist_ok=True)
            subprocess.run(
                [
                    "gowall",
                    "convert",
                    "--dir",
                    cat_dir / ORIGINAL_DIR,
                    "--output",
                    theme_dir,
                    "--theme",
                    theme,
                ]
            )

    print(f"All done {CHECK}")
    print(f"Results are in {WORK_DIR}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        die("Aborted by user")
