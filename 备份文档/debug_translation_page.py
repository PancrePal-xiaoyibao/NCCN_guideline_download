#!/usr/bin/env python3
"""
深入分析翻译页面结构，寻找更多中文PDF
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def analyze_translation_page_structure():
    """深入分析翻译页面结构"""
    print("🔍 深入分析翻译页面结构...")
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

        # 访问翻译页面
        translation_url = "https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations"
        print(f"🌐 访问翻译页面: {translation_url}")

        response = session.get(translation_url)
        print(f"📡 状态码: {response.status_code}")

        if response.status_code != 200:
            print("❌ 翻译页面访问失败")
            return

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"\n📄 页面标题: {soup.title.string if soup.title else 'N/A'}")

        # 分析页面结构
        print(f"\n🔍 分析页面结构...")

        # 查找所有h1-h6标题
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"\n📋 找到 {len(headers)} 个标题")
        for header in headers[:20]:  # 显示前20个标题
            print(f"   {header.name}: {header.get_text(strip=True)[:80]}")

        # 查找所有包含"Chinese"的文本
        chinese_text = soup.get_text()
        if 'Chinese' in chinese_text:
            chinese_sections = []
            lines = chinese_text.split('\n')
            for i, line in enumerate(lines):
                if 'Chinese' in line and line.strip():
                    chinese_sections.append((i, line.strip()))
            print(f"\n🇨🇳 找到 {len(chinese_sections)} 行包含'Chinese'的文本:")
            for line_num, line_text in chinese_sections[:10]:
                print(f"   行{line_num}: {line_text[:100]}...")

        # 查找所有PDF链接
        all_links = soup.find_all('a', href=True)
        pdf_links = []
        zh_links = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            if href.endswith('.pdf') and '/patients/guidelines/content/PDF/' in href:
                pdf_links.append({
                    'href': href,
                    'text': text,
                    'url': 'https://www.nccn.org' + href if href.startswith('/') else href
                })

                # 检查是否包含中文标识
                if any(keyword in href.lower() or keyword in text.lower() for keyword in ['zh', 'chinese', '中文']):
                    zh_links.append({
                        'href': href,
                        'text': text,
                        'url': 'https://www.nccn.org' + href if href.startswith('/') else href
                    })

        print(f"\n📄 总PDF链接数: {len(pdf_links)}")
        print(f"🇨🇳 疑似中文PDF链接数: {len(zh_links)}")

        # 显示所有PDF链接
        print(f"\n📋 所有PDF链接:")
        for i, pdf in enumerate(pdf_links, 1):
            print(f"   {i:2d}. {pdf['text'][:60]:<60} -> {pdf['href']}")

        # 查找可能的中文相关内容
        print(f"\n🔍 查找可能的中文相关内容...")

        # 查找包含-zh的链接
        zh_href_count = sum(1 for link in all_links if '-zh' in link.get('href', '').lower())
        print(f"   包含'-zh'的链接数: {zh_href_count}")

        # 查找包含chinese的链接
        chinese_text_count = sum(1 for link in all_links if 'chinese' in link.get_text(strip=True).lower())
        print(f"   包含'chinese'文本的链接数: {chinese_text_count}")

        # 查找中文文本
        chinese_character_links = []
        for link in all_links:
            text = link.get_text(strip=True)
            # 检查是否包含中文字符
            if any(ord(char) > 127 for char in text) and len(text) > 2:
                chinese_character_links.append({
                    'href': link.get('href', ''),
                    'text': text
                })

        print(f"   包含中文字符的链接数: {len(chinese_character_links)}")
        if chinese_character_links:
            print(f"   前5个包含中文字符的链接:")
            for link in chinese_character_links[:5]:
                print(f"      {link['text']} -> {link['href']}")

        # 详细分析每个PDF链接的语言
        print(f"\n🔍 详细分析PDF链接语言:")
        language_stats = {'Chinese': 0, 'Spanish': 0, 'English': 0, 'Unknown': 0}

        for pdf in pdf_links:
            href_lower = pdf['href'].lower()
            text_lower = pdf['text'].lower()

            language = 'Unknown'
            if '-zh' in href_lower or 'chinese' in text_lower:
                language = 'Chinese'
            elif '-es' in href_lower or 'spanish' in text_lower:
                language = 'Spanish'
            elif '-en' in href_lower or 'english' in text_lower:
                language = 'English'
            else:
                language = 'English'  # 默认认为是英文

            language_stats[language] += 1

        print(f"📊 语言统计:")
        for lang, count in language_stats.items():
            print(f"   {lang}: {count}")

        return True

    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    analyze_translation_page_structure()