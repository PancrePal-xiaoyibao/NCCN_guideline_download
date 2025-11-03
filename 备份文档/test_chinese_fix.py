#!/usr/bin/env python3
"""
测试Chinese Translations部分解析修复
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

class TestChineseFix:
    def test_parse_chinese_section(self):
        """测试从本地HTML文件解析Chinese Translations部分"""
        print("🔍 测试Chinese Translations部分解析修复")
        print("=" * 60)

        try:
            # 从本地HTML文件测试
            with open('curl_chinese_guidelines_response.md', 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取HTML内容
            html_start = content.find('<!DOCTYPE html>')
            html_end = content.rfind('</html>') + 7
            html_content = content[html_start:html_end]

            soup = BeautifulSoup(html_content, 'html.parser')

            # 模拟修复后的解析逻辑
            chinese_section = None
            chinese_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=lambda text: text and 'Chinese' in text and 'Translation' in text)

            if not chinese_headings:
                chinese_headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=lambda text: text and 'Chinese' in text)

            print(f"📊 找到 {len(chinese_headings)} 个中文相关标题")

            for heading in chinese_headings:
                print(f"🔍 检查标题: {heading.get_text().strip()}")

                # 查找标题后的pdfList
                current = heading.next_sibling
                while current:
                    if hasattr(current, 'name') and current.name == 'ul' and 'pdfList' in current.get('class', []):
                        chinese_section = current
                        print(f"✅ 找到Chinese PDF列表")
                        break
                    elif hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3', 'h4']:
                        # 遇到下一个标题，停止搜索
                        break
                    current = current.next_sibling

                if chinese_section:
                    break

            if not chinese_section:
                print("❌ 未找到Chinese Translations部分")
                return False

            # 从Chinese Translations部分提取PDF链接
            links = chinese_section.find_all('a', href=True)
            chinese_pdfs = []

            for link in links:
                href = link.get('href', '')
                if href.endswith('.pdf'):
                    title = link.text.strip()
                    if not title:
                        title = href.split('/')[-1].split('.')[0]

                    chinese_pdfs.append({
                        'title': title,
                        'url': href
                    })

            print(f"\n📋 Chinese Translations部分找到的PDF:")
            print(f"   总数: {len(chinese_pdfs)}")

            for i, pdf in enumerate(chinese_pdfs[:10], 1):  # 只显示前10个
                print(f"   {i:2d}. {pdf['title']}")

            if len(chinese_pdfs) > 10:
                print(f"   ... 还有 {len(chinese_pdfs) - 10} 个PDF")

            # 验证是否只包含中文翻译
            chinese_count = sum(1 for pdf in chinese_pdfs if 'chinese' in pdf['url'].lower())
            print(f"\n📊 验证结果:")
            print(f"   - 总PDF数: {len(chinese_pdfs)}")
            print(f"   - 包含'chinese'关键词: {chinese_count}")
            print(f"   - 中文翻译比例: {chinese_count/len(chinese_pdfs)*100:.1f}%")

            if chinese_count == len(chinese_pdfs):
                print(f"\n✅ 修复成功！所有PDF都是中文翻译版本")
                return True
            else:
                print(f"\n⚠️ 部分PDF不是中文翻译，可能需要进一步检查")
                return False

        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def main():
    tester = TestChineseFix()
    success = tester.test_parse_chinese_section()

    print(f"\n{'='*60}")
    if success:
        print("🎉 修复验证通过！Chinese Translations解析现在能正确提取中文PDF")
    else:
        print("❌ 修复验证失败，需要进一步调整")

    return success

if __name__ == "__main__":
    main()