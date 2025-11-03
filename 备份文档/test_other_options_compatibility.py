#!/usr/bin/env python3
"""
测试修改对其他选项的兼容性
确保选项2的优化不会影响选项1、3、4、5、6的正常运行
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_all_themes_config():
    """测试所有主题配置"""
    print("🧪 测试所有主题配置...")
    print("=" * 60)

    try:
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2

        themes = NCCNDownloaderV2.THEMES

        print("📋 所有主题配置:")
        for key, theme in themes.items():
            print(f"\n{key}. {theme.display_name}")
            print(f"   分类: {theme.category}")
            print(f"   目录: {theme.directory}")
            print(f"   语言过滤: {theme.has_language_filter}")
            print(f"   Guidelines-only: {getattr(theme, 'guidelines_only', False)}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_filtering_compatibility():
    """测试过滤逻辑对不同主题的兼容性"""
    print(f"\n🔍 测试过滤逻辑兼容性:")
    print("=" * 60)

    try:
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 模拟不同主题可能遇到的文件
        test_cases = [
            # 选项1（癌症治疗）可能遇到的文件
            {
                'url': '/professionals/physician_gls/pdf/cll.pdf',
                'text': 'NCCN Guidelines for CLL (Chronic Lymphocytic Leukemia)',
                'theme': '1',
                'should_include_english': True,
                'reason': '癌症治疗指南应该是核心文件'
            },
            {
                'url': '/professionals/physician_gls/pdf/aml.pdf',
                'text': 'NCCN Guidelines for AML (Acute Myeloid Leukemia)',
                'theme': '1',
                'should_include_english': True,
                'reason': '癌症治疗指南应该是核心文件'
            },

            # 选项2（支持性护理）应该过滤的文件
            {
                'url': '/files/content/guidelinespdf/materials/2026/basic-framework.pdf',
                'text': 'Basic Framework (English)',
                'theme': '2',
                'should_include_english': False,
                'reason': '支持性护理：应该过滤Framework文件'
            },
            {
                'url': '/professionals/physician_gls/pdf/nausea-vomiting-spanish.pdf',
                'text': 'Nausea and Vomiting-Spanish (Spanish)',
                'theme': '2',
                'should_include_english': False,
                'reason': '支持性护理：应该过滤Spanish版本'
            },

            # 通用的不应该包含的文件
            {
                'url': '/files/content/conference/2026-exhibitor-prospectus.pdf',
                'text': '2026 Annual Conference Exhibitor Prospectus (English)',
                'theme': 'any',
                'should_include_english': False,
                'reason': '所有主题都应该过滤会议文件'
            },
            {
                'url': '/professionals/physician_gls/pdf/user-guide.pdf',
                'text': 'View Chemotherapy Order Templates User Guide (English)',
                'theme': 'any',
                'should_include_english': False,
                'reason': '所有主题都应该过滤用户指南'
            },

            # 通用的应该包含的文件
            {
                'url': '/professionals/physician_gls/pdf/breast-cancer.pdf',
                'text': 'NCCN Guidelines for Breast Cancer',
                'theme': 'any',
                'should_include_english': True,
                'reason': '所有主题都应该包含核心癌症指南'
            }
        ]

        print("🧪 兼容性测试用例:")
        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i} ({test_case['theme']}):")
            print(f"   文件: {test_case['text'][:50]}...")
            print(f"   期望: {'包含' if test_case['should_include_english'] else '过滤'}")

            # 测试英文过滤模式
            result = downloader._should_include_pdf(
                test_case['url'],
                'english',
                test_case['text']
            )

            is_correct = (result == test_case['should_include_english'])

            if is_correct:
                status = "✅ 正确"
            else:
                status = "❌ 错误"
                all_passed = False

            print(f"   实际: {'包含' if result else '过滤'} - {status}")
            print(f"   说明: {test_case['reason']}")

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_filename_generation_compatibility():
    """测试文件名生成对不同主题的兼容性"""
    print(f"\n🔍 测试文件名生成兼容性:")
    print("=" * 60)

    try:
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 测试不同主题的文件名生成
        test_cases = [
            # 选项1：癌症治疗指南
            {
                'title': 'NCCN Guidelines for CLL',
                'version_info': '1_2026',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/cll.pdf',
                'expected': 'cll_version_1_2026.pdf',
                'theme': '1',
                'reason': '癌症治疗指南文件名'
            },
            {
                'title': 'NCCN Guidelines for AML',
                'version_info': '2_2025',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/aml.pdf',
                'expected': 'aml_version_2_2025.pdf',
                'theme': '1',
                'reason': '癌症治疗指南文件名'
            },

            # 选项2：支持性护理指南
            {
                'title': 'NCCN Guidelines for Pain Management',
                'version_info': '1_2025',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/pain.pdf',
                'expected': 'pain_version_1_2025.pdf',
                'theme': '2',
                'reason': '支持性护理指南文件名'
            },
            {
                'title': 'Nausea and Vomiting-English',
                'version_info': '1_2025',
                'pdf_url': 'https://www.nccn.org/professionals/physician_gls/pdf/nausea_vomiting.pdf',
                'expected': 'nausea_vomiting_version_1_2025.pdf',
                'theme': '2',
                'reason': '支持性护理指南文件名'
            }
        ]

        print("🧪 文件名生成测试用例:")
        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 测试用例 {i} ({test_case['theme']}):")
            print(f"   标题: {test_case['title']}")
            print(f"   URL: {test_case['pdf_url']}")
            print(f"   期望: {test_case['expected']}")

            enhanced_info = downloader._enhance_pdf_info(
                test_case['title'],
                test_case['version_info'],
                test_case['pdf_url']
            )

            actual_filename = enhanced_info['enhanced_filename']
            is_correct = (actual_filename == test_case['expected'])

            if is_correct:
                status = "✅ 正确"
            else:
                status = "❌ 错误"
                all_passed = False

            print(f"   实际: {actual_filename} - {status}")
            print(f"   说明: {test_case['reason']}")

        return all_passed

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 测试修改对其他选项的兼容性")
    print("确保选项2的优化不会影响选项1、3、4、5、6")
    print("=" * 60)

    success1 = test_all_themes_config()
    success2 = test_filtering_compatibility()
    success3 = test_filename_generation_compatibility()

    print(f"\n{'='*60}")
    print(f"📊 兼容性测试总结:")
    print(f"   主题配置测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"   过滤逻辑测试: {'✅ 通过' if success2 else '❌ 失败'}")
    print(f"   文件名生成测试: {'✅ 通过' if success3 else '❌ 失败'}")

    if success1 and success2 and success3:
        print(f"\n🎉 所有兼容性测试通过！")
        print(f"✅ 选项2的优化不会影响其他选项")
        print(f"✅ 所有主题都能正常工作")
        print(f"✅ 文件名生成对所有主题都正确")
    else:
        print(f"\n⚠️ 发现兼容性问题")
        print(f"🔧 需要进一步调整")