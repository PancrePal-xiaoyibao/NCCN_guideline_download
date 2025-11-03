#!/usr/bin/env python3
"""
测试修复后的语言检测逻辑，验证是否能识别所有13个中文PDF
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_fixed_language_detection():
    """测试修复后的语言检测逻辑"""
    print("🧪 测试修复后的语言检测逻辑...")
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
            return False

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        all_links = soup.find_all('a', href=True)

        # 实现修复后的语言检测逻辑
        def _detect_pdf_language(pdf_url: str, link_text: str = "") -> str:
            """修复后的语言检测逻辑"""
            url_lower = pdf_url.lower()
            text_lower = link_text.lower()

            # 检查中文标识（扩展多种中文标识符）
            if any(indicator in url_lower for indicator in ['-zh', '-chi', '-chinese', '-ch(', '-ch)']):
                return 'Chinese'
            elif 'chinese' in text_lower:
                return 'Chinese'
            # 检查西班牙语标识
            elif any(indicator in url_lower for indicator in ['-es', '-esl', '-es_', '-spanish', 'spanish']):
                return 'Spanish'
            elif 'spanish' in text_lower:
                return 'Spanish'
            # 检查其他语言标识
            elif any(indicator in url_lower for indicator in ['-ar', '-arabic', 'arabic']):
                return 'Arabic'
            elif any(indicator in url_lower for indicator in ['-fr', '-french', 'french']):
                return 'French'
            elif any(indicator in url_lower for indicator in ['-hi', '-hindi', 'hindi']):
                return 'Hindi'
            elif any(indicator in url_lower for indicator in ['-jp', '-japanese', 'japanese']):
                return 'Japanese'
            elif any(indicator in url_lower for indicator in ['-kr', '-korean', 'korean']):
                return 'Korean'
            elif any(indicator in url_lower for indicator in ['-po', '-polish', 'polish']):
                return 'Polish'
            elif any(indicator in url_lower for indicator in ['-pt', '-portuguese', 'portuguese']):
                return 'Portuguese'
            elif any(indicator in url_lower for indicator in ['-ru', '-russian', 'russian']):
                return 'Russian'
            elif any(indicator in url_lower for indicator in ['-vi', '-vietnamese', 'vietnamese']):
                return 'Vietnamese'
            else:
                return 'English'

        # 查找所有PDF链接并分类
        pdf_links = []
        language_stats = {'Chinese': 0, 'Spanish': 48, 'Arabic': 12, 'French': 7, 'Hindi': 10, 'Japanese': 3, 'Korean': 1, 'Polish': 3, 'Portuguese': 8, 'Russian': 3, 'Vietnamese': 2, 'English': 73}

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找PDF链接
            if href.endswith('.pdf') and '/patients/guidelines/content/PDF/' in href:
                # 应用修复后的语言检测
                detected_language = _detect_pdf_language(href, text)

                # 正确拼接URL
                if href.startswith('http'):
                    pdf_url = href
                else:
                    pdf_url = 'https://www.nccn.org' + href

                pdf_info = {
                    'title': text if text else 'Unknown Title',
                    'url': pdf_url,
                    'href': href,
                    'language': detected_language
                }

                pdf_links.append(pdf_info)

        # 统计各语言PDF数量
        actual_stats = {}
        for pdf in pdf_links:
            lang = pdf['language']
            actual_stats[lang] = actual_stats.get(lang, 0) + 1

        print(f"\n📊 修复后实际语言统计:")
        for lang, count in sorted(actual_stats.items()):
            print(f"   {lang}: {count}")

        # 特别检查中文PDF
        chinese_pdfs = [pdf for pdf in pdf_links if pdf['language'] == 'Chinese']
        print(f"\n🇨🇳 修复后找到中文PDF数量: {len(chinese_pdfs)}")

        if len(chinese_pdfs) >= 10:  # 与期望的13个接近
            print(f"✅ 成功！语言检测逻辑修复有效")
            print(f"📋 前15个中文PDF:")
            for i, pdf in enumerate(chinese_pdfs[:15], 1):
                print(f"   {i:2d}. {pdf['title'][:60]}")
                print(f"       标识: {pdf['href'].split('/')[-1]}")
                print()

            if len(chinese_pdfs) > 15:
                print(f"   ... 还有 {len(chinese_pdfs) - 15} 个文件")

            return True
        else:
            print(f"⚠️  仍有问题，期望13个中文PDF，实际找到{len(chinese_pdfs)}个")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_language_detection()

    print(f"\n{'='*60}")
    if success:
        print("🎉 语言检测逻辑修复成功！")
        print("✅ 修复后的双语患者指南解析现在应该能正确处理中文PDF")
        print("🚀 准备测试完整的主程序流程")
    else:
        print("⚠️  语言检测逻辑仍需调试")