#!/usr/bin/env python3
"""Build Smart-Search-for-IntelliFlow.epub from the Markdown chapters.

Requires pandoc, node with Playwright, and an npm-installed mermaid
(pass the path to mermaid.min.js via MERMAID_JS or let the script
install it into a temporary directory).
"""
import os, re, subprocess, sys, tempfile, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
HERE = ROOT / "epub"
OUT = ROOT / "Smart-Search-for-IntelliFlow.epub"
CHAPTERS = ["README.md"] + sorted(p.name for p in ROOT.glob("[0-9][0-9]-*.md"))

def chapter_id(name):
    return "ch-intro" if name == "README.md" else "ch-" + name[:2]

def mermaid_js(tmp):
    if os.environ.get("MERMAID_JS"):
        return os.environ["MERMAID_JS"]
    subprocess.run(["npm", "install", "--silent", "--prefix", tmp, "mermaid@11.4.1"], check=True)
    return os.path.join(tmp, "node_modules/mermaid/dist/mermaid.min.js")

def main():
    tmp = tempfile.mkdtemp()
    img_dir = pathlib.Path(tmp) / "images"; img_dir.mkdir()
    mjs = None
    parts, n_diag = [], 0
    for name in CHAPTERS:
        text = (ROOT / name).read_text(encoding="utf-8")
        lines = text.splitlines()
        # Drop the per-file navigation line ("[Start here](README.md) · ...").
        lines = [l for l in lines if not l.startswith("[Start here](README.md)")]
        text = "\n".join(lines).strip() + "\n"
        # Give each chapter's H1 a stable id; README becomes the introduction.
        def h1(m):
            title = "Introduction" if name == "README.md" else m.group(1)
            return f"# {title} {{#{chapter_id(name)}}}"
        text = re.sub(r"^# (.+)$", h1, text, count=1, flags=re.M)
        # Cross-file links -> internal anchors.
        text = re.sub(r"\]\((README\.md|\d\d-[\w-]+\.md)(#[\w-]+)?\)",
                      lambda m: f"]({m.group(2) or '#' + chapter_id(m.group(1))})", text)
        # Mermaid blocks -> rendered PNGs.
        def diagram(m):
            nonlocal n_diag, mjs
            n_diag += 1
            mjs = mjs or mermaid_js(tmp)
            src = pathlib.Path(tmp) / f"d{n_diag}.mmd"; src.write_text(m.group(1))
            png = img_dir / f"diagram-{n_diag}.png"
            subprocess.run(["node", str(HERE / "render-mermaid.js"), mjs, str(src), str(png)], check=True)
            return f"![Diagram {n_diag}]({png})\n"
        text = re.sub(r"```mermaid\n(.*?)```\n", diagram, text, flags=re.S)
        parts.append(text)
    book = pathlib.Path(tmp) / "book.md"
    book.write_text("\n\n".join(parts), encoding="utf-8")
    subprocess.run([
        "pandoc", str(book), "-f", "markdown-implicit_figures+implicit_figures",
        "-o", str(OUT), "--toc", "--toc-depth=2", "--split-level=1",
        "--metadata-file", str(HERE / "metadata.yaml"),
        "--css", str(HERE / "epub.css"),
        "--resource-path", tmp,
    ], check=True)
    print(f"Wrote {OUT} ({n_diag} diagrams)")

if __name__ == "__main__":
    main()
