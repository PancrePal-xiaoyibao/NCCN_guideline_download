#!/usr/bin/env python3
"""
分析患者指南页面的唯一PDF数量
检查74个详情页实际包含多少个唯一的英文PDF
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def analyze_unique_pdfs():
    """分析唯一的英文PDF数量"""
    print("🔍 分析患者指南的唯一英文PDF数量...")
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

        print(f"🎯 分析主题: {theme.display_name}")

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

        # 分析前10个详情页的PDF情况
        print(f"\n🧪 分析前10个详情页的PDF情况...")
        test_links = sub_links[:10]

        total_pdfs = 0
        english_pdfs = 0
        unique_pdfs = set()
        english_unique_pdfs = set()
        pdf_details = []

        for i, sub_url in enumerate(test_links, 1):
            print(f"\n📄 [{i}/10] 分析: {sub_url.split('?')[0].split('=')[-1] if '=' in sub_url else '未知'}")

            try:
                sub_response = downloader.session.get(sub_url)
                if sub_response.status_code != 200:
                    print(f"   ❌ 访问失败")
                    continue

                sub_soup = BeautifulSoup(sub_response.content, 'html.parser')

                # 查找所有PDF链接
                page_pdfs = []
                for link in sub_soup.find_all('a', href=True):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)

                    if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                        # 正确拼接URL
                        if href.startswith('http'):
                            pdf_url = href
                        else:
                            pdf_url = 'https://www.nccn.org' + href

                        # 检测语言
                        detected_lang = downloader._detect_pdf_language(href, link_text)

                        pdf_info = {
                            'url': pdf_url,
                            'href': href,
                            'title': link_text,
                            'language': detected_lang,
                            'page_url': sub_url
                        }

                        page_pdfs.append(pdf_info)
                        total_pdfs += 1

                        # 添加到唯一集合
                        unique_pdfs.add(pdf_url)

                        if detected_lang in ['English', 'Unknown']:
                            english_pdfs += 1
                            english_unique_pdfs.add(pdf_url)

                print(f"   📋 页面PDF: {len(page_pdfs)} 个")
                print(f"   🇺🇸 英文PDF: {len([p for p in page_pdfs if p['language'] in ['English', 'Unknown']])} 个")

                # 显示页面PDF详情
                for pdf in page_pdfs:
                    lang_flag = "🇺🇸" if pdf['language'] in ['English', 'Unknown'] else "🌍"
                    print(f"      {lang_flag} {pdf['title'][:30]}... → {pdf['href']}")

                pdf_details.extend(page_pdfs)

                # 添加延迟避免过于频繁的请求
                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                print(f"   ❌ 处理失败: {str(e)}")
                continue

        # 统计结果
        print(f"\n📊 详细统计分析:")
        print(f"   测试详情页数: {len(test_links)}")
        print(f"   总PDF引用数: {total_pdfs}")
        print(f"   英文PDF引用数: {english_pdfs}")
        print(f"   唯一PDF总数: {len(unique_pdfs)}")
        print(f"   唯一英文PDF数: {len(english_unique_pdfs)}")

        # 语言分布统计
        lang_counts = {}
        for pdf in pdf_details:
            lang = pdf['language']
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        print(f"\n🌍 语言分布:")
        for lang, count in sorted(lang_counts.items()):
            print(f"   {lang}: {count} 个")

        # 显示唯一的英文PDF
        print(f"\n📋 唯一英文PDF列表:")
        unique_english_list = list(english_unique_pdfs)
        for i, pdf_url in enumerate(sorted(unique_english_list), 1):
            # 提取文件名
            filename = pdf_url.split('/')[-1]
            print(f"   {i:2d}. {filename}")

        # 计算预期
        print(f"\n🔮 预期分析:")
        if len(test_links) > 0:
            pages_per_pdf = len(test_links) / len(english_unique_pdfs) if english_unique_pdfs else 0
            estimated_total_unique = int(len(sub_links) / pages_per_pdf) if pages_per_pdf > 0 else 0

            print(f"   当前样本 (10页) → {len(english_unique_pdfs)} 个唯一英文PDF")
            print(f"   平均每页PDF数: {pages_per_pdf:.1f}")
            print(f"   预估总数 (74页): ~{estimated_total_unique} 个唯一英文PDF")

            if estimated_total_unique < 20:
                print(f"\n⚠️  警告: 预估的唯一英文PDF数量偏少")
                print(f"   可能原因:")
                print(f"   1. 多个页面共享相同PDF")
                print(f"   2. 患者指南实际上种类较少")
                print(f"   3. 解析逻辑需要调整")
            else:
                print(f"\n✅ 预估数量合理")
        else:
            print(f"   ⚠️ 无法计算预估（没有成功解析的页面）")

        return len(english_unique_pdfs)

    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    import json

    unique_count = analyze_unique_pdfs()
    print(f"\n{'='*60}")
    print(f"🎯 最终结论:")
    print(f"   测试的10个详情页包含 {unique_count} 个唯一英文PDF")
    print(f"   如果这个比例保持，74个详情页预计有 ~{unique_count * 7} 个唯一英文PDF")
