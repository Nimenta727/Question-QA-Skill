# 2026-11-20 — P2 可复现发行包 / Reproducible distribution

## 本次改动
- 新增 VERSION=0.4.0、CHANGELOG.md 和 scripts/build_release.py。
- 输出单 ZIP，内含 SKILL、脚本、演示题库、说明、研究记录和回归测试；固定压缩条目排序和时间戳，支持重复构建得到相同文件。
- 在压缩包内放入 manifest.json，对每个文件保存 SHA256；build --verify 读取并逐一校验，缺失/篡改直接报错。
- 显式白名单排除本地学生记录、私有数据、Git 配置、缓存以及公开研究数据原始文件；只保留无隐私的已验证发行内容。
- 增加 tests/test_package.py 检验打包结果可重复、隐私安全及篡改防护。

## 下一步
1. 发布双语安装和学生反馈使用手册。
2. 配置自动化发行包构建、从包解压后运行 smoke test，以及正式 GitHub Release。
3. 通过 Python 3.9/3.12 CI，查验可下载的 Release 及 SHA256 校验文件。
