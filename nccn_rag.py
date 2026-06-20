#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCCN RAG预处理工具

功能:
- 调用 mineru-open-api 或 SiliconFlow DeepSeek-OCR 将PDF/图片/URL转换为Markdown
- 将Markdown切分为RAG友好的chunks和JSONL
- 可选调用OpenAI-compatible API将英文Markdown翻译为中文
"""

import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import tempfile

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = Path(os.getenv("NCCN_DOWNLOAD_DIR", SCRIPT_DIR / "nccn_downloads")).resolve()
DEEPSEEK_OCR_DEFAULT_MODEL = "deepseek-ai/DeepSeek-OCR"
DEEPSEEK_OCR_DEFAULT_BASE_URL = "https://api.siliconflow.cn/v1"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
PDF_SUFFIXES = {".pdf"}


def ensure_directories(base_dir: Optional[Path] = None) -> Dict[str, Path]:
    base_dir = Path(base_dir or DEFAULT_BASE_DIR).resolve()
    dirs = {
        "base": base_dir,
        "markdown": base_dir / "markdown",
        "translated": base_dir / "translated",
        "rag": base_dir / "rag",
        "logs": base_dir / "logs",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    return dirs


def _default_markdown_path(input_path: Path, output_dir: Optional[Path]) -> Path:
    output_dir = output_dir or ensure_directories()["markdown"]
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9_\-\u4e00-\u9fff]+", "_", input_path.stem)
    return output_dir / f"{safe_name}.md"


def _resolve_output_path(output: Optional[Path], input_path: Path, default_dir: Path) -> Path:
    if output is None:
        return _default_markdown_path(input_path, default_dir)
    output = output.expanduser().resolve()
    if output.suffix.lower() != ".md":
        output.mkdir(parents=True, exist_ok=True)
        return _default_markdown_path(input_path, output)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def run_mineru(
    input_path: str,
    output_path: Path,
    mode: str = "flash",
    language: str = "en",
    token: Optional[str] = None,
) -> Path:
    """调用 mineru-open-api 转换文档。"""
    mode = mode.lower()
    cmd = ["mineru-open-api"]
    if mode == "flash":
        cmd.extend(["flash-extract", str(input_path), "--language", language])
    elif mode == "extract":
        cmd.extend(["extract", str(input_path), "--format", "md", "--language", language])
        if token:
            cmd.extend(["--token", token])
    else:
        raise ValueError("mode 必须是 flash 或 extract")

    cmd.extend(["-o", str(output_path)])
    print("执行MinerU:", " ".join(cmd))
    result = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"MinerU转换失败，退出码: {result.returncode}")
    return output_path


def _is_remote_url(path: Path) -> bool:
    return str(path).startswith(("http://", "https://"))


def _download_remote_input(input_path: Path, temp_dir: Path) -> Path:
    if not _is_remote_url(input_path):
        return input_path
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", input_path.name) or "input"
    target = temp_dir / safe_name
    print(f"下载远程输入: {input_path}")
    response = requests.get(str(input_path), timeout=120)
    response.raise_for_status()
    target.write_bytes(response.content)
    return target


def _image_to_base64_url(image_path: Path) -> str:
    data = base64.b64encode(image_path.read_bytes()).decode("ascii")
    suffix = image_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,{data}"


def _iter_pdf_pages(input_path: Path, temp_dir: Path, max_pages: int = 0) -> List[Path]:
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PDF转图片需要安装 PyMuPDF：pip install pymupdf") from exc

    doc = fitz.open(str(input_path))
    try:
        page_count = doc.page_count
        if max_pages and max_pages > 0:
            page_count = min(page_count, max_pages)
        pages: List[Path] = []
        matrix = fitz.Matrix(2, 2)
        for index in range(page_count):
            page = doc.load_page(index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = temp_dir / f"{input_path.stem}_page_{index + 1:04d}.png"
            pix.save(image_path)
            pages.append(image_path)
        return pages
    finally:
        doc.close()


def _call_deepseek_ocr_page(image_url: str, api_key: str, base_url: str, model: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请对图片中的文字进行高精度OCR。保留原文结构、标题、表格、列表、换行和医学/药物/剂量术语；只输出Markdown，不要添加原文没有的信息。",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        "temperature": 0,
        "max_tokens": 4096,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=180)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def run_deepseek_ocr(
    input_path: str,
    output_path: Path,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    max_pages: int = 0,
) -> Path:
    """调用 SiliconFlow 上的 deepseek-ai/DeepSeek-OCR 转换PDF/图片为Markdown。"""
    api_key = api_key or os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未配置 SILICONFLOW_API_KEY，无法使用 DeepSeek-OCR")

    base_url = base_url or os.getenv("SILICONFLOW_BASE_URL") or os.getenv("OPENAI_BASE_URL") or DEEPSEEK_OCR_DEFAULT_BASE_URL
    model = model or os.getenv("NCCN_DEEPSEEK_OCR_MODEL") or DEEPSEEK_OCR_DEFAULT_MODEL
    try:
        max_pages = int(max_pages or os.getenv("NCCN_DEEPSEEK_OCR_MAX_PAGES", "0") or 0)
    except ValueError:
        max_pages = 0

    input_path = Path(input_path).expanduser()
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        source_path = _download_remote_input(input_path, temp_dir)
        suffix = source_path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            pages = [source_path]
        elif suffix in PDF_SUFFIXES:
            pages = _iter_pdf_pages(source_path, temp_dir, max_pages=max_pages)
        else:
            raise ValueError("DeepSeek-OCR 当前支持图片文件、PDF文件，或图片URL")
        if not pages:
            raise ValueError("没有可OCR的页面")

        translated_parts = []
        for i, page in enumerate(pages, 1):
            print(f"DeepSeek-OCR进度: {i}/{len(pages)}")
            image_url = _image_to_base64_url(page)
            translated_parts.append(
                f"<!-- page {i} -->\n{_call_deepseek_ocr_page(image_url, api_key, base_url, model)}"
            )

    output_path.write_text("\n\n".join(translated_parts) + "\n", encoding="utf-8")
    return output_path


def extract_markdown(
    input_path: Path,
    output_dir: Optional[Path] = None,
    mode: Optional[str] = None,
    language: Optional[str] = None,
    base_dir: Optional[Path] = None,
    ocr_backend: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> Path:
    """将输入文档转换为Markdown，并生成RAG chunk JSONL。"""
    mode = mode or os.getenv("NCCN_MINERU_MODE", "flash")
    language = language or os.getenv("NCCN_MINERU_LANGUAGE", "en")
    token = os.getenv("MINERU_TOKEN")
    ocr_backend = (ocr_backend or os.getenv("NCCN_OCR_BACKEND", "mineru")).lower()
    dirs = ensure_directories(base_dir)

    input_path = Path(input_path).expanduser().resolve()
    if not input_path.exists() and not str(input_path).startswith(("http://", "https://")):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    output_path = _resolve_output_path(output_dir, input_path, dirs["markdown"])
    if ocr_backend in {"mineru", "minermu"}:
        run_mineru(str(input_path), output_path, mode=mode, language=language, token=token)
    elif ocr_backend in {"deepseek", "deepseek-ocr", "deepseek_ocr", "siliconflow"}:
        run_deepseek_ocr(
            str(input_path),
            output_path,
            api_key=api_key,
            base_url=base_url,
            model=model,
            max_pages=max_pages or 0,
        )
    else:
        raise ValueError("ocr_backend 必须是 mineru 或 deepseek-ocr")

    chunk_jsonl = dirs["rag"] / f"{output_path.stem}.chunks.jsonl"
    chunks = split_markdown_to_chunks(output_path, chunk_jsonl)
    print(f"✅ 已生成 {len(chunks)} 个RAG chunks: {chunk_jsonl}")
    return output_path


def split_markdown_to_chunks(
    markdown_path: Path,
    output_jsonl: Optional[Path] = None,
    chunk_size: int = 1200,
    overlap: int = 100,
) -> List[Dict[str, Any]]:
    """按段落切分Markdown，输出RAG友好的JSONL。"""
    markdown_path = Path(markdown_path).expanduser().resolve()
    text = markdown_path.read_text(encoding="utf-8")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks: List[Dict[str, Any]] = []
    buffer = ""
    for paragraph in paragraphs:
        candidate = paragraph if not buffer else buffer + "\n\n" + paragraph
        if len(candidate) <= chunk_size or not buffer:
            buffer = candidate
        else:
            chunks.append(buffer)
            buffer = paragraph

    if buffer:
        chunks.append(buffer)

    records = []
    for index, chunk in enumerate(chunks, 1):
        record = {
            "id": f"{markdown_path.stem}-{index:04d}",
            "source": str(markdown_path),
            "chunk_index": index,
            "content": chunk,
            "token_estimate": max(1, len(chunk) // 4),
        }
        records.append(record)

    if output_jsonl is None:
        output_jsonl = markdown_path.with_suffix(".chunks.jsonl")
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with open(output_jsonl, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return records


def _translate_chunk(chunk: str, source: str, target: str, api_key: str, base_url: str, model: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "你是医学指南专业译者。请忠实翻译NCCN指南内容，保留Markdown标题、表格、列表和术语一致性。不要添加原文没有的信息。",
            },
            {
                "role": "user",
                "content": f"请将以下{source}内容翻译为{target}，只输出翻译后的Markdown：\n\n{chunk}",
            },
        ],
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def translate_markdown(
    input_path: Path,
    output_path: Optional[Path] = None,
    source: str = "en",
    target: str = "zh",
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
    chunk_size: int = 1800,
) -> Path:
    """调用OpenAI-compatible API翻译Markdown。"""
    api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError("未配置 OPENAI_API_KEY 或 SILICONFLOW_API_KEY，无法执行英文转译")

    base_url = base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model = model or os.getenv("OPENAI_MODEL") or os.getenv("SILICONFLOW_MODEL", "glm-4.5-air")
    input_path = Path(input_path).expanduser().resolve()
    output_path = output_path or input_path.with_name(f"{input_path.stem}.{target}.md")
    output_path = Path(output_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    text = input_path.read_text(encoding="utf-8")
    parts = [p.strip() for p in re.split(r"(?<=\n)\s*(?=#|##|###|\S)", text) if p.strip()]
    chunks: List[str] = []
    buffer = ""
    for part in parts:
        candidate = part if not buffer else buffer + "\n\n" + part
        if len(candidate) <= chunk_size or not buffer:
            buffer = candidate
        else:
            chunks.append(buffer)
            buffer = part
    if buffer:
        chunks.append(buffer)

    translated_parts = []
    for i, chunk in enumerate(chunks, 1):
        print(f"翻译进度: {i}/{len(chunks)}")
        translated_parts.append(_translate_chunk(chunk, source, target, api_key, base_url, model))

    output_path.write_text("\n\n".join(translated_parts) + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="NCCN Markdown/RAG工具")
    sub = parser.add_subparsers(dest="command", required=True)

    convert = sub.add_parser("convert", help="PDF/图片转Markdown")
    convert.add_argument("--input", required=True)
    convert.add_argument("--output")
    convert.add_argument("--mode", default="flash")
    convert.add_argument("--language", default="en")
    convert.add_argument("--base-dir")
    convert.add_argument("--ocr-backend", default=os.getenv("NCCN_OCR_BACKEND", "mineru"))
    convert.add_argument("--api-key")
    convert.add_argument("--base-url")
    convert.add_argument("--model")
    convert.add_argument("--max-pages", type=int, default=0)

    split = sub.add_parser("split", help="Markdown切chunk")
    split.add_argument("--input", required=True)
    split.add_argument("--output")

    translate = sub.add_parser("translate", help="翻译Markdown")
    translate.add_argument("--input", required=True)
    translate.add_argument("--output")
    translate.add_argument("--source", default="en")
    translate.add_argument("--target", default="zh")
    translate.add_argument("--api-key")
    translate.add_argument("--base-url")
    translate.add_argument("--model")

    args = parser.parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve() if hasattr(args, "base_dir") and args.base_dir else None

    if args.command == "convert":
        output = extract_markdown(
            Path(args.input),
            Path(args.output) if args.output else None,
            args.mode,
            args.language,
            base_dir,
            ocr_backend=args.ocr_backend,
            api_key=args.api_key,
            base_url=args.base_url,
            model=args.model,
            max_pages=args.max_pages,
        )
        print(f"✅ {output}")
    elif args.command == "split":
        chunks = split_markdown_to_chunks(Path(args.input), Path(args.output) if args.output else None)
        print(f"✅ chunks={len(chunks)}")
    elif args.command == "translate":
        output = translate_markdown(Path(args.input), Path(args.output) if args.output else None, args.source, args.target, args.api_key, args.base_url, args.model)
        print(f"✅ {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
