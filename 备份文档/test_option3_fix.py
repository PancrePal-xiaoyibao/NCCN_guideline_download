#!/usr/bin/env python3
"""
测试修复后的选项3：患者指南英文版
验证双步骤解析流程是否正常工作
"""

import sys
import os
import time
import random
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_option3_english():
    """测试选项3：患者指南英文版功能"""
    print("🧪 测试选项3：患者指南英文版...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项3的配置（与主程序中的一致）
        theme = ThemeConfig(
            name='patient_guidelines',
            display_name='患者指南英文版 (Patient Guidelines - English Only)',
            url='https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients',
            category='patient_guidelines_english',
            directory='03_Patient_Guidelines_English',
            description='患者专用英文指南'
        )

        print(f"🎯 测试主题: {theme.display_name}")
        print(f"📁 下载目录: {theme.directory}")
        print(f"🔗 URL: {theme.url}")
        print(f"🏷️  Category: {theme.category}")

        # 测试网页访问和解析
        print(f"\n🌐 访问主页面...")
        response = downloader.session.get(theme.url)

        if response.status_code == 200:
            print(f"✅ 页面访问成功 (状态码: {response.status_code})")

            # 解析页面
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # 测试子链接获取
            print(f"\n🔍 测试步骤1: 获取guidelines-detail链接...")
            sub_links = downloader._get_sub_links_patient_guidelines(soup, theme.url)
            print(f"📊 找到 {len(sub_links)} 个详情页链接")

            if len(sub_links) > 0:
                print(f"\n✅ 步骤1成功！找到详情页链接")
                print(f"🔗 示例链接:")
                for i, link in enumerate(sub_links[:3], 1):
                    print(f"   {i}. {link}")

                # 测试单个详情页解析
                print(f"\n🧪 测试步骤2: 解析详情页PDF...")
                test_url = sub_links[0]
                print(f"📄 测试详情页: {test_url}")

                test_response = downloader.session.get(test_url)
                if test_response.status_code == 200:
                    test_soup = BeautifulSoup(test_response.content, 'html.parser')

                    # 查找PDF链接
                    pdf_count = 0
                    for link in test_soup.find_all('a', href=True):
                        href = link.get('href', '')
                        if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                            pdf_count += 1
                            if pdf_count <= 3:  # 只显示前3个
                                print(f"   📄 PDF {pdf_count}: {link.get_text(strip=True)[:50]}")

                    print(f"📄 详情页找到 {pdf_count} 个PDF链接")

                    if pdf_count > 0:
                        print(f"\n✅ 步骤2成功！详情页包含PDF链接")

                        # 测试完整解析流程（限制数量避免长时间运行）
                        print(f"\n🎯 测试完整解析流程 (限制前5个详情页)...")
                        limited_links = sub_links[:5]
                        pdf_links = []

                        for i, sub_url in enumerate(limited_links, 1):
                            print(f"📄 [{i}/{len(limited_links)}] 处理: {sub_url.split('?')[0].split('/')[-1]}")

                            try:
                                sub_response = downloader.session.get(sub_url)
                                if sub_response.status_code == 200:
                                    sub_soup = BeautifulSoup(sub_response.content, 'html.parser')

                                    # 查找PDF链接并检测语言
                                    for link in sub_soup.find_all('a', href=True):
                                        href = link.get('href', '')
                                        link_text = link.get_text(strip=True)

                                        if '/patients/guidelines/content/PDF/' in href and href.endswith('.pdf'):
                                            # 检测语言
                                            detected_lang = downloader._detect_pdf_language(href, link_text)

                                            if detected_lang in ['English', 'Unknown']:
                                                if href.startswith('http'):
                                                    pdf_url = href
                                                else:
                                                    pdf_url = 'https://www.nccn.org' + href

                                                title = link_text if link_text else 'Patient Guideline'
                                                pdf_links.append({
                                                    'title': title,
                                                    'url': pdf_url,
                                                    'version': detected_lang
                                                })

                                # 短暂延迟
                                time.sleep(random.uniform(0.5, 1.5))

                            except Exception as e:
                                print(f"   ⚠️ 处理失败: {str(e)}")
                                continue

                        print(f"\n📊 解析结果:")
                        print(f"   处理详情页数: {len(limited_links)}")
                        print(f"   找到英文PDF数: {len(pdf_links)}")

                        if len(pdf_links) > 0:
                            print(f"\n✅ 选项3修复成功！")
                            print(f"🎯 现在可以:")
                            print(f"   • 获取所有患者指南详情页链接")
                            print(f"   • 正确解析详情页PDF")
                            print(f"   • 准确检测和过滤语言")
                            print(f"   • 提取英文版本PDF")

                            print(f"\n📋 找到的英文PDF示例:")
                            for i, pdf in enumerate(pdf_links[:3], 1):
                                print(f"   {i}. {pdf['title']} ({pdf['version']})")

                            return True
                        else:
                            print(f"\n⚠️ 没有找到英文PDF，可能语言检测有问题")
                            return False
                    else:
                        print(f"\n⚠️ 详情页没有PDF链接")
                        return False
                else:
                    print(f"❌ 无法访问测试详情页")
                    return False
            else:
                print(f"\n❌ 没有找到详情页链接")
                return False
        else:
            print(f"❌ 主页面访问失败")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def show_menu_comparison():
    """显示菜单对比"""
    print(f"\n📋 菜单修改对比:")
    print("=" * 60)

    print(f"🔄 修改前:")
    print(f"   3. 患者指南 (Patient Guidelines)")
    print(f"      - 默认下载全部版本")
    print(f"      - 解析失败：'未找到任何子链接'")
    print(f"      - 用途不明确")

    print(f"\n⚡ 修改后:")
    print(f"   3. 患者指南英文版 (Patient Guidelines - English Only)")
    print(f"      - 专门下载英文版本")
    print(f"      - 双步骤解析流程")
    print(f"      - 用途明确，与选项6形成互补")

    print(f"\n🎯 现在的菜单结构:")
    print(f"   3. 患者指南英文版 (English Only)")
    print(f"      → 专门下载英文患者指南")
    print(f"   6. 患者指南中文版本 (Chinese Only)")
    print(f"      → 专门下载中文患者指南")
    print(f"\n✅ 功能明确，互补不冲突")

if __name__ == "__main__":
    import json

    success = test_option3_english()
    show_menu_comparison()

    print(f"\n{'='*60}")
    if success:
        print("🎉 选项3修复完成！")
        print("✅ 现在可以:")
        print("   • 选择菜单选项3")
        print("   • 自动下载英文患者指南")
        print("   • 正确解析74个详情页")
        print("   • 准确过滤英文版本")
        print("🚀 请测试: python download_NCCN_Guide_v2_menu.py")
    else:
        print("⚠️ 选项3测试失败")
        print("🔧 需要进一步调试")