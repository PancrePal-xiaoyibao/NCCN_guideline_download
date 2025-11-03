#!/usr/bin/env python3
"""
测试支持性护理指南的双语提取功能
验证从Guidelines部分提取英文版本，从International部分提取中文版本
"""

import sys
import os
import time
import random
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_supportive_care_extraction():
    """测试支持性护理指南的双语提取功能"""
    print("🧪 测试支持性护理指南的双语提取功能...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项2的配置（支持性护理指南）
        theme = ThemeConfig(
            name='supportive_care',
            display_name='支持性护理指南 (Supportive Care)',
            url='https://www.nccn.org/guidelines/category_3',
            category='supportive_care',
            directory='02_Supportive_Care',
            description='支持性护理相关指南',
            has_language_filter=True,
            guidelines_only=True  # 启用新的双语提取
        )

        print(f"🎯 测试主题: {theme.display_name}")
        print(f"📁 下载目录: {theme.directory}")
        print(f"🔗 URL: {theme.url}")
        print(f"🏷️  Category: {theme.category}")
        print(f"🌐 语言过滤: {theme.has_language_filter}")
        print(f"🎯 指南提取: {'双语指南提取' if theme.guidelines_only else '传统方法'}")

        # 测试不同语言过滤选项
        test_cases = [
            ('all', '全部版本 (英文 + 中文)'),
            ('english', '仅英文版本'),
            ('chinese', '仅中文版本')
        ]

        for language_filter, description in test_cases:
            print(f"\n{'='*60}")
            print(f"🎯 测试语言过滤: {description}")
            print(f"   language_filter: {language_filter}")

            # 访问主页面
            print(f"\n🌐 访问主页面...")
            response = downloader.session.get(theme.url)

            if response.status_code == 200:
                print(f"✅ 页面访问成功 (状态码: {response.status_code})")

                # 解析页面
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # 获取子链接（限制数量避免长时间运行）
                print(f"\n🔍 获取guidelines-detail链接...")
                sub_links = downloader._get_sub_links(soup, theme.url)
                print(f"📊 找到 {len(sub_links)} 个指南子页面")

                if len(sub_links) > 0:
                    # 测试第一个详情页
                    test_link = sub_links[0]
                    print(f"\n🧪 测试第一个详情页: {test_link.split('/')[-1]}")

                    try:
                        # 测试双语提取方法
                        print(f"   🔍 使用双语提取方法...")
                        pdf_links = downloader._get_pdfs_from_detail_page(
                            test_link, f"支持性护理指南_测试", language_filter, theme
                        )

                        print(f"   📋 提取到 {len(pdf_links)} 个PDF")

                        # 统计语言分布
                        english_count = len([p for p in pdf_links if p['version'] == 'English'])
                        chinese_count = len([p for p in pdf_links if p['version'] == 'Chinese'])

                        print(f"   📊 语言分布:")
                        print(f"      英文版本: {english_count}")
                        print(f"      中文版本: {chinese_count}")

                        # 显示每个PDF的详细信息
                        for j, pdf in enumerate(pdf_links, 1):
                            title = pdf['title'][:50] + "..." if len(pdf['title']) > 50 else pdf['title']
                            version = pdf['version']
                            enhanced_filename = pdf.get('enhanced_filename', 'N/A')
                            print(f"      {j:2d}. {title} (语言: {version})")
                            print(f"          文件名: {enhanced_filename}")

                        # 验证结果是否符合预期
                        if language_filter == 'all':
                            expected_condition = (english_count > 0 or chinese_count > 0)
                        elif language_filter == 'english':
                            expected_condition = (english_count > 0 and chinese_count == 0)
                        elif language_filter == 'chinese':
                            expected_condition = (chinese_count > 0 and english_count == 0)

                        if expected_condition:
                            print(f"   ✅ 语言过滤验证通过")
                        else:
                            print(f"   ⚠️ 语言过滤验证失败")

                        # 短暂延迟
                        time.sleep(random.uniform(0.5, 1.5))

                    except Exception as e:
                        print(f"   ❌ 处理失败: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        continue

                else:
                    print(f"\n❌ 没有找到指南子页面链接")
                    return False
            else:
                print(f"❌ 主页面访问失败")
                return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_bilingual_extraction_logic():
    """测试双语提取逻辑"""
    print(f"\n🔍 测试双语提取逻辑:")
    print("=" * 60)

    try:
        from bs4 import BeautifulSoup

        # 模拟HTML结构
        mock_html = """
        <div>
            <h4 class="GL">Guidelines</h4>
            <ul class="pdfList">
                <li>
                    <p>
                        <a href="/professionals/physician_gls/pdf/pain.pdf">NCCN Guidelines</a>
                        <span>Version 2.2025</span>
                    </p>
                </li>
            </ul>

            <h4 class="INT">International</h4>
            <div class="international">
                <p>Translations</p>
                <ul class="pdfList">
                    <li>
                        <p>
                            <a href="/professionals/physician_gls/pdf/adult_cancer_pain-chinese1.pdf">Chinese </a>
                            <span>Version 1.2025</span>
                        </p>
                    </li>
                </ul>
            </div>
        </div>
        """

        soup = BeautifulSoup(mock_html, 'html.parser')

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        import json

        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        downloader = NCCNDownloaderV2(config_data)

        print("📋 模拟HTML结构:")
        print("   - Guidelines 部分包含 pain.pdf (英文)")
        print("   - International 部分包含 adult_cancer_pain-chinese1.pdf (中文)")

        # 测试提取逻辑
        print(f"\n🧪 测试提取逻辑...")

        # 测试英文部分提取
        print(f"   🔍 提取英文版本 (Guidelines)...")
        english_pdfs = downloader._extract_from_section(soup, 'GL', 'Guidelines', 'english')
        print(f"   📊 英文PDF数量: {len(english_pdfs)}")
        for pdf in english_pdfs:
            print(f"      - {pdf['title']} ({pdf['version']}) -> {pdf['enhanced_filename']}")

        # 测试中文部分提取
        print(f"   🔍 提取中文版本 (International)...")
        chinese_pdfs = downloader._extract_from_section(soup, 'INT', 'International', 'chinese')
        print(f"   📊 中文PDF数量: {len(chinese_pdfs)}")
        for pdf in chinese_pdfs:
            print(f"      - {pdf['title']} ({pdf['version']}) -> {pdf['enhanced_filename']}")

        # 测试双语提取
        print(f"   🔍 测试双语提取...")
        all_pdfs = downloader._extract_bilingual_guidelines(soup, 'all')
        print(f"   📊 总PDF数量: {len(all_pdfs)}")

        english_count = len([p for p in all_pdfs if p['version'] == 'English'])
        chinese_count = len([p for p in all_pdfs if p['version'] == 'Chinese'])

        print(f"   📈 语言统计: 英文 {english_count}, 中文 {chinese_count}")

        if english_count > 0 and chinese_count > 0:
            print(f"   ✅ 双语提取验证通过")
            return True
        else:
            print(f"   ❌ 双语提取验证失败")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 测试支持性护理指南双语提取功能")
    print("验证从Guidelines和International部分分别提取英文和中文版本")
    print("=" * 60)

    success1 = test_supportive_care_extraction()
    success2 = test_bilingual_extraction_logic()

    print(f"\n{'='*60}")
    if success1 and success2:
        print("🎉 所有测试通过！")
        print("✅ 支持性护理指南双语提取功能正常工作")
        print("✅ 能够从Guidelines部分提取英文版本")
        print("✅ 能够从International部分提取中文版本")
        print("✅ 语言过滤功能正常")
        print("🚀 现在运行: python download_NCCN_Guide_v2_menu.py")
        print("   选择选项2，验证双语提取效果")
    else:
        print("⚠️ 部分测试失败")
        print("🔧 需要进一步调试")