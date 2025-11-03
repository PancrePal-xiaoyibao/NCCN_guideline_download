#!/usr/bin/env python3
"""
仔细分析翻译页面，寻找所有13个中文PDF的完整链接
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def debug_detailed_translation_page():
    """详细调试翻译页面，寻找所有中文PDF链接"""
    print("🔍 详细分析翻译页面，寻找所有中文PDF链接...")
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

        # 使用用户提供的cURL中的URL
        translation_url = "https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations"
        print(f"🌐 访问翻译页面: {translation_url}")

        response = session.get(translation_url)
        print(f"📡 状态码: {response.status_code}")
        print(f"📄 响应头Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"📄 响应长度: {len(response.content)} 字节")

        if response.status_code != 200:
            print("❌ 翻译页面访问失败")
            return

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 查找所有h4标题，特别关注Chinese Translations
        print(f"\n🔍 查找Chinese Translations部分...")
        headers = soup.find_all('h4')

        chinese_section = None
        for header in headers:
            if 'Chinese' in header.get_text():
                chinese_section = header
                print(f"✅ 找到Chinese Translations部分")
                print(f"   标题: {header.get_text(strip=True)}")
                break

        if not chinese_section:
            print("❌ 未找到Chinese Translations部分")
            # 显示所有h4标题
            print("所有h4标题:")
            for h4 in headers:
                print(f"   {h4.get_text(strip=True)}")
            return

        # 从Chinese Translations部分开始查找PDF链接
        print(f"\n🔍 从Chinese Translations部分开始查找PDF链接...")

        # 找到Chinese Translations部分的下一个兄弟元素
        current = chinese_section
        chinese_pdfs = []
        processed_sections = 0

        # 遍历Chinese Translations后面的所有元素，直到下一个h4
        while current and processed_sections < 50:  # 防止无限循环
            current = current.find_next_sibling()

            if current is None:
                break

            if current.name == 'h4':  # 遇到下一个语言部分，停止
                break

            # 查找当前元素中的所有链接
            links = current.find_all('a', href=True)

            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)

                # 查找PDF链接
                if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                    # 正确拼接URL
                    if href.startswith('http'):
                        pdf_url = href
                    else:
                        pdf_url = 'https://www.nccn.org' + href

                    chinese_pdfs.append({
                        'title': text,
                        'href': href,
                        'url': pdf_url,
                        'section': current.name if current else 'unknown'
                    })

            processed_sections += 1

        print(f"✅ 从Chinese Translations部分找到 {len(chinese_pdfs)} 个PDF链接")

        # 显示所有找到的中文PDF
        print(f"\n🇨🇳 从Chinese Translations部分找到的中文PDF:")
        for i, pdf in enumerate(chinese_pdfs, 1):
            print(f"   {i:2d}. {pdf['title']}")
            print(f"       文件: {pdf['href']}")
            print(f"       完整URL: {pdf['url']}")
            print()

        # 现在查找页面上所有可能的PDF链接，筛选中文
        print(f"\n🔍 全页面搜索所有PDF链接并筛选中文...")
        all_links = soup.find_all('a', href=True)
        all_pdfs = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找PDF链接
            if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                all_pdfs.append({
                    'title': text,
                    'href': href,
                    'url': 'https://www.nccn.org' + href if href.startswith('/') else href
                })

        # 识别中文PDF的各种模式
        chinese_patterns = [
            '-zh', '-chi', '-chinese', '-ch(', '-ch)',
            'chinese', 'CH', 'zh'
        ]

        all_chinese_pdfs = []
        for pdf in all_pdfs:
            href_lower = pdf['href'].lower()
            text_lower = pdf['title'].lower()

            is_chinese = False
            matched_pattern = None

            for pattern in chinese_patterns:
                if pattern in href_lower or pattern in text_lower:
                    is_chinese = True
                    matched_pattern = pattern
                    break

            if is_chinese:
                all_chinese_pdfs.append({
                    **pdf,
                    'matched_pattern': matched_pattern
                })

        print(f"✅ 全页面搜索找到 {len(all_chinese_pdfs)} 个中文PDF")

        print(f"\n🇨🇳 全页面搜索到的所有中文PDF:")
        for i, pdf in enumerate(all_chinese_pdfs, 1):
            print(f"   {i:2d}. {pdf['title']}")
            print(f"       匹配模式: {pdf['matched_pattern']}")
            print(f"       文件: {pdf['href']}")
            print()

        # 验证PDF链接的可访问性
        print(f"\n🧪 测试中文PDF链接的可访问性...")
        accessible_count = 0

        for i, pdf in enumerate(all_chinese_pdfs[:5], 1):  # 测试前5个
            try:
                print(f"📄 [{i}/5] 测试: {pdf['title'][:50]}...")

                # 使用HEAD请求检查文件存在
                head_response = session.head(pdf['url'], timeout=10)
                print(f"   📡 HEAD状态码: {head_response.status_code}")

                if head_response.status_code == 200:
                    accessible_count += 1
                    print(f"   ✅ 可访问")
                else:
                    print(f"   ❌ 不可访问")

            except Exception as e:
                print(f"   ⚠️  测试失败: {str(e)}")

        print(f"\n📊 最终结果:")
        print(f"   Chinese Translations部分PDF数: {len(chinese_pdfs)}")
        print(f"   全页面中文PDF数: {len(all_chinese_pdfs)}")
        print(f"   可访问PDF数 (测试样本): {accessible_count}/5")

        # 检查是否达到了期望的13个
        if len(all_chinese_pdfs) >= 10:
            print(f"\n✅ 成功！找到 {len(all_chinese_pdfs)} 个中文PDF")
            return True
        else:
            print(f"\n⚠️  只找到 {len(all_chinese_pdfs)} 个中文PDF，期望13个")
            print(f"   需要进一步调试...")
            return False

    except Exception as e:
        print(f"❌ 详细调试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_detailed_translation_page()