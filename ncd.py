#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCCN 下载命令行入口 ncd

常用命令:
  ./ncd interactive
  ./ncd list-cancers
  ./ncd download --cancer breast --language 1 --yes
  ./ncd convert --input guide.pdf --output nccn_downloads/markdown/
  ./ncd translate --input guide.md --output guide.zh.md
"""

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = SCRIPT_DIR / "download_NCCN_Guide_v2_menu.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("nccn_downloader_main", MAIN_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError(f"无法加载脚本: {MAIN_SCRIPT}")
    spec.loader.exec_module(module)
    return module


nccn = _load_module()
NCCNDownloaderV2 = nccn.NCCNDownloaderV2


def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_config(config_data: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    auth_config = config_data.get("authentication", {}) or {}
    settings = config_data.get("download_settings", {}) or {}

    method = os.getenv("NCCN_AUTH_METHOD") or auth_config.get("method", "username_password")
    username = os.getenv("NCCN_USERNAME") or auth_config.get("username", "")
    password = os.getenv("NCCN_PASSWORD") or auth_config.get("password", "")
    cookie_file = os.getenv("NCCN_COOKIE_FILE") or auth_config.get("cookie_file", "extracted_cookies.txt")
    env_cookie = os.getenv("NCCN_COOKIE")

    config: Dict[str, Any] = {
        "download_settings": settings,
    }

    if method == "username_password":
        if not username or not password or password == "your_password_here":
            raise ValueError("用户名/密码认证配置不完整，请设置 NCCN_USERNAME/NCCN_PASSWORD 或 config.json")
        config["auth_method"] = "username_password"
        config["username"] = username
        config["password"] = password
    elif method == "cookie":
        if env_cookie:
            config["auth_method"] = "cookie"
            config["cookie"] = env_cookie
        else:
            if not (SCRIPT_DIR / cookie_file).exists() and not Path(cookie_file).exists():
                raise ValueError(f"Cookie文件不存在: {cookie_file}，请设置 NCCN_COOKIE_FILE 或 NCCN_COOKIE")
            config["auth_method"] = "cookie"
            config["cookie_file"] = cookie_file
    else:
        raise ValueError(f"不支持的认证方式: {method}")

    if getattr(args, "download_dir", None):
        config["download_dir"] = str(Path(args.download_dir).expanduser().resolve())

    return config


def resolve_config_path(config_arg: str) -> Path:
    path = Path(config_arg).expanduser()
    if not path.is_absolute():
        path = SCRIPT_DIR / path
    return path.resolve()


def create_downloader(args: argparse.Namespace) -> NCCNDownloaderV2:
    config_data = load_config(resolve_config_path(args.config))
    config = build_config(config_data, args)
    downloader = NCCNDownloaderV2(config)
    if getattr(args, "download_dir", None):
        downloader.base_download_dir = Path(config["download_dir"])
        downloader.logs_dir = downloader.base_download_dir / "logs"
        downloader.setup_directories()
    return downloader


def confirm_download(theme_name: str, language_filter: str, cancer_filter: Optional[str]):
    print("\n=== 下载确认 ===")
    print(f"主题: {theme_name}")
    print(f"语言: {NCCNDownloaderV2.language_group_label(language_filter)}")
    print(f"癌种: {cancer_filter or '全部'}")
    choice = input("确认后输入 Y 开始下载，其他键取消: ").strip().lower()
    if choice not in ["y", "yes", "是"]:
        raise KeyboardInterrupt("用户取消下载")


def cmd_download(args: argparse.Namespace) -> int:
    language_filter = NCCNDownloaderV2.normalize_language_filter(args.language or "1")
    theme_key = args.theme or "1"
    if theme_key not in NCCNDownloaderV2.THEMES:
        print(f"无效主题: {theme_key}")
        return 2

    downloader = create_downloader(args)
    if not args.no_auth and not downloader.authenticate():
        print("认证失败，请检查认证信息")
        return 1

    theme = NCCNDownloaderV2.THEMES[theme_key]
    if not args.yes:
        confirm_download(theme.display_name, language_filter, args.cancer)

    success = downloader.download_theme(theme_key, language_filter, args.cancer)
    print(f"\n{'✅' if success else '❌'} 下载完成" if success else f"\n❌ {theme.display_name} 下载失败!")
    return 0 if success else 1


def cmd_list_cancers(args: argparse.Namespace) -> int:
    downloader = create_downloader(args)
    items = downloader._discover_cancer_types_from_page(refresh=args.refresh)
    print(f"共找到 {len(items)} 个癌种:")
    print("0. 全部癌种")
    for i, item in enumerate(items, 1):
        print(f"{i}. {item}")
    return 0


def cmd_interactive(args: argparse.Namespace) -> int:
    # 复用主脚本中的简化交互菜单
    return nccn.main(
        config_path=resolve_config_path(args.config),
        download_dir=getattr(args, "download_dir", None),
    ) or 0


def cmd_convert(args: argparse.Namespace) -> int:
    from nccn_rag import extract_markdown

    rag_config = load_config(resolve_config_path(args.config)).get("rag", {}) or {}
    base_dir = Path(args.download_dir).expanduser().resolve() if args.download_dir else None
    output = extract_markdown(
        input_path=Path(args.input).expanduser().resolve(),
        output_dir=Path(args.output).expanduser().resolve() if args.output else None,
        mode=args.mode or rag_config.get("mineru_mode"),
        language=args.language or rag_config.get("mineru_language"),
        base_dir=base_dir,
        ocr_backend=args.ocr_backend or rag_config.get("ocr_backend"),
        api_key=args.api_key,
        base_url=args.base_url or rag_config.get("deepseek_ocr_base_url"),
        model=args.model or rag_config.get("deepseek_ocr_model"),
        max_pages=(
            args.max_pages
            if args.max_pages is not None
            else rag_config.get("deepseek_ocr_max_pages")
        ),
    )
    print(f"✅ Markdown已生成: {output}")
    return 0


def cmd_translate(args: argparse.Namespace) -> int:
    from nccn_rag import translate_markdown

    rag_config = load_config(resolve_config_path(args.config)).get("rag", {}) or {}
    output = translate_markdown(
        input_path=Path(args.input).expanduser().resolve(),
        output_path=Path(args.output).expanduser().resolve() if args.output else None,
        source=args.source,
        target=args.target,
        api_key=args.api_key,
        base_url=args.base_url or rag_config.get("translate_base_url"),
        model=args.model or rag_config.get("translate_model"),
    )
    print(f"✅ 翻译完成: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ncd",
        description="NCCN指南下载、筛选、Markdown解析与RAG预处理工具",
    )
    parser.add_argument("--config", default="config.json", help="配置文件路径，默认 config.json")
    parser.add_argument("--download-dir", help="下载根目录，默认 nccn_downloads")
    subparsers = parser.add_subparsers(dest="command")

    interactive = subparsers.add_parser("interactive", help="启动简化交互菜单")
    interactive.set_defaults(func=cmd_interactive)

    download = subparsers.add_parser("download", help="下载NCCN指南")
    download.add_argument("--theme", default="1", help="主题键，默认 1=癌症治疗指南")
    download.add_argument("--cancer", help="癌种关键词，支持英文/中文/逗号分隔，例如 breast 或 lung,colorectal")
    download.add_argument("--language", default="1", help="语言：0中文，1英文，2日语/其他，3全部，默认1英文")
    download.add_argument("--yes", "-y", action="store_true", help="跳过确认直接下载")
    download.add_argument("--no-auth", action="store_true", help="跳过认证，仅用于公开页面测试")
    download.set_defaults(func=cmd_download)

    list_cancers = subparsers.add_parser("list-cancers", help="列出NCCN癌种分类")
    list_cancers.add_argument("--refresh", action="store_true", help="强制刷新NCCN癌种列表")
    list_cancers.set_defaults(func=cmd_list_cancers)

    convert = subparsers.add_parser("convert", help="将PDF/图片/URL转为Markdown")
    convert.add_argument("--input", required=True, help="输入PDF/图片/URL")
    convert.add_argument("--output", help="输出文件或目录")
    convert.add_argument("--mode", choices=["flash", "extract"], help="MinerU模式，默认读取 config.json 或 NCCN_MINERU_MODE")
    convert.add_argument("--language", help="MinerU识别语言，默认读取 config.json 或 NCCN_MINERU_LANGUAGE")
    convert.add_argument("--ocr-backend", choices=["mineru", "deepseek-ocr"], help="OCR后端，默认读取 config.json 或 NCCN_OCR_BACKEND")
    convert.add_argument("--api-key", help="DeepSeek-OCR/SiliconFlow API Key，默认读取 SILICONFLOW_API_KEY")
    convert.add_argument("--base-url", help="SiliconFlow/OpenAI-compatible base URL")
    convert.add_argument("--model", help="DeepSeek-OCR模型名")
    convert.add_argument("--max-pages", type=int, help="PDF最多转换页数，0表示全部")
    convert.set_defaults(func=cmd_convert)

    translate = subparsers.add_parser("translate", help="将Markdown英文内容翻译为中文")
    translate.add_argument("--input", required=True, help="输入Markdown文件")
    translate.add_argument("--output", help="输出Markdown文件")
    translate.add_argument("--source", default="en")
    translate.add_argument("--target", default="zh")
    translate.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY"))
    translate.add_argument("--base-url", help="翻译API base URL，默认读取 config.json、OPENAI_BASE_URL 或 SILICONFLOW_BASE_URL")
    translate.add_argument("--model", help="翻译模型，默认读取 config.json、OPENAI_MODEL 或 SILICONFLOW_MODEL")
    translate.set_defaults(func=cmd_translate)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n用户取消操作")
        return 130
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
