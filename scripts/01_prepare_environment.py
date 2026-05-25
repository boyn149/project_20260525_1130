import asyncio
import os
from datetime import datetime
from pathlib import Path
from notebooklm import NotebookLMClient, ChatGoal

async def prepare_environment():
    """
    Phase 0: เตรียม NotebookLM Environment
    1. สร้าง notebook ใหม่
    2. Add sources: context.md, project.md และทุกไฟล์ใน src/
    3. Inject instruction.md เข้า Configure Chat
    4. Send prompt "details โดยอ้างอิงจาก project.md"
    5. บันทึก answer ไว้ใน book/details.md
    6. Add details.md เข้า sources
    """
    
    # กำหนดชื่อ notebook
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    notebook_title = f"project_{current_time}"
    
    print(f"🚀 Starting Phase 0: Preparing Environment")
    print(f"Creating notebook: {notebook_title}")

    async with await NotebookLMClient.from_storage() as client:
        # 1. สร้าง notebook ใหม่
        nb = await client.notebooks.create(notebook_title)
        nb_id = nb.id
        print(f"✅ Notebook created: {nb_id}")

        # 2. Add sources: context.md, project.md
        print("📤 Uploading context.md and project.md...")
        context_path = Path("notebooklm/context.md")
        project_path = Path("notebooklm/project.md")
        
        if context_path.exists():
            await client.sources.add_file(nb_id, context_path)
            print(f"  - Added {context_path}")
        
        if project_path.exists():
            await client.sources.add_file(nb_id, project_path)
            print(f"  - Added {project_path}")

        # Add ทุกไฟล์ใน src/
        print("📤 Uploading files from src/...")
        src_dir = Path("src")
        for file_path in src_dir.iterdir():
            if file_path.is_file():
                try:
                    await client.sources.add_file(nb_id, file_path)
                    print(f"  - Added {file_path}")
                except Exception as e:
                    print(f"  ❌ Error adding {file_path}: {e}")

        # 3. Inject instruction.md เข้า Configure Chat
        print("⚙️ Injecting instruction.md...")
        instruction_path = Path("notebooklm/instruction.md")
        if instruction_path.exists():
            with open(instruction_path, "r", encoding="utf-8") as f:
                instruction_content = f.read()
            
            await client.chat.configure(
                nb_id,
                goal=ChatGoal.CUSTOM,
                custom_prompt=instruction_content
            )
            print("✅ Instruction injected")
        else:
            print("⚠️ instruction.md not found, skipping configuration")

        # 4. Send prompt: "details โดยอ้างอิงจาก project.md"
        print("💬 Requesting details from NotebookLM...")
        prompt = "details โดยอ้างอิงจาก project.md"
        result = await client.chat.ask(nb_id, prompt)
        
        # 5. บันทึก answer ไว้ใน book/details.md
        # ตรวจสอบและลบ citation [1], [1-2], etc. ตาม Global Rules
        import re
        clean_answer = re.sub(r'\[\d+(?:[\s,-]+\d+)*\]', '', result.answer)
        
        book_dir = Path("book")
        book_dir.mkdir(exist_ok=True)
        details_path = book_dir / "details.md"
        
        with open(details_path, "w", encoding="utf-8") as f:
            f.write(clean_answer)
        
        print(f"✅ Details saved to {details_path}")

        # 6. Add details.md เข้า sources
        print(f"📤 Adding {details_path} back to sources...")
        await client.sources.add_file(nb_id, details_path)
        print("✅ Phase 0 completed successfully!")

if __name__ == "__main__":
    asyncio.run(prepare_environment())
