import asyncio
import os
import re
from pathlib import Path
from notebooklm import NotebookLMClient, InfographicOrientation, InfographicStyle

async def generate_images():
    """
    Phase 4: สร้างรูปภาพสำหรับ book1
    1. สร้าง infographic จาก NotebookLM
    2. ดาวน์โหลดรูปภาพเก็บไว้ใน pic_book1/
    3. บันทึกผลลงใน pic_ture_details.md
    """
    
    notebook_id = "fc75cd1c-5f03-4563-9ddf-6027787b7021"
    book_code = "book1"
    output_dir = Path(f"book/book_{book_code}/pic_book1")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prompts จากไฟล์หนังสือ
    prompts = [
        {
            "id": 1,
            "prompt": "Informational Infographic showing the combination of Ni (Mystery) and Fe (Empathy) creating a powerful Passive Attraction aura for INFJ personality, aspect ratio 16:8, minimal style, white background. All text in the image must be in Thai.",
            "filename": f"infographic_{book_code}_1.png"
        },
        {
            "id": 2,
            "prompt": "Grid Infographic showing 3 elements of Passive Attraction for INFJ based on Art of Seduction: 1. The Ideal Lover (Fe empathy), 2. The Star (Ni mystery), 3. The Coquette (Space and boundary). Text must be entirely in Thai language, aspect ratio 16:8, minimal style, white background",
            "filename": f"infographic_{book_code}_2.png"
        }
    ]

    print(f"🚀 Starting Phase 4: Image Generation for {book_code}")

    async with await NotebookLMClient.from_storage() as client:
        for item in prompts:
            print(f"🎨 Generating Image {item['id']}: {item['filename']}...")
            try:
                # สร้าง infographic
                result = await client.artifacts.generate_infographic(
                    notebook_id,
                    instructions=item['prompt'],
                    orientation=InfographicOrientation.LANDSCAPE,
                    style=InfographicStyle.PROFESSIONAL
                )
                
                print(f"  ✓ Started generation. Task ID: {result.task_id}")
                
                # รอให้สร้างเสร็จ
                print(f"  ⏳ Waiting for completion...")
                final_status = await client.artifacts.wait_for_completion(
                    notebook_id,
                    result.task_id,
                    timeout=600,
                    poll_interval=20
                )
                
                if final_status.is_complete:
                    print(f"  ✅ Generation completed! Status: {final_status}")
                    
                    # ลองหา ID จาก metadata หรือ url
                    artifact_id = None
                    if final_status.metadata and 'artifact_id' in final_status.metadata:
                        artifact_id = final_status.metadata['artifact_id']
                    
                    # ดาวน์โหลดรูปภาพ
                    output_path = output_dir / item['filename']
                    await client.artifacts.download_infographic(
                        notebook_id, 
                        str(output_path), 
                        artifact_id=artifact_id
                    )
                    print(f"  💾 Downloaded to: {output_path}")
                else:
                    print(f"  ❌ Generation failed or timed out for {item['filename']}")
            
            except Exception as e:
                print(f"  ❌ Error: {e}")
                print(f"  ⚠️ Skipping {item['filename']} due to error. You might need to use Nanobanana.")

    print(f"🏁 Image generation process finished.")

if __name__ == "__main__":
    asyncio.run(generate_images())
