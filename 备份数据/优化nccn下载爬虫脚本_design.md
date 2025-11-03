需求：
1) 构建main函数，通过菜单选择，支持下载不同主题的指南文件
2）根据选择的对象，分类检查和建立对应主题的目录，避免重复建立，支持增量下载
3）指南目录根据nccn的主页菜单自动更新：
https://www.nccn.org/guidelines/category_1 - Treatment by Cancer Type
https://www.nccn.org/guidelines/category_3 - Supportive Care
https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients - Patientsguide患者手册
https://www.nccn.org/global/what-we-do/clinical-guidelines-translations - 临床指南翻译，默认下载Chinese Translations的pdf list文件
https://www.nccn.org/global/what-we-do/guidelines-for-patients-translations - 患者指南翻译，默认下载Chinese Translations的pdf list文件
4. 支持两种登陆方法：
4.1. user/pw登陆，支持在菜单交互过程中配置
4.2. cookie登陆，默认从环境变量中读取COOKIE，支持菜单交互中手动配置
4.3  每个主题下载完成后，日志中显示下载统计信息，包括下载的文件数量，下载时间，失败文件数量和名称清单，并对失败文件进行提示，确认后，执行重新下载。
4.4. 对于https://www.nccn.org/guidelines/category_1的页面连接，应该遍历方式对所有癌种进行页面编码提取，凭借为https://www.nccn.org/guidelines/guidelines-detail?category=1&id=<xxxx>,提取response中的内容, 

# NCCN全集主页的curl/response内容
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_nccn_guilde_mainpage.md
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_nccn_guilde_mainpage_response.md
提取list
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/nccnlist.md

# 英文患者指南全套curl/response
主页提取子页面链接，获取和拼接子页面url -> 访问子页面url，提取英文pdf链接，拼接完整链接 -> 下载完整文件
主页入口链接:
子页面链接提取：


# 原来的脚本reference：
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/download_NCCN_Guide.py，这个脚本无法覆盖以上不同主题，是手工单一配置的逻辑，不太友好。

# 《中文患者手册指南中文翻译版本》的curl/response内容

/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_patient_care.md
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/patient_care_reponse.md

# 《NCCN指南中文版本》的curl/response内容
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_chinese_guidelines.md
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_chinese_guidelines_response.md

# 《NCCN患者指南英文和中文版本》：中文不全，英文是全套。
1.先从 /Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_eng_patient_guideline.md，获取子页面链接，并拼接为正确的页面；               <div class="item">
                    <div class="item-name">
                        <a href="/patientresources/patient-resources/guidelines-for-patients/guidelines-for-patients-details?patientGuidelineId=58">Anal Cancer</a>
                    </div>

                    拼接的链接例子：https://www.nccn.org/patientresources/patient-resources/guidelines-for-patients/guidelines-for-patients-details?patientGuidelineId=58

2. 从拼接的子页面中获取pdf链接，只提取chinese和english的pdf文件，并下载。增加单独的主菜单选项。
/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_encn_patient_guideline.md 提供了详细的curl/response/以及拼接链接样本例子。
## 提取链接

### 英文pdf文件的格式例子：注意文件名就是癌种名称+ -patient.pdf
           <div class="row">
                <div class="col-md-12 item-header"><a href="/patients/guidelines/content/PDF/anal-patient.pdf" target="_blank" onclick="openPDWindow()">Anal Cancer</a></div>

### 中文格式的例子：注意文件名中带有个-zh-patient.pdf
            <div class="col-md-12 item-header">
                <a href="/patients/guidelines/content/PDF/Bladder-zh-patient.pdf">
                    Bladder Cancer - Chinese
                </a>
            </div>

拼接后的链接是：
- english文件链接样本：https://www.nccn.org/patients/guidelines/content/PDF/anal-patient.pdf
- chinese文件链接样本：https://www.nccn.org/patients/guidelines/content/PDF/Bladder-zh-patient.pdf

请你创建新的爬虫下载脚本，单独命名为download_NCCN_Guide_v2_menu.py

# 检查
检查一下：从指南主页mainpage获得的reponse中提取第一次，拼接出具体癌种的子页面，比如https://www.nccn.org/guidelines/guidelines-detail?category=1&id=
  1410，然后通过获取response，再提取pdf文档链接，拼接为https://www.nccn.org/professionals/physician_gls/pdf/all.pdf，检查下代码是否满足。 

- 检查一下：
参考/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_patient_guide_translate.md ，以及/Users/qinxiaoqiang/Downloads/NCCN下载脚本/curl_patient_guide_translate_res.md，找到带chinese的pdf链接下载，拼接完成的链接是https://www.nccn.org/patients/guidelines/content/PDF/Bladder-zh-patient.pdf。其它语言的不需要下载。 