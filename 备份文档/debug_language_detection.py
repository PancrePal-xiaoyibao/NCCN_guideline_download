#!/usr/bin/env python3
"""
调试语言检测逻辑
查看为什么其他语言版本没有被正确过滤
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_language_detection():
    """调试语言检测逻辑"""
    print("🔍 调试语言检测逻辑...")
    print("=" * 60)

    try:
        # 导入下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        # 读取配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 测试各种语言检测
        test_cases = [
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026.pdf", "NCCN Guidelines"),
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026-ES.pdf", "Acute Myeloid Leukemia-Spanish"),
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026-CH.pdf", "Chinese"),
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026-FR.pdf", "French"),
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026-JP.pdf", "Japanese"),
            ("https://www.nccn.org/files/content/guidelinespdf/materials/2026/AML-2026-ZH.pdf", "Chinese"),
        ]

        print("🧪 测试语言检测:")
        for pdf_url, link_text in test_cases:
            detected = downloader._detect_pdf_language(pdf_url, link_text)
            should_include = downloader._should_include_pdf(pdf_url, 'english', link_text)

            status = "✅ 包括" if should_include else "❌ 过滤"
            print(f"   {detected:10s} | {status} | {pdf_url}")
            print(f"   {'':12s} | {' '*8} | {link_text}")
            print()

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_language_detection()