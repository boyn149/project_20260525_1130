import asyncio
import re
from pathlib import Path
from notebooklm import NotebookLMClient

async def generate_layers():
    """
    Phase 1: สร้าง Layer 1-4 ของทุกเล่ม
    - ใช้ conversation_id เดียวกันตลอด Phase
    - ลำดับ: Layer 1 (ทุกเล่ม) -> Layer 2 (ทุกเล่ม) -> Layer 3 (ทุกเล่ม) -> Layer 4 (ทุกเล่ม)
    - Prompt: "layer{n} {book_code} ไม่ใช้สำนวน esther และใช้ชื่อหนังสือตามใน details.md"
    """
    
    notebook_id = "fc75cd1c-5f03-4563-9ddf-6027787b7021"
    book_codes = ["book1", "book2"]
    layers = [1, 2, 3, 4]
    conversation_id = None

    print(f"🚀 Starting Phase 1: Generating Layers 1-4 for {book_codes}")

    async with await NotebookLMClient.from_storage() as client:
        for layer_num in layers:
            print(f"--- Processing Layer {layer_num} ---")
            for book_code in book_codes:
                # สร้าง folder สำหรับหนังสือแต่ละเล่ม
                book_dir = Path(f"book/book_{book_code}")
                book_dir.mkdir(parents=True, exist_ok=True)
                
                # เตรียม prompt
                prompt = f"layer{layer_num} {book_code} ไม่ใช้สำนวน esther และใช้ชื่อหนังสือตามใน details.md"
                print(f"💬 Asking for {book_code} Layer {layer_num}...")
                
                # ส่ง prompt
                result = await client.chat.ask(
                    notebook_id, 
                    prompt, 
                    conversation_id=conversation_id
                )
                
                # เก็บ conversation_id เพื่อใช้ต่อเนื่อง
                conversation_id = result.conversation_id
                
                # ทำความสะอาดข้อมูล (ตัด citation)
                clean_answer = re.sub(r'\[\d+(?:[\s,-]+\d+)*\]', '', result.answer)
                
                # บันทึกไฟล์
                file_path = book_dir / f"layer{layer_num}.md"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_answer)
                
                print(f"✅ Saved: {file_path}")

    print(f"🎉 Phase 1 completed! Conversation ID: {conversation_id}")

if __name__ == "__main__":
    asyncio.run(generate_layers())
