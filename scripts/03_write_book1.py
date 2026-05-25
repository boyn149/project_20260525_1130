import asyncio
import re
from pathlib import Path
from notebooklm import NotebookLMClient

async def write_book1():
    """
    Phase 2: เขียนเนื้อหาหนังสือ book1
    - จัดการ sources (ลบ layer เล่มอื่น, เพิ่ม layer book1)
    - เขียนตามลำดับ: preface -> con-1-1-1 -> con-1-1-2 -> reference -> bio -> contact
    - ใช้ conversation_id ใหม่ทุกบท (ในเล่มนี้มี 1 บทหลัก ดังนั้นจะเปลี่ยน id เมื่อเริ่มบท หรือหัวข้อใหญ่)
    """
    
    notebook_id = "fc75cd1c-5f03-4563-9ddf-6027787b7021"
    book_code = "book1"
    book_name = "เสน่ห์เงียบฉบับ_INFJ_ดึงดูดคนที่ใช่ด้วยหัวใจที่เป็นตัวเอง"
    output_file = Path(f"book/book_{book_code}/book_{book_code}_{book_name}.md")
    
    # คำสั่งที่จะส่งตามลำดับ
    prompts = [
        {"cmd": "preface", "desc": "เขียนคำนำ"},
        {"cmd": "con-1-1-1 ใช้หัวข้อตาม outline ใน layer3.md", "desc": "เขียนเนื้อหาบทที่ 1 หัวข้อ 1.1"},
        {"cmd": "con-1-1-2 ใช้หัวข้อตาม outline ใน layer3.md", "desc": "เขียนเนื้อหาบทที่ 1 หัวข้อ 1.2"},
        {"cmd": "reference", "desc": "เขียนเอกสารอ้างอิง"},
        {"cmd": "bio", "desc": "เขียนประวัติผู้เขียน"},
        {"cmd": "contact", "desc": "เขียนข้อมูลการติดต่อ"}
    ]

    print(f"🚀 Starting Phase 2: Writing {book_code} - {book_name}")

    async with await NotebookLMClient.from_storage() as client:
        # 1. จัดการ Sources
        print("🧹 Managing sources...")
        sources = await client.sources.list(notebook_id)
        
        # ลบ layer ของเล่มอื่น (book2)
        for src in sources:
            if "book_book2" in src.title or "layer" in src.title and "book2" in src.title:
                print(f"  - Removing source: {src.title}")
                await client.sources.delete(notebook_id, src.id)

        # ตรวจสอบและเพิ่ม layer ของ book1
        current_source_titles = [src.title for src in await client.sources.list(notebook_id)]
        for i in range(1, 5):
            layer_path = Path(f"book/book_{book_code}/layer{i}.md")
            if layer_path.exists() and layer_path.name not in current_source_titles:
                print(f"  + Adding source: {layer_path}")
                await client.sources.add_file(notebook_id, layer_path)

        # 2. เริ่มการเขียน
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {book_name}\n\n")

        conversation_id = None
        
        for i, item in enumerate(prompts):
            print(f"💬 Step {i+1}/{len(prompts)}: {item['desc']} ({item['cmd']})")
            
            # กฎ: แบบ conversation prompting แยกบท - ในที่นี้จะขอเปลี่ยน id เมื่อเริ่ม con- ครั้งแรก
            if item['cmd'].startswith("con-1-1-1"):
                conversation_id = None # เริ่มบทใหม่
                print("  (Starting new conversation for Chapter 1)")

            result = await client.chat.ask(
                notebook_id, 
                item['cmd'], 
                conversation_id=conversation_id
            )
            
            conversation_id = result.conversation_id
            
            # ทำความสะอาดข้อมูล
            clean_answer = re.sub(r'\[\d+(?:[\s,-]+\d+)*\]', '', result.answer)
            
            # บันทึกเนื้อหา (Append)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(clean_answer)
                f.write("\n\n")
            
            print(f"✅ Step {i+1} completed and saved.")

    print(f"🎉 Writing of {book_code} completed! Output: {output_file}")

if __name__ == "__main__":
    asyncio.run(write_book1())
