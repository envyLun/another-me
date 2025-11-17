"""
快速测试文档解析模块
"""

import asyncio
import tempfile
from pathlib import Path
from ame.foundation.file import DocumentParsePipeline, parse_document, SectionType


async def test_basic_functionality():
    """测试基础功能"""
    print("=" * 60)
    print("测试文档解析模块基础功能")
    print("=" * 60 + "\n")
    
    # 1. 测试文本解析
    print("1. 测试文本解析")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("第一段内容\n\n第二段内容\n\n第三段内容")
        txt_path = f.name
    
    try:
        doc = await parse_document(txt_path)
        print(f"✓ 格式: {doc.format}")
        print(f"✓ 字符数: {doc.total_chars}")
        print(f"✓ 章节数: {len(doc.sections)}")
        print(f"✓ 段落数: {len(doc.get_paragraphs())}")
        print()
    finally:
        Path(txt_path).unlink()
    
    # 2. 测试Markdown解析
    print("2. 测试Markdown解析")
    print("-" * 40)
    
    md_content = """# 一级标题

这是一个段落。

## 二级标题

- 列表项1
- 列表项2

```python
def hello():
    print("Hello World")
```

### 三级标题

另一个段落。
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write(md_content)
        md_path = f.name
    
    try:
        doc = await parse_document(md_path)
        print(f"✓ 格式: {doc.format}")
        print(f"✓ 章节数: {len(doc.sections)}")
        
        headings = doc.get_headings()
        print(f"✓ 标题数: {len(headings)}")
        
        code_blocks = doc.get_sections_by_type(SectionType.CODE_BLOCK)
        print(f"✓ 代码块数: {len(code_blocks)}")
        
        lists = doc.get_sections_by_type(SectionType.LIST_ITEM)
        print(f"✓ 列表项数: {len(lists)}")
        
        print("\n文档大纲:")
        print(doc.get_outline())
        print()
    finally:
        Path(md_path).unlink()
    
    # 3. 测试管道
    print("3. 测试管道功能")
    print("-" * 40)
    
    pipeline = DocumentParsePipeline()
    
    formats = pipeline.get_supported_formats()
    print("✓ 支持的格式:")
    for parser_name, exts in formats.items():
        print(f"  - {parser_name}: {', '.join(exts)}")
    
    print(f"\n✓ 是否支持 .txt: {pipeline.is_supported('test.txt')}")
    print(f"✓ 是否支持 .md: {pipeline.is_supported('test.md')}")
    print(f"✓ 是否支持 .unknown: {pipeline.is_supported('test.unknown')}")
    print()
    
    # 4. 测试批量解析
    print("4. 测试批量解析")
    print("-" * 40)
    
    temp_files = []
    for i in range(3):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        f.write(f"文档{i+1}的内容")
        f.close()
        temp_files.append(f.name)
    
    try:
        docs = await pipeline.batch_parse(temp_files)
        print(f"✓ 成功解析 {len(docs)}/{len(temp_files)} 个文档")
        for i, doc in enumerate(docs):
            print(f"  - 文档{i+1}: {doc.total_chars} 字符")
        print()
    finally:
        for path in temp_files:
            Path(path).unlink()
    
    # 5. 测试转换为字典
    print("5. 测试转换为字典")
    print("-" * 40)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("测试内容")
        temp_path = f.name
    
    try:
        doc = await parse_document(temp_path)
        doc_dict = doc.to_dict()
        
        print("✓ 字典包含的键:")
        for key in doc_dict.keys():
            print(f"  - {key}")
        print()
    finally:
        Path(temp_path).unlink()
    
    print("=" * 60)
    print("✅ 所有测试通过!")
    print("=" * 60)


async def main():
    """主函数"""
    try:
        await test_basic_functionality()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
