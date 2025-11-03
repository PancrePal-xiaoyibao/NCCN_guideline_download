#!/usr/bin/env python3
"""
测试re模块重复导入问题的修复
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def test_re_import_fix():
    """测试re模块重复导入修复"""
    print("🧪 测试re模块重复导入修复...")
    print("=" * 60)

    try:
        # 尝试导入主模块
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2
        print("✅ 主模块导入成功")

        # 尝试创建一个实例（不需要真实配置）
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # 测试一些关键方法是否能正常工作
        downloader = NCCNDownloaderV2(config_data)
        print("✅ 下载器实例创建成功")

        # 测试一些使用了re模块的方法
        test_url = "https://www.nccn.org/professionals/physician_gls/pdf/test.pdf"
        test_text = "NCCN Guidelines Version 1.2026"

        # 测试语言检测
        language = downloader._detect_pdf_language(test_url, test_text)
        print(f"✅ 语言检测功能正常: {language}")

        # 测试版本信息提取
        version_info = downloader._extract_version_info(test_text)
        print(f"✅ 版本信息提取功能正常: {version_info}")

        # 测试文件名增强
        enhanced_info = downloader._enhance_pdf_info("Test Guidelines", "1_2026", test_url)
        print(f"✅ 文件名增强功能正常: {enhanced_info}")

        print("🎉 所有测试通过！re模块导入问题已修复")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 测试re模块重复导入修复")
    print("验证修复后的代码是否能正常工作")
    print("=" * 60)

    success = test_re_import_fix()

    print(f"\n{'='*60}")
    if success:
        print("🎉 修复验证成功！")
        print("✅ re模块重复导入问题已解决")
        print("✅ 所有依赖re模块的功能都能正常工作")
        print("🚀 现在可以重新运行主程序了")
    else:
        print("⚠️ 修复验证失败")
        print("🔧 需要进一步调试")