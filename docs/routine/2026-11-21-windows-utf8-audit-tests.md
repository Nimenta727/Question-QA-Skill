# 2026-11-21 — Windows下UTF-8诊断记录读取兼容修复

## 本次修改
- 新版演示题库添加了中文“可能的误区”标签，在Windows CI中暴露了旧测试使用Path.read_text()默认系统代码页读取UTF-8学习记录的问题；表现为UnicodeDecodeError而非评分或审题失败。
- 在tests/test_tutor_core.py、tests/test_v080.py、tests/test_v090.py全部将隐式read_text()改成显式read_text(encoding="utf-8")，包括私有状态、凭据、收据等测试文件，保持跨平台JSON协议一致。
- 保留中文知识诊断内容，不把真实用户数据改成系统本地编码；生产端state_store仍按UTF-8写入和校验，测试也按同样约定处理。

## 下一步
1. 再运行Linux、macOS、Windows的完整测试矩阵和发行门槛。
2. 只有6/6完整回归与3系统发行解压通过后才确认v1.1.0成功。
3. 进一步核对正式ZIP包含严格模型审题模块、双语说明及完整合成回归。
