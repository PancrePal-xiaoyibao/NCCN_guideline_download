#!/usr/bin/env python3
"""
测试修复后的双语患者指南解析逻辑
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_fixed_bilingual_parsing():
    """测试修复后的双语患者指南解析"""
    print("🧪 测试修复后的双语患者指南解析逻辑...")
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

        # 访问患者指南主页
        url = "https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients"
        print(f"🌐 访问主页面: {url}")

        response = session.get(url)
        print(f"📡 状态码: {response.status_code}")

        if response.status_code != 200:
            print("❌ 主页面访问失败")
            return False

        # 解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # 模拟修复后的解析逻辑
        print(f"\n🔍 步骤1: 从主页面提取患者指南详情页链接...")
        all_links = soup.find_all('a', href=True)
        detail_links = []

        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)

            # 查找详情页链接格式
            if '/guidelines-for-patients-details?patientGuidelineId=' in href:
                # 正确拼接URL
                if href.startswith('http'):
                    detail_url = href
                else:
                    detail_url = 'https://www.nccn.org' + href

                detail_links.append({
                    'url': detail_url,
                    'text': text
                })

        print(f"✅ 步骤1完成，找到 {len(detail_links)} 个患者指南详情页")

        if not detail_links:
            print("❌ 未找到患者指南详情页链接")
            return False

        # 测试访问前几个详情页
        print(f"\n🔍 步骤2: 遍历详情页提取PDF链接...")
        max_pages = min(3, len(detail_links))  # 测试前3个详情页
        found_pdfs = []

        for i, detail in enumerate(detail_links[:max_pages]):
            try:
                print(f"📄 [{i+1}/{max_pages}] 处理详情页: {detail['text']}")

                detail_response = session.get(detail['url'])
                if detail_response.status_code != 200:
                    print(f"   ❌ 无法访问详情页: {detail['url']}")
                    continue

                detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                detail_links_page = detail_soup.find_all('a', href=True)

                page_pdfs = 0
                for link in detail_links_page:
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)

                    # 查找PDF链接
                    if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                        # 正确拼接URL
                        if href.startswith('http'):
                            pdf_url = href
                        else:
                            pdf_url = 'https://www.nccn.org' + href

                        # 确定版本语言
                        version = 'Chinese' if '-zh' in href.lower() or 'chinese' in link_text.lower() else 'English'

                        pdf_info = {
                            'title': link_text if link_text else detail['text'],
                            'url': pdf_url,
                            'version': version,
                            'detail_page': detail['text']
                        }

                        found_pdfs.append(pdf_info)
                        page_pdfs += 1

                        print(f"   📄 PDF: {pdf_info['title']} ({version}) -> {pdf_url[:60]}...")

                print(f"   ✅ 详情页找到 {page_pdfs} 个PDF")

            except Exception as e:
                print(f"   ⚠️  处理详情页失败 {detail['text']}: {str(e)}")
                continue

        # 统计结果
        print(f"\n📊 解析结果统计:")
        print(f"   测试详情页数: {max_pages}")
        print(f"   总PDF文件数: {len(found_pdfs)}")

        chinese_count = sum(1 for pdf in found_pdfs if pdf['version'] == 'Chinese')
        english_count = len(found_pdfs) - chinese_count
        print(f"   中文版本: {chinese_count}")
        print(f"   英文版本: {english_count}")

        if found_pdfs:
            print(f"\n✅ 测试成功！修复后的双步骤解析逻辑正常工作")
            print(f"🎯 可以正确从详情页提取PDF链接")
            return True
        else:
            print(f"\n❌ 测试失败：未找到PDF文件")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_bilingual_parsing()

    print(f"\n{'='*60}")
    if success:
        print("🎉 修复验证成功！")
        print("✅ 双语患者指南解析逻辑现在可以正常工作")
        print("🚀 可以尝试运行主程序下载双语患者指南")
    else:
        print("⚠️  修复验证失败")
        print("🔧 需要进一步调试解析逻辑")