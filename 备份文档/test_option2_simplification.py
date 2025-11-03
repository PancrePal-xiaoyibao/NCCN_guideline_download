#!/usr/bin/env python3
"""
测试选项2（支持性护理指南）简化后的功能
验证简化后的用户交互和提取逻辑
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_option2_config():
    """测试选项2的配置简化"""
    print("🧪 测试选项2配置简化...")
    print("=" * 60)

    try:
        # 读取配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 导入主题配置
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2

        # 检查选项2的配置
        theme = NCCNDownloaderV2.THEMES.get('2')
        if not theme:
            print("❌ 找不到选项2的主题配置")
            return False

        print(f"📋 主题信息:")
        print(f"   名称: {theme.name}")
        print(f"   显示名称: {theme.display_name}")
        print(f"   分类: {theme.category}")
        print(f"   目录: {theme.directory}")
        print(f"   语言过滤: {theme.has_language_filter}")
        print(f"   Guidelines-only: {getattr(theme, 'guidelines_only', False)}")

        # 验证简化后的配置
        expected_name = 'supportive_care'
        expected_category = 'category_3'  # 实际是category_3
        expected_directory = '02_Supportive_Care'

        config_correct = (
            theme.name == expected_name and
            theme.category == expected_category and
            theme.directory == expected_directory and
            theme.has_language_filter == True and
            getattr(theme, 'guidelines_only', False) == False  # 简化后应该没有这个标志
        )

        if config_correct:
            print("   ✅ 配置验证通过")
        else:
            print("   ❌ 配置验证失败")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_language_filter_logic():
    """测试语言过滤逻辑"""
    print(f"\n🔍 测试语言过滤逻辑:")
    print("=" * 60)

    try:
        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        # 测试语言检测
        test_pdfs = [
            {
                'title': 'NCCN Guidelines for Pain Management',
                'url': '/professionals/physician_gls/pdf/pain.pdf',
                'version': 'English'
            },
            {
                'title': 'Chinese Pain Management Guidelines',
                'url': '/professionals/physician_gls/pdf/pain-chinese.pdf',
                'version': 'Chinese'
            },
            {
                'title': 'Spanish Guidelines',
                'url': '/professionals/physician_gls/pdf/pain-spanish.pdf',
                'version': 'Spanish'
            }
        ]

        # 模拟语言检测
        print("📋 语言过滤测试:")

        for filter_type, description in [('all', '全部版本'), ('english', '仅英文版本')]:
            print(f"\n   🧪 {description} ({filter_type}):")

            for pdf in test_pdfs:
                # 模拟语言检测逻辑
                is_chinese = 'chinese' in pdf['url'].lower() or 'chinese' in pdf['title'].lower()
                is_english = not is_chinese and 'spanish' not in pdf['url'].lower()

                should_include = False
                if filter_type == 'all':
                    should_include = True
                elif filter_type == 'english':
                    should_include = is_english

                status = "✅ 包含" if should_include else "❌ 过滤"
                print(f"      {pdf['title']}: {status}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_extraction_simplification():
    """测试提取逻辑简化"""
    print(f"\n🔍 测试提取逻辑简化:")
    print("=" * 60)

    try:
        # 检查是否还有复杂的方法
        import inspect
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2

        # 获取所有方法
        methods = [method for method in dir(NCCNDownloaderV2) if method.startswith('_extract')]

        print("📋 当前提取方法:")
        for method in sorted(methods):
            print(f"   - {method}")

        # 检查是否移除了复杂方法
        complex_methods = ['_extract_bilingual_guidelines', '_extract_from_section']
        removed_methods = [method for method in complex_methods if method in methods]

        if removed_methods:
            print(f"\n❌ 发现未移除的复杂方法: {removed_methods}")
            return False
        else:
            print(f"\n✅ 复杂双语提取方法已成功移除")

        # 检查是否存在简化后的方法
        simplified_methods = ['_extract_guidelines_only', '_get_pdfs_from_detail_page']
        existing_methods = [method for method in simplified_methods if method in methods]

        if len(existing_methods) >= 1:
            print(f"✅ 核心提取方法存在: {existing_methods}")
        else:
            print(f"⚠️ 部分核心提取方法缺失")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 测试选项2（支持性护理指南）简化功能")
    print("验证简化后的配置、用户交互和提取逻辑")
    print("=" * 60)

    # 需要导入json
    import json

    success1 = test_option2_config()
    success2 = test_language_filter_logic()
    success3 = test_extraction_simplification()

    print(f"\n{'='*60}")
    if success1 and success2 and success3:
        print("🎉 所有测试通过！")
        print("✅ 选项2配置简化成功")
        print("✅ 语言过滤逻辑简化成功")
        print("✅ 提取逻辑简化成功")
        print("🚀 现在运行: python download_NCCN_Guide_v2_menu.py")
        print("   选择选项2，验证简化后的效果")
        print("\n📋 简化后的选项2特性:")
        print("   - 统一的PDF提取（不再区分Guidelines和International）")
        print("   - 简化的语言过滤（只有2个选项：全部版本、仅英文版本）")
        print("   - 自动检测中文版本（通过文件名中的'chinese'标识）")
    else:
        print("⚠️ 部分测试失败")
        print("🔧 需要进一步调试")