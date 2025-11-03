#!/usr/bin/env python3
"""
测试修复后的文件名生成功能
验证从PDF URL提取原始文件名
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_filename_generation():
    """测试修复后的文件名生成功能"""
    print("🧪 测试修复后的文件名生成功能...")
    print("=" * 60)

    try:
        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 测试案例：模拟从NCCN网站提取的真实PDF链接
        test_cases = [
            {
                'title': 'NCCN Guidelines (English)',
                'version_info': '1_2026',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/pain.pdf',
                'expected_prefix': 'pain'
            },
            {
                'title': 'Nausea and Vomiting-English (English)',
                'version_info': '2_2025',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/nausea_vomiting.pdf',
                'expected_prefix': 'nausea_vomiting'
            },
            {
                'title': 'Blood Clots and Cancer-English (English)',
                'version_info': '1_2025',
                'pdf_url': 'https://www.nccn.org/files/content/guidelinespdf/materials/2026/blood_clots_cancer.pdf',
                'expected_prefix': 'blood_clots_cancer'
            },
            {
                'title': 'Fatigue and Cancer-English (English)',
                'version_info': '1_2024',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/fatigue.pdf',
                'expected_prefix': 'fatigue'
            },
            {
                'title': 'Chinese (Chinese)',
                'version_info': '1_2025',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/pain_chinese.pdf',
                'expected_prefix': 'pain_chinese'
            }
        ]

        print("🧪 测试用例:")
        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i}:")
            print(f"   标题: {test_case['title']}")
            print(f"   版本: {test_case['version_info']}")
            print(f"   URL: {test_case['pdf_url']}")
            print(f"   期望前缀: {test_case['expected_prefix']}")

            # 调用增强文件名方法
            enhanced_info = downloader._enhance_pdf_info(
                test_case['title'],
                test_case['version_info'],
                test_case['pdf_url']
            )

            actual_filename = enhanced_info['enhanced_filename']
            actual_title = enhanced_info['title']

            print(f"   实际文件名: {actual_filename}")
            print(f"   实际标题: {actual_title}")

            # 验证文件名是否正确
            expected_filename = f"{test_case['expected_prefix']}_version_{test_case['version_info']}.pdf"
            if actual_filename == expected_filename:
                print(f"   ✅ 通过")
            else:
                print(f"   ❌ 失败")
                print(f"      期望: {expected_filename}")
                all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_url_parsing():
    """测试URL解析功能"""
    print(f"\n🔍 测试URL解析功能:")
    print("=" * 60)

    test_urls = [
        'https://www.nccn.org/professionals/physician_gls/pdf/pain.pdf',
        'https://www.nccn.org/files/content/guidelinespdf/materials/2026/blood_clots_cancer.pdf',
        'https://www.nccn.org/professionals/physician_gls/pdf/fatigue.pdf',
        'https://www.nccn.org/professionals/physician_gls/pdf/nausea_vomiting.pdf'
    ]

    for i, url in enumerate(test_urls, 1):
        print(f"\n📋 URL {i}: {url}")

        try:
            from urllib.parse import urlparse
            import os

            parsed_url = urlparse(url)
            path = parsed_url.path
            filename = os.path.basename(path)

            if filename and '.' in filename:
                file_prefix = os.path.splitext(filename)[0]
                print(f"   解析结果: {filename} -> {file_prefix}")
            else:
                print(f"   解析失败: 无法提取有效文件名")

        except Exception as e:
            print(f"   解析错误: {str(e)}")

if __name__ == "__main__":
    print("🎯 测试修复后的文件名生成功能")
    print("验证从PDF URL提取原始文件名并结合版本信息")
    print("=" * 60)

    success = test_filename_generation()
    test_url_parsing()

    print(f"\n{'='*60}")
    if success:
        print("🎉 所有测试通过！")
        print("✅ 修复后的文件名生成逻辑工作正常")
        print("✅ 能够正确从PDF URL提取原始文件名")
        print("✅ 正确结合版本信息生成增强文件名")
        print("🚀 现在可以重新运行主程序测试了")
    else:
        print("⚠️ 部分测试失败")
        print("🔧 需要进一步调试")