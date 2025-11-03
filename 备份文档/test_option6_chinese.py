#!/usr/bin/env python3
"""
测试新的选项6：患者指南中文版本
验证直接访问翻译页面功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_option6_chinese():
    """测试选项6：患者指南中文版本功能"""
    print("🧪 测试选项6：患者指南中文版本...")
    print("=" * 60)

    try:
        # 读取配置文件
        config_file = 'config.json'
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 初始化下载器
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, ThemeConfig

        downloader = NCCNDownloaderV2(config_data)

        # 创建选项6的配置（与主程序中的一致）
        theme = ThemeConfig(
            name='patient_guidelines_chinese',
            display_name='患者指南中文版本 (Chinese Patient Guidelines)',
            url='https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations',
            category='patient_guidelines_chinese',
            directory='06_Chinese_Patient_Guidelines',
            description='患者指南中文翻译版本下载',
            has_language_filter=False
        )

        print(f"🎯 测试主题: {theme.display_name}")
        print(f"📁 下载目录: {theme.directory}")
        print(f"🔗 URL: {theme.url}")

        # 测试网页访问和解析
        print(f"\n🌐 访问翻译页面...")
        response = downloader.session.get(theme.url)

        if response.status_code == 200:
            print(f"✅ 页面访问成功 (状态码: {response.status_code})")

            # 解析页面
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # 使用新的解析方法
            pdf_links = downloader._parse_patient_guidelines_chinese(soup, theme)

            print(f"\n📊 解析结果:")
            print(f"   找到中文PDF数量: {len(pdf_links)}")

            if len(pdf_links) >= 10:
                print(f"\n🎉 测试成功！")
                print(f"✅ 选项6现在可以:")
                print(f"   • 直接访问翻译页面")
                print(f"   • 自动解析Chinese Translations部分")
                print(f"   • 找到所有中文PDF文件")
                print(f"   • 无需语言过滤（默认中文）")

                print(f"\n📋 找到的中文PDF示例:")
                for i, pdf in enumerate(pdf_links[:5], 1):
                    print(f"   {i}. {pdf['title']}")

                if len(pdf_links) > 5:
                    print(f"   ... 还有 {len(pdf_links) - 5} 个文件")

                return True
            else:
                print(f"\n⚠️  只找到 {len(pdf_links)} 个中文PDF，期望找到10+个")
                return False
        else:
            print(f"❌ 页面访问失败 (状态码: {response.status_code})")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def simulate_menu_selection():
    """模拟菜单选择过程"""
    print(f"\n📋 模拟新的菜单选择体验:")
    print("=" * 60)

    print(f"🔄 旧版本菜单:")
    print(f"   3. 患者指南 (Patient Guidelines)")
    print(f"   6. 患者指南中英文版本 (Bilingual Patient Guidelines)")
    print(f"      - 需要语言选择: 1(全部)/2(英文)/3(中文)")
    print(f"      - 选择中文时仍然需要扫描主页")

    print(f"\n⚡ 新版本菜单:")
    print(f"   3. 患者指南 (Patient Guidelines)")
    print(f"      - 英文版本下载")
    print(f"   6. 患者指南中文版本 (Chinese Patient Guidelines)")
    print(f"      - 默认下载中文翻译")
    print(f"      - 直接访问翻译页面")
    print(f"      - 无需语言过滤")

    print(f"\n🎯 用户体验改进:")
    print(f"   • 选项6专注于中文版本")
    print(f"   • 简化操作：选择6即可下载中文")
    print(f"   • 性能优化：跳过主页扫描")
    print(f"   • 明确用途：一看就知道是中文版")

if __name__ == "__main__":
    import json

    success = test_option6_chinese()
    simulate_menu_selection()

    print(f"\n{'='*60}")
    if success:
        print("🎉 选项6修改完成！")
        print("✅ 现在可以:")
        print("   • 选择菜单选项6")
        print("   • 直接下载所有中文患者指南")
        print("   • 无需额外的语言过滤选择")
        print("🚀 请测试: python download_NCCN_Guide_v2_menu.py")
    else:
        print("⚠️  选项6测试失败")
        print("🔧 需要进一步调试")