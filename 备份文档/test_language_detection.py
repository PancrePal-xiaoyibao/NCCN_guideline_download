#!/usr/bin/env python3
"""
测试修复后的语言检测和过滤逻辑
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from download_NCCN_Guide_v2_menu import NCCNDownloaderV2

def test_language_detection():
    """测试语言检测和过滤"""
    print("🧪 测试修复后的语言检测和过滤逻辑...")
    print("=" * 60)

    # 创建临时实例来测试语言检测方法
    config = {'auth_method': 'cookie'}
    downloader = NCCNDownloaderV2(config)

    # 测试语言检测
    test_cases = [
        {
            'url': '/patients/guidelines/content/PDF/all-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult)',
            'expected': 'English'
        },
        {
            'url': '/patients/guidelines/content/PDF/ALL-es-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult) - Spanish',
            'expected': 'Spanish'
        },
        {
            'url': '/patients/guidelines/content/PDF/bladder-zh-patient.pdf',
            'text': 'Bladder Cancer - Chinese',
            'expected': 'Chinese'
        },
        {
            'url': '/patients/guidelines/content/PDF/anal-patient.pdf',
            'text': 'Anal Cancer',
            'expected': 'English'
        }
    ]

    print("🔍 测试语言检测:")
    for i, test in enumerate(test_cases, 1):
        detected = downloader._detect_pdf_language(test['url'], test['text'])
        status = "✅" if detected == test['expected'] else "❌"
        print(f"   {i}. {status} {test['text'][:30]}...")
        print(f"      URL: {test['url']}")
        print(f"      期望: {test['expected']}, 检测: {detected}")

    print(f"\n🔍 测试语言过滤:")
    # 测试语言过滤
    filter_tests = [
        {
            'url': '/patients/guidelines/content/PDF/all-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult)',
            'filter': 'all',
            'expected': True
        },
        {
            'url': '/patients/guidelines/content/PDF/all-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult)',
            'filter': 'english',
            'expected': True
        },
        {
            'url': '/patients/guidelines/content/PDF/ALL-es-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult) - Spanish',
            'filter': 'english',
            'expected': False
        },
        {
            'url': '/patients/guidelines/content/PDF/ALL-es-patient.pdf',
            'text': 'Acute Lymphoblastic Leukemia (adult) - Spanish',
            'filter': 'all',
            'expected': True
        }
    ]

    for i, test in enumerate(filter_tests, 1):
        result = downloader._should_include_pdf(test['url'], test['filter'], test['text'])
        status = "✅" if result == test['expected'] else "❌"
        print(f"   {i}. {status} 过滤 '{test['filter']}': {test['text'][:30]}...")
        print(f"      期望: {test['expected']}, 结果: {result}")

    print(f"\n📋 当前NCCN患者指南的语言分布:")
    print(f"   • 英文版本 (English): 主要版本")
    print(f"   • 西班牙语版本 (Spanish): 部分指南可用")
    print(f"   • 中文版本 (Chinese): 当前测试发现较少或暂无")

    print(f"\n💡 建议:")
    print(f"   • 选择'全部版本'来下载可用的所有语言版本")
    print(f"   • 选择'仅英文版本'获取最完整的内容")
    print(f"   • '仅中文版本'可能找到的文件较少（取决于NCCN的实际提供情况）")

if __name__ == "__main__":
    test_language_detection()