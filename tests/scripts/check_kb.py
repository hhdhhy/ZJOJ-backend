from apps.ai_assistant.models import KnowledgeBase

# 检查现有知识库文档数量
count = KnowledgeBase.objects.count()
print(f'当前知识库文档数: {count}')

if count > 0:
    # 显示前5个文档
    docs = KnowledgeBase.objects.all()[:5]
    for doc in docs:
        print(f'ID: {doc.id}, Title: {doc.title[:30]}, Type: {doc.doc_type}, Error: {doc.error_type}')
else:
    print('知识库为空，需要添加错误解决方案文档')
