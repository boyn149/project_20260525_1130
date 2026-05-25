import asyncio
import re
from pathlib import Path
from notebooklm import NotebookLMClient

async def write_book2():
    """
    Phase 2: เขียนเนื้อหาหนังสือ book2
    - จัดการ sources (ลบ layer เล่มอื่น, เพิ่ม layer book2)
    - เขียนตามลำดับ: preface -> con-1-1-1 -> con-1-1-2 -> reference -> bio -> contact
    - ใช้ conversation_id ใหม่ทุกบท
    """
    
    notebook_id = "fc75cd1c-5f03-4563-9ddf-6027787b7021"
    book_code = "book2"
    book_name = "ปรากฏการณ์กำแพงน้ำแข็ง_เจาะลึกกลไก_Door_Slam_ของ_INFJ"
    output_file = Path(f"book/book_{book_code}/book_{book_code}_{book_name}.md")
    
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
        
        # ลบ layer เก่าออกทั้งหมดก่อน (เพื่อป้องกันชื่อซ้ำหรือข้อมูลปนกัน)
        for src in sources:
            if src.title.startswith("layer") and src.title.endswith(".md"):
                print(f"  - Removing old layer source: {src.title}")
                await client.sources.delete(notebook_id, src.id)

        # เพิ่ม layer ของ book2 เข้าไปใหม่
        for i in range(1, 5):
            layer_path = Path(f"book/book_{book_code}/layer{i}.md")
            if layer_path.exists():
                print(f"  + Adding source: {layer_path}")
                await client.sources.add_file(notebook_id, layer_path)

        # 2. เริ่มการเขียน
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"# {book_name}\n\n")

        conversation_id = None
        
        for i, item in enumerate(prompts):
            print(f"💬 Step {i+1}/{len(prompts)}: {item['desc']} ({item['cmd']})")
            
            if item['cmd'].startswith("con-1-1-1"):
                conversation_id = None
                print("  (Starting new conversation for Chapter 1)")

            result = await client.chat.ask(
                notebook_id, 
                item['cmd'], 
                conversation_id=conversation_id
            )
            
            conversation_id = result.conversation_id
            clean_answer = re.sub(r'\[\d+(?:[\s,-]+\d+)*\]', '', result.answer)
            
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(clean_answer)
                f.write("\n\n")
            
            print(f"✅ Step {i+1} completed and saved.")

    print(f"🎉 Writing of {book_code} completed! Output: {output_file}")

if __name__ == "__main__":
    asyncio.run(write_book2())
