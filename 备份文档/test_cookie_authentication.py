#!/usr/bin/env python3
"""
测试NCCN Cookie认证的有效性
"""

import requests
import sys
from pathlib import Path
from urllib.parse import urljoin

def test_nccn_cookie():
    """测试NCCN网站的Cookie认证"""
    print("🔍 测试NCCN Cookie认证...")
    print("=" * 60)

    # 读取完整的Cookie字符串
    try:
        with open('extracted_cookies.txt', 'r', encoding='utf-8') as f:
            cookie_string = f.read().strip()
        print("✅ 成功读取Cookie文件")
    except Exception as e:
        print(f"❌ 读取Cookie文件失败: {e}")
        return False

    # 创建会话
    session = requests.Session()

    # 设置请求头，模拟浏览器
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })

    # 解析Cookie字符串
    try:
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value

        print(f"✅ 成功解析 {len(cookies)} 个Cookie")
        print(f"📋 主要认证Cookie: .AspNet.Cookies, username, ASP.NET_SessionId")

    except Exception as e:
        print(f"❌ 解析Cookie失败: {e}")
        return False

    # 更新会话Cookie
    session.cookies.update(cookies)

    # 测试访问受限页面
    test_urls = [
        {
            'name': '患者指南主页面',
            'url': 'https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients',
            'description': '测试是否可以访问双语患者指南页面'
        },
        {
            'name': '临床指南页面',
            'url': 'https://www.nccn.org/guidelines/category_1',
            'description': '测试是否可以访问临床指南'
        },
        {
            'name': '支持性护理指南',
            'url': 'https://www.nccn.org/guidelines/category_2',
            'description': '测试是否可以访问支持性护理指南'
        }
    ]

    success_count = 0
    for test in test_urls:
        print(f"\n🌐 测试访问: {test['name']}")
        print(f"   URL: {test['url']}")
        print(f"   目的: {test['description']}")

        try:
            response = session.get(test['url'], timeout=30)

            # 检查响应状态
            if response.status_code == 200:
                # 检查是否被重定向到登录页面
                if 'login' in response.url.lower():
                    print(f"   ❌ 被重定向到登录页面: {response.url}")
                elif 'login' in response.text.lower() and 'username' in response.text.lower():
                    print(f"   ❌ 页面显示登录表单，认证失败")
                else:
                    print(f"   ✅ 访问成功 (状态码: {response.status_code})")
                    print(f"   📄 页面大小: {len(response.text):,} 字符")
                    success_count += 1

                    # 检查页面内容关键词
                    if 'guidelines' in response.text.lower():
                        print(f"   🎯 页面包含指南相关内容")
                    if 'patient' in response.text.lower():
                        print(f"   👥 页面包含患者相关内容")
            else:
                print(f"   ❌ 访问失败 (状态码: {response.status_code})")

        except Exception as e:
            print(f"   ❌ 请求异常: {e}")

    # 测试结果总结
    print(f"\n{'='*60}")
    print(f"📊 测试结果总结:")
    print(f"   测试页面数: {len(test_urls)}")
    print(f"   成功访问数: {success_count}")
    print(f"   成功率: {success_count/len(test_urls)*100:.1f}%")

    if success_count == len(test_urls):
        print(f"\n🎉 Cookie认证完全成功！")
        print(f"✅ 所有测试页面都可以正常访问")
        print(f"🚀 可以使用Cookie认证运行下载程序")
        return True
    elif success_count > 0:
        print(f"\n⚠️  Cookie认证部分成功")
        print(f"🔄 部分页面可以访问，建议:")
        print(f"   1. 使用用户名密码认证作为主要方式")
        print(f"   2. Cookie认证作为备用方式")
        return True
    else:
        print(f"\n❌ Cookie认证失败")
        print(f"🔧 建议:")
        print(f"   1. 检查Cookie是否过期")
        print(f"   2. 重新登录并提取新的Cookie")
        print(f"   3. 使用用户名密码认证")
        return False

def test_cookie_components():
    """分析Cookie组件"""
    print("\n🔍 分析Cookie组件...")
    print("-" * 40)

    try:
        with open('extracted_cookies.txt', 'r', encoding='utf-8') as f:
            cookie_string = f.read().strip()

        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value

        # 显示主要认证相关的Cookie
        auth_cookies = {
            '.AspNet.Cookies': 'ASP.NET身份验证Cookie (最重要)',
            'username': '用户名',
            'ASP.NET_SessionId': '会话标识',
            'customerid': '客户ID',
            'customerguid': '客户GUID',
            'sessionguid': '会话GUID',
            'IsNCCNUser': 'NCCN用户标识',
            'IsCustomerOfMemInst': '机构成员标识',
            'IsCOIMember': 'COI成员标识',
            'IsBoardMember': '董事会成员标识'
        }

        print("🗝️  关键认证组件:")
        for key, desc in auth_cookies.items():
            if key in cookies:
                value = cookies[key]
                if len(value) > 50:
                    display_value = value[:50] + "..."
                else:
                    display_value = value
                print(f"   ✅ {key}: {display_value} ({desc})")
            else:
                print(f"   ❌ {key}: 缺失 ({desc})")

        # 检查其他重要Cookie
        other_cookies = {
            'PDFSession': 'PDF会话',
            'ExternalCookie_qinxiaoqiang@gmail.com': '外部Cookie',
            'sf-prs-ss': 'SF会话',
            '_ga': 'Google Analytics',
            '_gcl_gs': 'Google转化跟踪'
        }

        print(f"\n🔧 其他重要组件:")
        for key, desc in other_cookies.items():
            if key in cookies:
                print(f"   ✅ {key}: 已包含 ({desc})")
            else:
                print(f"   - {key}: 不存在 ({desc})")

    except Exception as e:
        print(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    print("🧪 NCCN Cookie认证测试工具")
    print("=" * 60)

    # 分析Cookie组件
    test_cookie_components()

    # 测试认证有效性
    auth_success = test_nccn_cookie()

    print(f"\n{'='*60}")
    if auth_success:
        print("🎯 测试完成：Cookie认证可用")
        print("💡 建议：可以尝试使用Cookie认证运行下载程序")
    else:
        print("⚠️  测试完成：Cookie认证需要改进")
        print("💡 建议：使用用户名密码认证作为主要方式")