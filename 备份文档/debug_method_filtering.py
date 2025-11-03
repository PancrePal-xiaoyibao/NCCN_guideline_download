#!/usr/bin/env python3
"""
调试具体的方法过滤问题
查看方法1和方法2的过滤效果
"""

import sys
import os
import time
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_method_filtering():
    """调试各个方法的过滤效果"""
    print("🔍 调试各个方法的过滤效果...")
    print("=" * 60)

    try:
        # 读取配置文件
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 测试URL
        test_url = "https://www.nccn.org/guidelines/guidelines-detail?category=1&id=1410"
        language_filter = 'english'

        print(f"🎯 测试URL: {test_url}")
        print(f"🌐 语言过滤: {language_filter}")

        # 访问页面
        response = downloader.session.get(test_url)
        if response.status_code != 200:
            print(f"❌ 无法访问页面")
            return

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"\n🔍 手动模拟方法1：查找直接PDF链接")
        method1_pdfs = []
        all_links = soup.find_all('a', href=True)

        for link in all_links:
            href = link.get('href', '')
            if href.endswith('.pdf'):
                link_text = link.text.strip()

                print(f"   检查: {link_text[:30]}...")
                print(f"   URL: {href}")

                # 应用语言过滤
                should_include = downloader._should_include_pdf(href, language_filter, link_text)
                detected_lang = downloader._detect_pdf_language(href, link_text)

                print(f"   检测语言: {detected_lang}")
                print(f"   应该包含: {'✅' if should_include else '❌'}")

                if should_include:
                    # 正确拼接URL
                    if href.startswith('http'):
                        pdf_url = href
                    else:
                        pdf_url = 'https://www.nccn.org' + href

                    method1_pdfs.append({
                        'title': link_text,
                        'url': pdf_url,
                        'version': detected_lang
                    })
                    print(f"   ✅ 添加到方法1结果")

                print()

        print(f"\n📊 方法1结果: {len(method1_pdfs)} 个PDF")

        print(f"\n🔍 手动模拟方法2：查找pdfList链接")
        method2_pdfs = []
        pdf_lists = soup.find_all('ul', class_='pdfList')

        for pdf_list in pdf_lists:
            print(f"📋 找到pdfList区域: {len(pdf_list.find_all('a', href=True))} 个链接")

            for link in pdf_list.find_all('a', href=True):
                href = link.get('href', '')
                if href.endswith('.pdf'):
                    link_text = link.text.strip()

                    print(f"   检查: {link_text[:30]}...")
                    print(f"   URL: {href}")

                    # 应用语言过滤
                    should_include = downloader._should_include_pdf(href, language_filter, link_text)
                    detected_lang = downloader._detect_pdf_language(href, link_text)

                    print(f"   检测语言: {detected_lang}")
                    print(f"   应该包含: {'✅' if should_include else '❌'}")

                    if should_include:
                        # 正确拼接URL
                        if href.startswith('http'):
                            pdf_url = href
                        else:
                            pdf_url = 'https://www.nccn.org' + href

                        method2_pdfs.append({
                            'title': link_text,
                            'url': pdf_url,
                            'version': detected_lang
                        })
                        print(f"   ✅ 添加到方法2结果")

                    print()

        print(f"\n📊 方法2结果: {len(method2_pdfs)} 个PDF")

        # 合并和去重
        all_pdfs = method1_pdfs.copy()
        for pdf in method2_pdfs:
            if not any(p['url'] == pdf['url'] for p in all_pdfs):
                all_pdfs.append(pdf)

        print(f"\n🎯 合并去重后总计: {len(all_pdfs)} 个PDF")

        print(f"\n📋 最终包含的PDF:")
        for i, pdf in enumerate(all_pdfs, 1):
            print(f"   {i:2d}. {pdf['version']:10s} | {pdf['title'][:40]}...")

        return len(all_pdfs)

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    import json

    result_count = debug_method_filtering()
    print(f"\n{'='*60}")
    print(f"🎯 手动方法结果: {result_count} 个PDF")
    print(f"现在可以对比实际方法调用结果，看看差异在哪里")