#!/usr/bin/env python3
"""
详细调试选项3的PDF解析过程
检查为什么只找到10个PDF而不是预期的60+
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_option3_detailed():
    """详细调试选项3的PDF解析过程"""
    print("🔍 详细调试选项3PDF解析过程...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建主题配置
        theme = ThemeConfig(
            name='patient_guidelines',
            display_name='患者指南英文版 (Patient Guidelines - English Only)',
            url='https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients',
            category='patient_guidelines_english',
            directory='03_Patient_Guidelines_English',
            description='患者专用英文指南'
        )

        print(f"🎯 调试主题: {theme.display_name}")

        # 访问主页面
        print(f"\n🌐 访问主页面...")
        response = downloader.session.get(theme.url)
        if response.status_code != 200:
            print(f"❌ 页面访问失败")
            return

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # 获取详情页链接
        print(f"\n🔍 获取详情页链接...")
        sub_links = downloader._get_sub_links_patient_guidelines(soup, theme.url)
        print(f"📊 总共找到 {len(sub_links)} 个详情页链接")

        # 测试前3个详情页的详细解析过程
        test_links = sub_links[:3]
        print(f"\n🧪 详细分析前3个详情页的PDF解析过程...")

        total_pdfs = 0
        english_pdfs = 0
        detailed_results = []

        for i, sub_url in enumerate(test_links, 1):
            print(f"\n📄 [{i}/3] 详细分析详情页:")
            print(f"   URL: {sub_url}")

            try:
                sub_response = downloader.session.get(sub_url)
                if sub_response.status_code != 200:
                    print(f"   ❌ 访问失败")
                    continue

                sub_soup = BeautifulSoup(sub_response.content, 'html.parser')

                # 查找所有PDF链接并详细分析
                all_pdf_links = []
                for link in sub_soup.find_all('a', href=True):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)

                    if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                        all_pdf_links.append({
                            'href': href,
                            'text': link_text,
                            'full_url': 'https://www.nccn.org' + href if not href.startswith('http') else href
                        })

                print(f"   📋 找到 {len(all_pdf_links)} 个PDF链接:")
                page_english_count = 0

                for j, pdf_info in enumerate(all_pdf_links, 1):
                    # 详细检测语言
                    detected_lang = downloader._detect_pdf_language(pdf_info['href'], pdf_info['text'])
                    title = pdf_info['text'] if pdf_info['text'] else '无标题'
                    print(f"      {j}. {title}")
                    print(f"         URL: {pdf_info['href']}")
                    print(f"         检测语言: {detected_lang}")

                    if detected_lang in ['English', 'Unknown']:
                        page_english_count += 1
                        detailed_results.append({
                            'page': i,
                            'title': title,
                            'url': pdf_info['href'],
                            'full_url': pdf_info['full_url'],
                            'language': detected_lang
                        })

                print(f"   ✅ 页面英文PDF数: {page_english_count}")
                total_pdfs += len(all_pdf_links)
                english_pdfs += page_english_count

            except Exception as e:
                print(f"   ❌ 处理失败: {str(e)}")
                continue

        print(f"\n📊 初步统计结果:")
        print(f"   测试详情页数: {len(test_links)}")
        print(f"   总PDF链接数: {total_pdfs}")
        print(f"   英文PDF数: {english_pdfs}")
        print(f"   比例: {english_pdfs}/{total_pdfs} = {english_pdfs/total_pdfs*100:.1f}%")

        # 分析问题
        print(f"\n🔍 问题分析:")

        if total_pdfs == 0:
            print(f"   ❌ 没有找到任何PDF链接")
            print(f"   🔧 可能原因:")
            print(f"      - 页面结构已变化")
            print(f"      - 链接选择器不正确")
            print(f"      - 需要登录才能访问")
        else:
            non_english_count = total_pdfs - english_pdfs
            if non_english_count > 0:
                print(f"   ⚠️ 找到 {non_english_count} 个非英文PDF被过滤")
                print(f"   🔧 可能原因:")
                print(f"      - 语言检测逻辑过于严格")
                print(f"      - 包含西班牙语、中文等版本")
                print(f"      - URL格式不符合预期")

            if english_pdfs == 0:
                print(f"   ❌ 所有PDF都被过滤掉了")
                print(f"   🔧 可能原因:")
                print(f"      - 语言检测逻辑有误")
                print(f"      - 所有文件都是非英文")
                print(f"      - 检测条件过于严格")

        # 检查语言检测逻辑
        print(f"\n🧪 测试语言检测逻辑...")
        test_urls = [
            'https://www.nccn.org/patients/guidelines/content/PDF/all-patient.pdf',
            'https://www.nccn.org/patients/guidelines/content/PDF/ALL-es-patient.pdf',
            'https://www.nccn.org/patients/guidelines/content/PDF/Bladder-zh-patient.pdf',
        ]

        for test_url in test_urls:
            detected = downloader._detect_pdf_language(test_url, '')
            print(f"   {test_url} → {detected}")

        # 给出修复建议
        print(f"\n💡 修复建议:")

        if english_pdfs < total_pdfs * 0.5:  # 如果英文PDF少于50%
            print(f"   1. 放宽语言检测条件")
            print(f"   2. 检查默认处理逻辑")
            print(f"   3. 考虑将Unknown视为英文")

        if total_pdfs < len(test_links) * 2:  # 如果平均每个页面PDF少于2个
            print(f"   1. 检查PDF链接选择器")
            print(f"   2. 验证页面结构")
            print(f"   3. 检查是否有动态加载内容")

        print(f"\n📋 详细解析的英文PDF:")
        for result in detailed_results:
            print(f"   {result['title']} → {result['language']}")

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import json

    debug_option3_detailed()