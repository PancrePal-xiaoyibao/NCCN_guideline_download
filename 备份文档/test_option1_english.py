#!/usr/bin/env python3
"""
测试选项1：癌症治疗指南英文版
验证语言过滤是否正常工作，只下载英文版本
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_option1_english():
    """测试选项1：癌症治疗指南英文版功能"""
    print("🧪 测试选项1：癌症治疗指南英文版...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项1的配置（与主程序中的一致）
        theme = ThemeConfig(
            name='cancer_treatment',
            display_name='癌症治疗指南英文版 (Treatment by Cancer Type - English Only)',
            url='https://www.nccn.org/guidelines/category_1',
            category='category_1',
            directory='01_Cancer_Treatment',
            description='按癌症类型分类的治疗指南（英文版）',
            has_language_filter=True
        )

        print(f"🎯 测试主题: {theme.display_name}")
        print(f"📁 下载目录: {theme.directory}")
        print(f"🔗 URL: {theme.url}")
        print(f"🏷️  Category: {theme.category}")
        print(f"🌐 语言过滤: {theme.has_language_filter}")

        # 模拟用户交互：直接设置英文版本
        print(f"\n🎯 模拟用户选择: 仅英文版本")
        language_filter = 'english'

        # 测试网页访问和解析
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
                # 测试前3个详情页
                test_links = sub_links[:3]
                print(f"\n🧪 测试前3个详情页的语言过滤效果...")

                all_pdfs = []
                english_pdfs = []

                for i, sub_url in enumerate(test_links, 1):
                    print(f"\n📄 [{i}/3] 测试详情页: {sub_url.split('/')[-1]}")

                    try:
                        # 获取PDF链接（带语言过滤）
                        pdf_links = downloader._get_pdfs_from_detail_page(
                            sub_url, f"指南_{i}", language_filter
                        )

                        print(f"   📋 找到 {len(pdf_links)} 个PDF（英文版本）")
                        all_pdfs.extend(pdf_links)

                        # 显示每个PDF的标题和语言
                        for pdf in pdf_links:
                            title = pdf['title'][:50] + "..." if len(pdf['title']) > 50 else pdf['title']
                            print(f"      ✅ {title}")

                        # 短暂延迟
                        time.sleep(random.uniform(0.5, 1.5))

                    except Exception as e:
                        print(f"   ⚠️ 处理失败: {str(e)}")
                        continue

                print(f"\n📊 过滤结果统计:")
                print(f"   测试详情页数: {len(test_links)}")
                print(f"   英文PDF总数: {len(all_pdfs)}")

                # 验证是否包含其他语言版本
                non_english_detected = []
                for pdf in all_pdfs:
                    pdf_url = pdf['url'].lower()
                    pdf_title = pdf['title'].lower()
                    # 检查是否包含其他语言标识符
                    other_languages = ['spanish', 'chinese', 'french', 'japanese', 'espanol']
                    if any(lang in pdf_url or lang in pdf_title for lang in other_languages):
                        non_english_detected.append(pdf)

                if len(non_english_detected) == 0:
                    print(f"\n✅ 语言过滤成功！没有发现其他语言版本的PDF")
                    print(f"🎯 验证通过: 选项1现在只下载英文版本")
                    return True
                else:
                    print(f"\n⚠️ 发现 {len(non_english_detected)} 个其他语言PDF:")
                    for pdf in non_english_detected:
                        title = pdf['title'][:50] + "..." if len(pdf['title']) > 50 else pdf['title']
                        print(f"   ⚠️ {title}")
                    return False

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

def show_option1_changes():
    """显示选项1的修改内容"""
    print(f"\n📋 选项1修改总结:")
    print("=" * 60)

    print(f"🔄 修改前:")
    print(f"   1. 癌症治疗指南 (Treatment by Cancer Type)")
    print(f"      - 会下载所有语言版本（英文、西班牙语、中文、法语等）")
    print(f"      - 菜单标题不明确用途")
    print(f"      - 没有语言过滤选择")

    print(f"\n⚡ 修改后:")
    print(f"   1. 癌症治疗指南英文版 (Treatment by Cancer Type - English Only)")
    print(f"      - 默认只下载英文版本")
    print(f"      - 自动过滤西班牙语、中文、法语、日语版本")
    print(f"      - 菜单标题明确标明用途")
    print(f"      - 无需用户选择，自动应用英文过滤")

    print(f"\n🎯 修改要点:")
    print(f"   ✅ 添加 has_language_filter=True")
    print(f"   ✅ 默认 language_filter='english'")
    print(f"   ✅ 更新标题明确标明英文版")
    print(f"   ✅ 自动应用语言过滤，无需用户交互")

if __name__ == "__main__":
    import json

    success = test_option1_english()
    show_option1_changes()

    print(f"\n{'='*60}")
    if success:
        print("🎉 选项1修改完成！")
        print("✅ 现在选项1将：")
        print("   • 只下载英文版本的癌症治疗指南")
        print("   • 自动过滤其他语言版本（西班牙语、中文、法语、日语等）")
        print("   • 无需用户手动选择语言")
        print("🚀 请测试: python download_NCCN_Guide_v2_menu.py")
    else:
        print("⚠️ 选项1测试发现问题")
        print("🔧 需要进一步调试")