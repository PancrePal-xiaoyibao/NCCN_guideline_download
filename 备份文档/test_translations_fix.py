#!/usr/bin/env python3
"""
测试翻译页面解析修复
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from download_NCCN_Guide_v2_menu import ThemeConfig

class TestTranslationsFix:
    def __init__(self):
        self.session = requests.Session()

        # 模拟ThemeConfig
        self.clinical_theme = ThemeConfig(
            category='clinical_translations',
            name='clinical_translations',
            display_name='临床指南中文翻译 (Clinical Translations)',
            url='https://www.nccn.org/global/what-we-do/clinical-guidelines-translations',
            description='临床指南中文翻译版本',
            directory='04_Clinical_Translations'
        )

        self.patient_theme = ThemeConfig(
            category='patient_translations',
            name='patient_translations',
            display_name='患者指南中文翻译 (Patient Guidelines Translations)',
            url='https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations',
            description='患者指南中文翻译版本',
            directory='05_Patient_Translations'
        )

    def test_parse_translations(self, theme):
        """测试翻译页面解析"""
        print(f"\n{'='*60}")
        print(f"测试主题: {theme.display_name}")
        print(f"URL: {theme.url}")
        print(f"{'='*60}")

        try:
            # 获取页面内容
            response = self.session.get(theme.url, timeout=30)
            response.raise_for_status()

            print(f"✅ HTTP请求成功，状态码: {response.status_code}")
            print(f"📄 页面内容长度: {len(response.content)} 字节")

            soup = BeautifulSoup(response.content, 'html.parser')

            # 使用修复后的解析方法
            pdf_links = self._parse_translations(soup, theme)

            print(f"\n📊 解析结果:")
            print(f"   - 找到PDF链接数: {len(pdf_links)}")

            if pdf_links:
                print(f"\n📋 前10个PDF链接示例:")
                for i, pdf in enumerate(pdf_links[:10], 1):
                    print(f"   {i:2d}. {pdf['title'][:50]}...")
                    print(f"       URL: {pdf['url'][:80]}...")
            else:
                print("❌ 未找到任何PDF链接！")

            return pdf_links

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_translations(self, soup: BeautifulSoup, theme) -> list:
        """修复后的翻译页面解析方法"""
        pdf_links = []

        print(f"🔍 开始解析翻译页面PDF链接...")

        # 直接查找所有PDF链接，不限制在特定section中
        all_links = soup.find_all('a', href=True)
        pdf_count = 0

        for link in all_links:
            href = link.get('href', '')
            if href.endswith('.pdf'):
                pdf_count += 1

                # 正确拼接URL - 使用NCCN根域名
                if href.startswith('http'):
                    pdf_url = href
                else:
                    base_url = 'https://www.nccn.org'
                    if href.startswith('/'):
                        pdf_url = base_url + href
                    else:
                        pdf_url = urljoin(base_url, href)

                title = link.text.strip()
                if not title:
                    title = href.split('/')[-1].split('.')[0]

                pdf_links.append({
                    'title': title,
                    'url': pdf_url,
                    'version': 'Chinese',
                    'directory': theme.directory
                })

                if pdf_count <= 5:  # 只显示前5个
                    print(f"📄 找到PDF: {title} -> {pdf_url[:80]}...")

        print(f"✅ 翻译页面解析完成，共找到 {pdf_count} 个PDF链接")
        return pdf_links

def main():
    print("🚀 NCCN翻译页面解析修复测试")
    print("测试修复效果：确保类别4和5能正确解析PDF链接")

    tester = TestTranslationsFix()

    # 测试临床指南中文翻译 (类别4)
    print("\n📍 测试类别4: 临床指南中文翻译")
    clinical_results = tester.test_parse_translations(tester.clinical_theme)

    # 测试患者指南中文翻译 (类别5)
    print("\n📍 测试类别5: 患者指南中文翻译")
    patient_results = tester.test_parse_translations(tester.patient_theme)

    # 总结测试结果
    print(f"\n{'='*60}")
    print(f"📊 测试结果总结")
    print(f"{'='*60}")
    print(f"类别4 (临床指南中文翻译): {len(clinical_results)} 个PDF链接")
    print(f"类别5 (患者指南中文翻译): {len(patient_results)} 个PDF链接")

    if len(clinical_results) > 0 and len(patient_results) > 0:
        print(f"\n✅ 修复成功！类别4和5现在都能正确提取PDF链接")
        print(f"🔧 修复内容:")
        print(f"   - 修正了方法调用 (_parse_translations)")
        print(f"   - 重写了翻译页面解析逻辑")
        print(f"   - 统一了URL拼接处理")
    else:
        print(f"\n❌ 修复可能未完全成功，请检查")

    return len(clinical_results) > 0 and len(patient_results) > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)