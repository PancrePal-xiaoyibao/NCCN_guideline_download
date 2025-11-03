#!/usr/bin/env python3
"""
调试双语患者指南解析问题
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_patient_guidelines_page():
    """调试患者指南页面结构"""
    print("🔍 调试双语患者指南页面结构...")
    print("=" * 60)

    try:
        # 使用Cookie访问患者指南页面
        with open('extracted_cookies.txt', 'r', encoding='utf-8') as f:
            cookie_string = f.read().strip()

        # 解析Cookie
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value

        # 创建session
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        session.cookies.update(cookies)

        # 访问患者指南主页
        url = "https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients"
        print(f"🌐 访问: {url}")

        response = session.get(url)
        print(f"📡 状态码: {response.status_code}")
        print(f"📄 页面大小: {len(response.text):,} 字符")

        if response.status_code != 200:
            print("❌ 访问失败")
            return

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"🔗 总链接数: {len(all_links)}")

        # 查找详情页链接 (根据用户提供的结构)
        detail_links = []
        patient_links = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找详情页链接
            if '/guidelines-for-patients-details?patientGuidelineId=' in href:
                detail_links.append({
                    'href': href,
                    'text': text,
                    'full_url': 'https://www.nccn.org' + href if href.startswith('/') else href
                })

            # 查找PDF链接
            if '/patients/guidelines/content/PDF/' in href:
                patient_links.append({
                    'href': href,
                    'text': text,
                    'is_chinese': '-zh' in href.lower(),
                    'full_url': 'https://www.nccn.org' + href if href.startswith('/') else href
                })

        print(f"\n📋 详情页链接数量: {len(detail_links)}")
        for i, link in enumerate(detail_links[:5]):  # 只显示前5个
            print(f"   {i+1}. {link['text']} -> {link['full_url']}")

        print(f"\n📋 直接PDF链接数量: {len(patient_links)}")
        chinese_count = 0
        english_count = 0
        for link in patient_links[:10]:  # 只显示前10个
            version = "Chinese" if link['is_chinese'] else "English"
            if link['is_chinese']:
                chinese_count += 1
            else:
                english_count += 1
            print(f"   📄 {link['text']} ({version}) -> {link['full_url'][:60]}...")

        print(f"\n📊 语言分布:")
        print(f"   中文版本: {chinese_count}")
        print(f"   英文版本: {english_count}")

        # 如果找到了详情页链接，测试访问第一个
        if detail_links:
            print(f"\n🧪 测试访问第一个详情页...")
            test_detail_url = detail_links[0]['full_url']
            print(f"🌐 访问详情页: {test_detail_url}")

            detail_response = session.get(test_detail_url)
            print(f"📡 状态码: {detail_response.status_code}")

            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                detail_links_page = detail_soup.find_all('a', href=True)

                pdf_on_detail_page = []
                for link in detail_links_page:
                    href = link.get('href', '')
                    if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                        pdf_on_detail_page.append({
                            'href': href,
                            'text': link.get_text(strip=True),
                            'is_chinese': '-zh' in href.lower()
                        })

                print(f"📋 详情页PDF链接数量: {len(pdf_on_detail_page)}")
                for link in pdf_on_detail_page:
                    version = "Chinese" if link['is_chinese'] else "English"
                    full_url = 'https://www.nccn.org' + link['href'] if link['href'].startswith('/') else link['href']
                    print(f"   📄 {link['text']} ({version}) -> {full_url}")

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_patient_guidelines_page()