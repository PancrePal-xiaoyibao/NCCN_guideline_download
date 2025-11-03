#!/usr/bin/env python3
"""
调试中文患者指南链接检测问题
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_chinese_patient_guidelines():
    """调试中文患者指南链接检测"""
    print("🔍 调试中文患者指南链接检测...")
    print("=" * 60)

    try:
        # 读取Cookie
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

        # 测试用户提到的中文翻译入口页面
        chinese_url = "https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations"
        print(f"🌐 访问中文翻译入口页面: {chinese_url}")

        response = session.get(chinese_url)
        print(f"📡 状态码: {response.status_code}")

        if response.status_code != 200:
            print("❌ 中文翻译页面访问失败")
            return

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"🔗 总链接数: {len(all_links)}")

        # 查找中文PDF链接
        chinese_pdfs = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找中文PDF链接（-zh标识）
            if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                is_chinese = '-zh' in href.lower()
                if is_chinese:
                    chinese_pdfs.append({
                        'href': href,
                        'text': text,
                        'full_url': 'https://www.nccn.org' + href if href.startswith('/') else href
                    })

        print(f"\n🇨🇳 找到中文PDF链接数量: {len(chinese_pdfs)}")
        for i, link in enumerate(chinese_pdfs[:10]):  # 显示前10个
            print(f"   {i+1}. {link['text']} -> {link['full_url']}")

        # 测试用户提到的具体链接
        user_url = "https://www.nccn.org/patients/guidelines/content/PDF/Bladder-zh-patient.pdf"
        print(f"\n🧪 测试用户提到的具体链接: {user_url}")

        test_response = session.get(user_url)
        print(f"📡 状态码: {test_response.status_code}")

        if test_response.status_code == 200:
            print("✅ 用户提到的中文PDF链接可访问")
        else:
            print("❌ 用户提到的中文PDF链接无法访问")

        # 现在检查普通患者指南页面的中文链接
        print(f"\n🔍 检查普通患者指南页面的中文链接...")
        patient_url = "https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients"

        patient_response = session.get(patient_url)
        print(f"📡 患者指南页面状态码: {patient_response.status_code}")

        if patient_response.status_code == 200:
            patient_soup = BeautifulSoup(patient_response.content, 'html.parser')
            patient_links = patient_soup.find_all('a', href=True)

            # 查找详情页链接并测试几个
            detail_links = []
            for link in patient_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if '/guidelines-for-patients-details?patientGuidelineId=' in href:
                    detail_url = 'https://www.nccn.org' + href if href.startswith('/') else href
                    detail_links.append({'url': detail_url, 'text': text})

            print(f"📋 找到 {len(detail_links)} 个详情页链接，测试前3个...")

            for i, detail in enumerate(detail_links[:3]):
                try:
                    print(f"\n📄 测试详情页 {i+1}: {detail['text']}")
                    detail_response = session.get(detail['url'])

                    if detail_response.status_code == 200:
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        detail_links_page = detail_soup.find_all('a', href=True)

                        chinese_found = 0
                        for link in detail_links_page:
                            href = link.get('href', '')
                            link_text = link.get_text(strip=True)

                            if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                                if '-zh' in href.lower():
                                    chinese_found += 1
                                    print(f"   🇨🇳 中文PDF: {link_text} -> {href}")

                        print(f"   详情页中文PDF数量: {chinese_found}")

                except Exception as e:
                    print(f"   ❌ 测试详情页失败: {e}")

    except Exception as e:
        print(f"❌ 调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chinese_patient_guidelines()