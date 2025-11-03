#!/usr/bin/env python3
"""
测试新的Guidelines-only提取功能
验证只提取"Guidelines"部分的核心指南，并包含版本信息
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_guidelines_only_extraction():
    """测试Guidelines-only提取功能"""
    print("🧪 测试新的Guidelines-only提取功能...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项1的配置（使用新的guidelines_only=True）
        theme = ThemeConfig(
            name='cancer_treatment',
            display_name='癌症治疗指南英文版 (Treatment by Cancer Type - English Only)',
            url='https://www.nccn.org/guidelines/category_1',
            category='category_1',
            directory='01_Cancer_Treatment',
            description='按癌症类型分类的治疗指南（英文版）',
            has_language_filter=True,
            guidelines_only=True  # 启用新的Guidelines-only提取
        )

        print(f"🎯 测试主题: {theme.display_name}")
        print(f"📁 下载目录: {theme.directory}")
        print(f"🔗 URL: {theme.url}")
        print(f"🏷️  Category: {theme.category}")
        print(f"🌐 语言过滤: {theme.has_language_filter}")
        print(f"🎯 指南提取: {'Guidelines-only' if theme.guidelines_only else '传统方法'}")

        # 模拟用户交互：英文版本
        language_filter = 'english'
        print(f"\n🎯 语言过滤: {language_filter}")

        # 访问主页面
        print(f"\n🌐 访问主页面...")
        response = downloader.session.get(theme.url)

        if response.status_code == 200:
            print(f"✅ 页面访问成功 (状态码: {response.status_code})")

            # 解析页面
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # 测试子链接获取（限制数量避免长时间运行）
            print(f"\n🔍 获取guidelines-detail链接...")
            sub_links = downloader._get_sub_links(soup, theme.url)
            print(f"📊 找到 {len(sub_links)} 个指南子页面")

            if len(sub_links) > 0:
                # 测试前2个详情页
                test_links = sub_links[:2]
                print(f"\n🧪 测试前2个详情页的Guidelines-only提取效果...")

                all_pdfs = []

                for i, sub_url in enumerate(test_links, 1):
                    print(f"\n📄 [{i}/2] 测试详情页: {sub_url.split('/')[-1]}")

                    try:
                        # 测试新的Guidelines-only提取方法
                        print(f"   🔍 使用指南-only方法提取...")
                        pdf_links = downloader._get_pdfs_from_detail_page(
                            sub_url, f"指南_{i}", language_filter, theme
                        )

                        print(f"   📋 提取到 {len(pdf_links)} 个核心PDF")

                        # 显示每个PDF的详细信息
                        for j, pdf in enumerate(pdf_links, 1):
                            title = pdf['title'][:50] + "..." if len(pdf['title']) > 50 else pdf['title']
                            version = pdf['version']
                            enhanced_filename = pdf.get('enhanced_filename', 'N/A')
                            print(f"      {j:2d}. {title} (语言: {version})")
                            print(f"          文件名: {enhanced_filename}")

                            all_pdfs.append(pdf)

                        # 短暂延迟
                        time.sleep(random.uniform(0.5, 1.5))

                    except Exception as e:
                        print(f"   ⚠️ 处理失败: {str(e)}")
                        continue

                print(f"\n📊 Guidelines-only提取结果统计:")
                print(f"   测试详情页数: {len(test_links)}")
                print(f"   核心PDF总数: {len(all_pdfs)}")

                # 验证增强文件名格式
                enhanced_count = 0
                version_info_count = 0

                for pdf in all_pdfs:
                    enhanced_filename = pdf.get('enhanced_filename', '')
                    if enhanced_filename and 'version_' in enhanced_filename:
                        enhanced_count += 1
                    if 'version_' not in (pdf.get('original_filename', '')):
                        version_info_count += 1

                print(f"   包含增强文件名的PDF: {enhanced_count}")
                print(f"   需要版本信息的PDF: {version_info_count}")

                # 验证语言过滤
                non_english_detected = []
                for pdf in all_pdfs:
                    if pdf['version'] != 'English':
                        non_english_detected.append(pdf)

                if len(non_english_detected) == 0:
                    print(f"\n✅ 语言过滤成功！没有发现其他语言版本的PDF")
                else:
                    print(f"\n⚠️ 发现 {len(non_english_detected)} 个其他语言PDF:")
                    for pdf in non_english_detected[:3]:  # 只显示前3个
                        title = pdf['title'][:50] + "..." if len(pdf['title']) > 50 else pdf['title']
                        print(f"   ⚠️ {title} (语言: {pdf['version']})")

                return len(all_pdfs) > 0

            else:
                print(f"\n❌ 没有找到指南子页面链接")
                return False
        else:
            print(f"❌ 主页面访问失败")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_guidelines_only_changes():
    """显示Guidelines-only提取的修改内容"""
    print(f"\n📋 Guidelines-only提取修改总结:")
    print("=" * 60)

    print(f"🔄 修改前:")
    print(f"   • 提取页面上的所有PDF链接")
    print(f"   • 包含各种附加文件（框架、模板、工具等）")
    print(f"   • 文件名中没有版本信息")

    print(f"\n⚡ 修改后:")
    print(f"   • 只提取'Guidelines'部分的核心指南PDF")
    print(f"   • 忽略其他附加文件和工具")
    print(f"   • 自动检测和添加版本信息到文件名")
    print(f"   • 生成更有意义的文件名格式")

    print(f"\n🎯 关键改进:")
    print(f"   ✅ 新增 _extract_guidelines_only() 方法")
    print(f"   ✅ 查找 <h4 class=\"GL\">Guidelines</h4> 标题")
    print(f"   ✅ 提取 Guidelines 部分下的 pdfList 元素")
    print(f"   ✅ 新增 _extract_version_info() 方法提取版本")
    print(f"   ✅ 新增 _enhance_pdf_info() 方法生成增强文件名")
    print(f"   ✅ 文件名格式: [prefix]_version_1_2026.pdf")

if __name__ == "__main__":
    import json

    result = test_guidelines_only_extraction()
    show_guidelines_only_changes()

    print(f"\n{'='*60}")
    if result:
        print("🎉 Guidelines-only提取功能测试成功！")
        print("✅ 现在选项1将：")
        print("   • 只提取Guidelines部分的核心指南")
        print("   • 自动过滤其他附加文件")
        print("   • 添加版本信息到文件名")
        print("   • 只下载英文版本")
        print("🚀 请测试: python download_NCCN_Guide_v2_menu.py")
        print("   选择选项1，验证新的Guidelines-only提取效果")
    else:
        print("⚠️ Guidelines-only提取测试未通过")
        print("🔧 需要进一步调试")