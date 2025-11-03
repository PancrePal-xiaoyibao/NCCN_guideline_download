#!/usr/bin/env python3
"""
检查主页面是否包含指向翻译页面的链接
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def check_translation_links():
    """检查主页面是否包含指向翻译页面的链接"""
    print("🔍 检查主页面是否包含指向翻译页面的链接...")
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

        # 访问主页面
        main_url = "https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients"
        print(f"🌐 访问主页面: {main_url}")

        response = session.get(main_url)
        print(f"📡 状态码: {response.status_code}")

        if response.status_code != 200:
            print("❌ 主页面访问失败")
            return

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        print(f"🔗 总链接数: {len(all_links)}")

        # 查找指向翻译页面的链接
        translation_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找包含"translations"或"中文"的链接
            if 'translations' in href.lower() or '中文' in text or 'chinese' in text.lower():
                full_url = 'https://www.nccn.org' + href if href.startswith('/') else href
                translation_links.append({
                    'href': href,
                    'text': text,
                    'full_url': full_url
                })

        print(f"\n🔗 找到可能的翻译相关链接数量: {len(translation_links)}")
        for i, link in enumerate(translation_links[:10]):  # 显示前10个
            print(f"   {i+1}. {link['text']} -> {link['full_url']}")

        # 特别检查是否包含我们已知的中文翻译页面
        known_chinese_url = "https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations"
        found_chinese = False
        for link in translation_links:
            if 'guidelines-for-patients-translations' in link['href']:
                print(f"\n✅ 找到指向中文翻译页面的链接!")
                print(f"   文本: {link['text']}")
                print(f"   链接: {link['full_url']}")
                found_chinese = True
                break

        if not found_chinese:
            print(f"\n❌ 主页面未找到指向中文翻译页面的直接链接")
            print(f"   这解释了为什么选项6无法找到中文PDF")

            # 检查是否有其他形式的翻译链接
            print(f"\n🔍 查找其他可能的翻译相关内容...")
            translation_keywords = ['translation', 'chinese', 'zh', 'spanish', 'es']
            for link in all_links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()

                for keyword in translation_keywords:
                    if keyword in href or keyword in text:
                        full_url = 'https://www.nccn.org' + link.get('href', '') if link.get('href', '').startswith('/') else link.get('href', '')
                        print(f"   包含'{keyword}'的链接: {text} -> {full_url}")
                        break

    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_translation_links()