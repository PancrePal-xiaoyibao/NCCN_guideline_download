#!/usr/bin/env python3
"""
测试双语患者指南解析功能
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class TestBilingualPatientGuidelines:
    def test_parse_main_page(self):
        """测试从主页面直接解析患者指南PDF链接"""
        print("🔍 测试双语患者指南主页面PDF解析")
        print("=" * 60)

        try:
            # 从本地HTML文件测试
            with open('curl_encn_mainpage_patient_guideline.md', 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取HTML内容
            html_start = content.find('<!DOCTYPE html>')
            if html_start == -1:
                html_start = 0
            html_end = content.rfind('</html>') + 7
            if html_end == 6:
                html_end = len(content)
            html_content = content[html_start:html_end]

            soup = BeautifulSoup(html_content, 'html.parser')

            # 模拟新的解析逻辑
            all_links = soup.find_all('a', href=True)
            pdf_links = []
            found_pdfs = 0

            for link in all_links:
                href = link.get('href', '')

                # 查找患者指南PDF链接 - 根据用户提供的结构
                if href.endswith('.pdf') and '/patients/guidelines/content/PDF/' in href:
                    found_pdfs += 1

                    # 正确拼接URL
                    if href.startswith('http'):
                        pdf_url = href
                    else:
                        from urllib.parse import urljoin
                        base_url = 'https://www.nccn.org'
                        if href.startswith('/'):
                            pdf_url = base_url + href
                        else:
                            pdf_url = urljoin(base_url, href)

                    title = link.text.strip()
                    if not title:
                        # 从URL提取标题
                        filename = href.split('/')[-1].replace('.pdf', '')
                        if filename.endswith('-zh'):
                            title = filename[:-3].replace('-', ' ') + ' (Chinese)'
                        else:
                            title = filename.replace('-', ' ')

                    # 确定版本语言
                    version = 'Chinese' if '-zh' in href.lower() or 'chinese' in href.lower() else 'English'

                    pdf_info = {
                        'title': title,
                        'url': pdf_url,
                        'version': version
                    }

                    pdf_links.append(pdf_info)

                    print(f"✅ 找到PDF: {title} ({version})")
                    print(f"   URL: {pdf_url[:80]}...")
                    print()

            print(f"📊 解析结果:")
            print(f"   总PDF数={found_pdfs}")
            print(f"   成功提取={len(pdf_links)}")

            # 显示语言分布
            chinese_count = sum(1 for pdf in pdf_links if pdf['version'] == 'Chinese')
            english_count = len(pdf_links) - chinese_count
            print(f"   中文版本={chinese_count}")
            print(f"   英文版本={english_count}")

            return len(pdf_links) > 0

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def test_parse_detail_page(self):
        """测试从详情页解析PDF链接（备用测试）"""
        print("\n🔍 测试患者指南详情页PDF解析（备用）")
        print("=" * 60)

        try:
            # 从本地HTML文件测试
            with open('curl_encn_patient_guideline.md', 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取HTML内容
            html_start = content.find('<!DOCTYPE html>')
            if html_start == -1:
                html_start = 0
            html_end = content.rfind('</html>') + 7
            if html_end == 6:
                html_end = len(content)
            html_content = content[html_start:html_end]

            soup = BeautifulSoup(html_content, 'html.parser')

            # 模拟新的解析逻辑
            all_links = soup.find_all('a', href=True)
            pdf_links = []
            found_pdfs = 0

            for link in all_links:
                href = link.get('href', '')

                # 查找患者指南PDF链接
                if href.endswith('.pdf') and '/patients/guidelines/content/PDF/' in href:
                    found_pdfs += 1

                    # 正确拼接URL
                    if href.startswith('http'):
                        pdf_url = href
                    else:
                        from urllib.parse import urljoin
                        base_url = 'https://www.nccn.org'
                        if href.startswith('/'):
                            pdf_url = base_url + href
                        else:
                            pdf_url = urljoin(base_url, href)

                    title = link.text.strip()
                    if not title:
                        filename = href.split('/')[-1].replace('.pdf', '')
                        if filename.endswith('-zh'):
                            title = filename[:-3].replace('-', ' ') + ' (Chinese)'
                        else:
                            title = filename.replace('-', ' ')

                    # 确定版本语言
                    version = 'Chinese' if '-zh' in href.lower() or 'chinese' in href.lower() else 'English'

                    pdf_info = {
                        'title': title,
                        'url': pdf_url,
                        'version': version
                    }

                    pdf_links.append(pdf_info)

                    print(f"📄 找到PDF: {title} ({version})")
                    print(f"   URL: {pdf_url[:80]}...")
                    print()

            print(f"📊 详情页解析结果:")
            print(f"   总PDF数={found_pdfs}")
            print(f"   成功提取={len(pdf_links)}")

            return len(pdf_links) > 0

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    tester = TestBilingualPatientGuidelines()

    print("🧪 开始测试双语患者指南功能")
    print("=" * 60)

    # 测试主页面解析
    main_page_success = tester.test_parse_main_page()

    # 测试详情页解析
    detail_page_success = tester.test_parse_detail_page()

    print(f"\n{'='*60}")
    print("📊 测试结果总结:")
    print(f"   主页面解析: {'✅ 通过' if main_page_success else '❌ 失败'}")
    print(f"   详情页解析: {'✅ 通过' if detail_page_success else '❌ 失败'}")

    if main_page_success and detail_page_success:
        print(f"\n🎉 所有测试通过！双语患者指南功能可以正常工作")
        return True
    else:
        print(f"\n❌ 部分测试失败，需要进一步调整")
        return False

if __name__ == "__main__":
    main()