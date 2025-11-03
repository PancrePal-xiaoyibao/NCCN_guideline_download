#!/usr/bin/env python3
"""
详细调试选项1的语言过滤过程
查看PDF解析和过滤的具体步骤
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_detailed_filtering():
    """详细调试语言过滤过程"""
    print("🔍 详细调试选项1的语言过滤过程...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项1的配置
        theme = ThemeConfig(
            name='cancer_treatment',
            display_name='癌症治疗指南英文版 (Treatment by Cancer Type - English Only)',
            url='https://www.nccn.org/guidelines/category_1',
            category='category_1',
            directory='01_Cancer_Treatment',
            description='按癌症类型分类的治疗指南（英文版）',
            has_language_filter=True
        )

        # 模拟用户选择：仅英文版本
        language_filter = 'english'
        print(f"🎯 语言过滤设置: {language_filter}")

        # 访问主页面
        print(f"\n🌐 访问主页面...")
        response = downloader.session.get(theme.url)

        if response.status_code == 200:
            print(f"✅ 页面访问成功")

            # 解析页面
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # 获取子链接
            sub_links = downloader._get_sub_links(soup, theme.url)
            print(f"📊 找到 {len(sub_links)} 个指南子页面")

            # 只测试第一个详情页
            test_url = sub_links[0]
            print(f"\n🧪 详细测试第一个详情页: {test_url}")

            # 手动模拟PDF解析过程
            print(f"\n🔍 手动模拟PDF解析和过滤过程...")

            test_response = downloader.session.get(test_url)
            if test_response.status_code == 200:
                test_soup = BeautifulSoup(test_response.content, 'html.parser')

                # 查找所有PDF链接
                all_links = test_soup.find_all('a', href=True)
                pdf_candidates = []

                for link in all_links:
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)

                    if href.endswith('.pdf'):
                        pdf_candidates.append({
                            'href': href,
                            'text': link_text,
                            'url': href if href.startswith('http') else 'https://www.nccn.org' + href
                        })

                print(f"📋 找到 {len(pdf_candidates)} 个PDF候选链接")

                # 手动应用语言过滤
                english_pdfs = []
                filtered_pdfs = []

                for pdf in pdf_candidates:
                    # 检测语言
                    detected_lang = downloader._detect_pdf_language(pdf['href'], pdf['text'])
                    should_include = downloader._should_include_pdf(pdf['href'], language_filter, pdf['text'])

                    status = "✅ 保留" if should_include else "❌ 过滤"
                    print(f"   {detected_lang:10s} | {status} | {pdf['text'][:30]}...")
                    print(f"   {'':12s} | {' '*8} | {pdf['href']}")

                    if should_include:
                        english_pdfs.append(pdf)
                    else:
                        filtered_pdfs.append(pdf)

                print(f"\n📊 过滤结果:")
                print(f"   总PDF数: {len(pdf_candidates)}")
                print(f"   保留PDF数: {len(english_pdfs)}")
                print(f"   过滤PDF数: {len(filtered_pdfs)}")

                # 验证过滤结果
                if len(filtered_pdfs) > 0:
                    print(f"\n⚠️ 被过滤的PDF:")
                    for pdf in filtered_pdfs:
                        detected_lang = downloader._detect_pdf_language(pdf['href'], pdf['text'])
                        print(f"   ❌ {detected_lang:10s} | {pdf['text'][:40]}...")

                # 调用实际方法进行对比
                print(f"\n🔄 对比：调用实际解析方法...")
                actual_pdfs = downloader._get_pdfs_from_detail_page(test_url, "Test Guideline", language_filter)

                print(f"📊 方法调用结果:")
                print(f"   手动过滤结果: {len(english_pdfs)}")
                print(f"   方法调用结果: {len(actual_pdfs)}")

                if len(english_pdfs) == len(actual_pdfs):
                    print(f"✅ 结果一致，语言过滤正常工作")
                    return True
                else:
                    print(f"⚠️ 结果不一致，存在问题")
                    return False

            else:
                print(f"❌ 无法访问测试详情页")
                return False
        else:
            print(f"❌ 主页面访问失败")
            return False

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import json

    success = debug_detailed_filtering()

    print(f"\n{'='*60}")
    if success:
        print("✅ 语言过滤功能正常")
    else:
        print("❌ 语言过滤存在问题")