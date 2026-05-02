# -*- coding: utf-8 -*-
"""
修复 error_pusher.py 中的内容截断问题
"""

file_path = r'E:\learning file\ZJOJ\apps\ai_assistant\error_pusher.py'

# 读取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换第51行的截断代码
content = content.replace(
    "'content': doc['content'][:500],  # 截取前500字",
    "'content': doc['content'],  # 返回完整内容，前端通过滚动条展示"
)

# 替换第97行的截断代码
content = content.replace(
    "'content': doc['content'][:300],",
    "'content': doc['content'],  # 返回完整内容，前端通过滚动条展示"
)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 修改完成！")
print("\n修改内容：")
print("1. 第51行: 移除 [:500] 截断")
print("2. 第97行: 移除 [:300] 截断")
print("\n现在后端将返回完整的错误解决方案内容。")
