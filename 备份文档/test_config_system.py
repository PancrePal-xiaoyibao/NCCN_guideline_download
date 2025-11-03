#!/usr/bin/env python3
"""
测试修改后的配置系统
"""

import json
import os

def test_config_loading():
    """测试配置加载"""
    print("🧪 测试配置系统...")
    print("=" * 60)

    # 测试1: 检查配置文件是否存在
    config_file = 'config.json'
    if os.path.exists(config_file):
        print(f"✅ 配置文件 {config_file} 存在")
    else:
        print(f"❌ 配置文件 {config_file} 不存在")
        return False

    # 测试2: 读取和解析配置
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"✅ 配置文件解析成功")
    except Exception as e:
        print(f"❌ 配置文件解析失败: {e}")
        return False

    # 测试3: 检查认证配置
    auth_config = config_data.get('authentication', {})
    method = auth_config.get('method', 'username_password')
    username = auth_config.get('username', '')
    password = auth_config.get('password', '')
    cookie_file = auth_config.get('cookie_file', 'extracted_cookies.txt')

    print(f"\n📋 认证配置:")
    print(f"   认证方式: {method}")
    print(f"   用户名: {username if username else '未设置'}")
    print(f"   密码: {'已设置' if password and password != 'your_password_here' else '未设置或使用默认值'}")
    print(f"   Cookie文件: {cookie_file}")

    # 测试4: 验证配置完整性
    print(f"\n🔍 配置完整性检查:")

    if method == 'username_password':
        if not username:
            print(f"   ❌ 用户名为空")
            config_valid = False
        elif not password or password == 'your_password_here':
            print(f"   ❌ 密码未正确设置")
            config_valid = False
        else:
            print(f"   ✅ 用户名/密码配置完整")
            config_valid = True

    elif method == 'cookie':
        if not os.path.exists(cookie_file):
            print(f"   ❌ Cookie文件不存在: {cookie_file}")
            config_valid = False
        else:
            try:
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookie_content = f.read().strip()
                if cookie_content:
                    print(f"   ✅ Cookie认证配置完整")
                    config_valid = True
                else:
                    print(f"   ❌ Cookie文件为空")
                    config_valid = False
            except Exception as e:
                print(f"   ❌ 读取Cookie文件失败: {e}")
                config_valid = False

    else:
        print(f"   ❌ 不支持的认证方式: {method}")
        config_valid = False

    # 测试5: 检查程序是否可以导入
    print(f"\n🐍 程序模块检查:")
    try:
        import sys
        sys.path.insert(0, '.')
        from download_NCCN_Guide_v2_menu import NCCNDownloaderV2, main
        print(f"   ✅ 程序模块导入成功")
        program_valid = True
    except Exception as e:
        print(f"   ❌ 程序模块导入失败: {e}")
        program_valid = False

    # 总结
    print(f"\n{'='*60}")
    print(f"📊 测试结果总结:")
    print(f"   配置文件: {'✅ 正常' if os.path.exists(config_file) else '❌ 异常'}")
    print(f"   配置解析: {'✅ 正常' if config_data else '❌ 异常'}")
    print(f"   配置完整性: {'✅ 正常' if config_valid else '❌ 异常'}")
    print(f"   程序模块: {'✅ 正常' if program_valid else '❌ 异常'}")

    overall_success = os.path.exists(config_file) and config_data and config_valid and program_valid

    if overall_success:
        print(f"\n🎉 配置系统测试通过！")
        print(f"✅ 可以使用以下命令运行程序:")
        print(f"   python download_NCCN_Guide_v2_menu.py")
        if method == 'username_password':
            print(f"   认证方式: 用户名/密码 ({username})")
        else:
            print(f"   认证方式: Cookie ({cookie_file})")
    else:
        print(f"\n⚠️  配置系统需要修复")
        print(f"🔧 请检查上述错误并修复")

    return overall_success

def show_menu_options():
    """显示菜单选项"""
    print(f"\n📋 当前菜单选项:")
    print(f"1. 癌症治疗指南 (Treatment by Cancer Type)")
    print(f"2. 支持性护理指南 (Supportive Care) - 支持语言过滤")
    print(f"3. 患者指南 (Patient Guidelines)")
    print(f"4. 临床指南中文翻译 (Clinical Translations)")
    print(f"5. 患者指南中文翻译 (Patient Guidelines Translations)")
    print(f"6. 患者指南中英文版本 (Bilingual Patient Guidelines) - 支持语言过滤")
    print(f"7. 查看下载统计")
    print(f"8. 退出")

if __name__ == "__main__":
    print("🔧 NCCN下载工具配置系统测试")
    print("=" * 60)

    # 运行测试
    success = test_config_loading()

    # 显示菜单选项
    show_menu_options()

    print(f"\n{'='*60}")
    if success:
        print("🚀 程序已准备就绪，可以开始下载！")
    else:
        print("⚠️  请修复配置问题后再运行程序")