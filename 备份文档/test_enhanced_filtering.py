#!/usr/bin/env python3
"""
测试增强后的过滤逻辑
验证能否正确过滤掉不需要的文件，只保留核心指南
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_filtering():
    """测试增强后的过滤逻辑"""
    print("🧪 测试增强后的过滤逻辑...")
    print("=" * 60)

    try:
        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 测试用例：模拟从日志中看到的不需要的文件
        test_cases = [
            # 应该被过滤掉的文件
            {
                'url': '/files/content/guidelinespdf/materials/2026/basic-framework.pdf',
                'text': 'Basic Framework (English) (English)',
                'expected': False,
                'reason': 'Framework文件'
            },
            {
                'url': '/files/content/guidelinespdf/materials/2026/core-framework.pdf',
                'text': 'Core Framework (English) (English)',
                'expected': False,
                'reason': 'Framework文件'
            },
            {
                'url': '/files/content/guidelinespdf/materials/2026/enhanced-framework.pdf',
                'text': 'Enhanced Framework (English) (English)',
                'expected': False,
                'reason': 'Framework文件'
            },
            {
                'url': '/files/content/conference/2026-exhibitor-prospectus.pdf',
                'text': '2026 Annual Conference Exhibitor Prospectus (English)',
                'expected': False,
                'reason': '会议文件'
            },
            {
                'url': '/files/content/conference/2025-lung-congress.pdf',
                'text': '2025 Lung Congress Exhibitor Prospectus (English)',
                'expected': False,
                'reason': '会议文件'
            },
            {
                'url': '/professionals/physician_gls/pdf/nausea-vomiting-spanish.pdf',
                'text': 'Nausea and Vomiting-Spanish (Spanish)',
                'expected': False,
                'reason': 'Spanish版本'
            },
            {
                'url': '/professionals/physician_gls/pdf/blood-clots-arabic.pdf',
                'text': 'Blood Clots and Cancer-Arabic (Arabic)',
                'expected': False,
                'reason': 'Arabic版本'
            },
            {
                'url': '/professionals/physician_gls/pdf/distress-hindi.pdf',
                'text': 'Distress During Cancer Care-Hindi (Hindi)',
                'expected': False,
                'reason': 'Hindi版本'
            },
            {
                'url': '/professionals/physician_gls/pdf/nausea-vomiting-portuguese.pdf',
                'text': 'Nausea and Vomiting-Portuguese (English)',
                'expected': False,
                'reason': 'Portuguese版本'
            },
            {
                'url': '/professionals/physician_gls/pdf/user-guide.pdf',
                'text': 'View Chemotherapy Order Templates User Guide (English)',
                'expected': False,
                'reason': '用户指南'
            },
            {
                'url': '/professionals/physician_gls/pdf/mena-region.pdf',
                'text': 'Middle East & North Africa (MENA) (English) (English)',
                'expected': False,
                'reason': '地区性文件'
            },
            {
                'url': '/professionals/physician_gls/pdf/africa-region.pdf',
                'text': 'Sub-Saharan Africa (English) (English)',
                'expected': False,
                'reason': '地区性文件'
            },

            # 应该被保留的文件
            {
                'url': '/professionals/physician_gls/pdf/pain.pdf',
                'text': 'NCCN Guidelines (English)',
                'expected': True,
                'reason': '核心英文指南'
            },
            {
                'url': '/professionals/physician_gls/pdf/nausea-vomiting.pdf',
                'text': 'Nausea and Vomiting-English (English)',
                'expected': True,
                'reason': '核心英文指南'
            },
            {
                'url': '/professionals/physician_gls/pdf/blood-clots.pdf',
                'text': 'Blood Clots and Cancer-English (English)',
                'expected': True,
                'reason': '核心英文指南'
            },
            {
                'url': '/professionals/physician_gls/pdf/fatigue.pdf',
                'text': 'Fatigue and Cancer-English (English)',
                'expected': True,
                'reason': '核心英文指南'
            },
            {
                'url': '/professionals/physician_gls/pdf/distress.pdf',
                'text': 'Distress During Cancer Care-English (English)',
                'expected': True,
                'reason': '核心英文指南'
            },

            # 中文版本（在all模式下应该保留）
            {
                'url': '/professionals/physician_gls/pdf/pain-chinese.pdf',
                'text': 'Chinese (Chinese)',
                'expected': 'depends',  # 取决于语言过滤设置
                'reason': '中文版本'
            }
        ]

        # 测试不同语言过滤设置
        language_filters = [
            ('english', '英文版本过滤'),
            ('all', '全部版本过滤')
        ]

        total_tests = 0
        passed_tests = 0

        for lang_filter, filter_desc in language_filters:
            print(f"\n📋 测试 {filter_desc} ({lang_filter}):")
            print("-" * 40)

            for i, test_case in enumerate(test_cases, 1):
                # 跳过中文版本的依赖测试
                if test_case['expected'] == 'depends':
                    continue

                result = downloader._should_include_pdf(
                    test_case['url'],
                    lang_filter,
                    test_case['text']
                )

                total_tests += 1
                is_correct = (result == test_case['expected'])

                if is_correct:
                    passed_tests += 1
                    status = "✅ 通过"
                else:
                    status = "❌ 失败"

                print(f"  {i:2d}. {test_case['reason'][:20]:<20} {test_case['text'][:30]:<30} -> {status}")

                if not is_correct:
                    print(f"      期望: {test_case['expected']}, 实际: {result}")

        # 特别测试中文版本
        print(f"\n📋 测试中文版本处理:")
        print("-" * 40)
        chinese_test = test_cases[-1]  # 最后一个是中文版本测试

        for lang_filter, filter_desc in language_filters:
            result = downloader._should_include_pdf(
                chinese_test['url'],
                lang_filter,
                chinese_test['text']
            )

            total_tests += 1

            if lang_filter == 'all':
                expected = True
                is_correct = (result == expected)
            elif lang_filter == 'english':
                expected = False
                is_correct = (result == expected)

            if is_correct:
                passed_tests += 1
                status = "✅ 通过"
            else:
                status = "❌ 失败"

            print(f"  {filter_desc}: {chinese_test['text'][:30]:<30} -> {status}")
            if not is_correct:
                print(f"      期望: {expected}, 实际: {result}")

        print(f"\n{'='*60}")
        print(f"📊 测试总结:")
        print(f"   总测试数: {total_tests}")
        print(f"   通过数量: {passed_tests}")
        print(f"   失败数量: {total_tests - passed_tests}")
        print(f"   成功率: {passed_tests/total_tests*100:.1f}%")

        return passed_tests == total_tests

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 测试增强后的过滤逻辑")
    print("验证能否正确过滤掉不需要的文件，只保留核心指南")
    print("=" * 60)

    success = test_enhanced_filtering()

    print(f"\n{'='*60}")
    if success:
        print("🎉 所有测试通过！")
        print("✅ 新的过滤逻辑能正确识别和过滤不需要的文件")
        print("✅ 只保留核心的NCCN Guidelines文件")
        print("✅ 正确过滤Spanish、Framework、地区性文件等")
        print("🚀 现在重新运行: python download_NCCN_Guide_v2_menu.py")
        print("   选择选项2，验证新的过滤效果")
    else:
        print("⚠️ 部分测试失败")
        print("🔧 需要进一步调试过滤逻辑")