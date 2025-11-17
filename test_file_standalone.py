"""
纯粹测试文档解析模块（不依赖其他模块）
"""

import asyncio
import tempfile
from pathlib import Path

# 直接导入模块文件
import sys
sys.path.insert(0, '/Users/kaiiangs/Desktop/another-me/ame/foundation/file')

from base import DocumentFormat, SectionType, ParsedDocument, DocumentSection
from text_parser import TextParser
from markdown_parser import MarkdownParser
from pipeline import DocumentParsePipeline


async def test_text_parser():
    """测试文本解析器"""
    print("=" * 60)
    print("测试文本解析器")
    print("=" * 60)
    
    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("第一段内容\n\n第二段内容\n\n第三段内容")
        txt_path = f.name
    
    try:
        parser = TextParser()
        doc = await parser.parse(txt_path)
        
        print(f"✓ 格式: {doc.format}")
        print(f"✓ 文件路径: {doc.file_path}")
        print(f"✓ 字符数: {doc.total_chars}")
        print(f"✓ 词数: {doc.total_words}")
        print(f"✓ 章节数: {len(doc.sections)}")
        print(f"✓ 段落数: {len(doc.get_paragraphs())}")
        
        for i, section in enumerate(doc.sections, 1):
            print(f"\n段落 {i}:")
            print(f"  类型: {section.type}")
            print(f"  内容: {section.content}")
        
        print("\n✅ 文本解析测试通过!\n")
    
    finally:
        Path(txt_path).unlink()


async def test_markdown_parser():
    """测试Markdown解析器"""
    print("=" * 60)
    print("测试Markdown解析器")
    print("=" * 60)
    
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
        parser = MarkdownParser()
        doc = await parser.parse(md_path)
        
        print(f"✓ 格式: {doc.format}")
        print(f"✓ 章节数: {len(doc.sections)}")
        
        headings = doc.get_headings()
        print(f"✓ 标题数: {len(headings)}")
        
        code_blocks = doc.get_sections_by_type(SectionType.CODE_BLOCK)
        print(f"✓ 代码块数: {len(code_blocks)}")
        
        lists = doc.get_sections_by_type(SectionType.LIST_ITEM)
        print(f"✓ 列表项数: {len(lists)}")
        
        print("\n文档大纲:")
        outline = doc.get_outline()
        print(outline)
        
        print("\n标题详情:")
        for h in headings:
            print(f"  {h.level}级标题: {h.content}")
        
        print("\n✅ Markdown解析测试通过!\n")
    
    finally:
        Path(md_path).unlink()


async def test_pipeline():
    """测试解析管道"""
    print("=" * 60)
    print("测试解析管道")
    print("=" * 60)
    
    pipeline = DocumentParsePipeline()
    
    # 查看支持的格式
    formats = pipeline.get_supported_formats()
    print("\n支持的格式:")
    for parser_name, exts in formats.items():
        print(f"  {parser_name}: {', '.join(exts)}")
    
    # 测试文件类型检查
    print(f"\n✓ 是否支持 test.txt: {pipeline.is_supported('test.txt')}")
    print(f"✓ 是否支持 test.md: {pipeline.is_supported('test.md')}")
    print(f"✓ 是否支持 test.pdf: {pipeline.is_supported('test.pdf')}")
    print(f"✓ 是否支持 test.unknown: {pipeline.is_supported('test.unknown')}")
    
    # 测试自动选择解析器
    print("\n测试自动选择解析器:")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("TXT 文件内容")
        txt_path = f.name
    
    try:
        doc = await pipeline.parse(txt_path)
        print(f"  ✓ TXT 文件自动识别: {doc.format}")
    finally:
        Path(txt_path).unlink()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# Markdown 标题")
        md_path = f.name
    
    try:
        doc = await pipeline.parse(md_path)
        print(f"  ✓ MD 文件自动识别: {doc.format}")
    finally:
        Path(md_path).unlink()
    
    print("\n✅ 管道测试通过!\n")


async def test_batch_parse():
    """测试批量解析"""
    print("=" * 60)
    print("测试批量解析")
    print("=" * 60)
    
    pipeline = DocumentParsePipeline()
    
    # 创建多个临时文件
    temp_files = []
    for i in range(3):
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
        f.write(f"文档{i+1}的内容\n\n这是第{i+1}个文档。")
        f.close()
        temp_files.append(f.name)
    
    try:
        docs = await pipeline.batch_parse(temp_files)
        print(f"\n✓ 成功解析 {len(docs)}/{len(temp_files)} 个文档")
        
        for i, doc in enumerate(docs, 1):
            print(f"\n文档 {i}:")
            print(f"  字符数: {doc.total_chars}")
            print(f"  章节数: {len(doc.sections)}")
        
        print("\n✅ 批量解析测试通过!\n")
    
    finally:
        for path in temp_files:
            Path(path).unlink()


async def test_document_to_dict():
    """测试文档转换为字典"""
    print("=" * 60)
    print("测试文档转换为字典")
    print("=" * 60)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# 标题\n\n段落内容")
        md_path = f.name
    
    try:
        pipeline = DocumentParsePipeline()
        doc = await pipeline.parse(md_path)
        
        doc_dict = doc.to_dict()
        
        print("\n字典包含的键:")
        for key in doc_dict.keys():
            print(f"  - {key}")
        
        print(f"\n✓ 格式: {doc_dict['format']}")
        print(f"✓ 字符数: {doc_dict['total_chars']}")
        print(f"✓ 章节数: {len(doc_dict['sections'])}")
        
        print("\n✅ 转换为字典测试通过!\n")
    
    finally:
        Path(md_path).unlink()


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("文档解析模块完整测试")
    print("=" * 60 + "\n")
    
    try:
        await test_text_parser()
        await test_markdown_parser()
        await test_pipeline()
        await test_batch_parse()
        await test_document_to_dict()
        
        print("=" * 60)
        print("🎉 所有测试全部通过!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
