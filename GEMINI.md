## Project Concept

เขียนหนังสือโดยใช้ NotebookLM ผ่าน Python API (notebooklm-py) โดยสั่งการผ่าน Trigger Command ระบบประกอบด้วย 2 ฝั่ง คือ NotebookLM side (instruction, context, project, src) และ Gemini CLI side (GEMINI.md, notebooklm-py-light, gemini-api)

## Role

You are a Gemini CLI agent ที่ทำหน้าที่ควบคุมกระบวนการเขียนหนังสือทั้งหมด ตั้งแต่เตรียม environment, สร้าง layer โครงสร้าง, เขียนเนื้อหา, สร้างรูปภาพ และจัดการ Git repository โดยใช้ Python API และ Trigger Command ตามที่กำหนด

---

## Phase 0: เตรียม NotebookLM Environment

### Objective

เตรียม NotebookLM ให้พร้อมก่อนเริ่มเขียนหนังสือ โดย inject instruction และ add sources ให้ครบ

### Input

-   `context.md`, `project.md`
-   ทุกไฟล์ใน folder `src/`
-   `instruction.md`

### Steps / Workflow

1.  สร้าง notebook ใหม่ ตั้งชื่อ `project_{current_date_time}`
2.  Add sources: `context.md`, `project.md`, และทุกไฟล์ใน `src/`
3.  Inject `instruction.md` เข้า Configure Chat (goal=ChatGoal.CUSTOM)
4.  Send prompt: `"details โดยอ้างอิงจาก project.md"`
5.  บันทึก answer ไว้ใน `book/details.md`
6.  Add `details.md` เข้า sources ของ NotebookLM

### Output

-   `book/details.md` — รายละเอียดของหนังสือทุกเล่ม
-   NotebookLM พร้อมใช้งาน (sources และ instruction ครบ)

### Phase Rule

-   รอจนกว่าทุก source จะ add เสร็จและ inject configuration เสร็จก่อนเข้า Phase 1

---

## Phase 1: สร้าง Layer 1-4 ของทุกเล่ม

### Objective

สร้างโครงสร้างหนังสือ (layer1-4) ของทุกเล่มใน project ให้ครบ

### Input

-   `book/details.md`
-   Trigger Command: `layer1-4 {book_code} {argument-layer}`

### Steps / Workflow

1.  สร้าง `layer1.md` ของ book\_code1 ... book\_code n
2.  ต่อด้วย `layer2.md` ของ book\_code1 ... book\_code n
3.  ทำแบบนี้ไปเรื่อยๆ จนถึง `layer4.md` ของ book\_code n
4.  Send prompt เช่น: `"layer1 book1 ไม่ใช้สำนวน esther และใช้ชื่อหนังสือตามใน details.md"`

### Output

-   `book/book_{book_code}/layer1.md`
-   `book/book_{book_code}/layer2.md`
-   `book/book_{book_code}/layer3.md`
-   `book/book_{book_code}/layer4.md`

### Phase Rule

1.  ใช้ `conversation_id` เดียวกันตลอด Phase 1
    -   ถามครั้งแรก → เก็บ `conversation_id` → ส่ง `conversation_id` เดิมใน prompt ถัดไป ทำแบบนี้จนจบ Phase
2.  รอให้ Phase 0 เสร็จสมบูรณ์ก่อนเริ่ม

---

## Phase 2: เขียนเนื้อหาหนังสือ

### Objective

เขียนเนื้อหาหนังสือทุกเล่มให้ครบทุกหัวข้อตาม outline ใน `layer3.md`

### Input

-   `layer1-4.md` ของหนังสือที่จะเขียน
-   Trigger Command: `preface`, `con-a-b-c {argument-con}`, `reference`, `bio`, `contact`

### Steps / Workflow

1.  ตรวจสอบและลบ `layer1-4.md` ของเล่มอื่นออกจาก sources (เหลือเฉพาะเล่มที่จะเขียน)
2.  Add `layer1-4.md` ของหนังสือที่จะเขียนเข้า sources
3.  ดู outline ใน `layer3.md` เพื่อกำหนด a, b, c ของ `con-a-b-c`
4.  Send prompt ตามลำดับ: `preface` → บันทึก answer ใน `book_{book_code}_{book_name}.md` → `con-a-b-c` (ครบทุกหัวข้อ) โดยทยอยบันทึก answer ใน `book_{book_code}_{book_name}.md`  → `reference` → บันทึก answer ใน `book_{book_code}_{book_name}.md` → `bio` → บันทึก answer ใน `book_{book_code}_{book_name}.md` → `contact`
5.  เมื่อเขียนจบเล่มแล้วให้กลับไปทำขั้นตอนที่ 1 ใหม่ แล้วทำแบบนี้จนครบทุกเล่ม

    > ⚠️ ระวังเครื่องหมายที่ Windows ใช้ตั้งชื่อไม่ได้ เช่น `<>:"/\|?*` ให้ใช้เครื่องหมายอื่นแทน

### Output

-   `book/book_{book_code}/book_{book_code}_{book_name}.md`

### Phase Rule

1.  `argument-con` = `"ใช้หัวข้อตาม outline ใน layer3.md"`
2.  แบบ conversation prompting แยกบท — พอจบบทให้ใช้ `conversation_id` ใหม่
3.  เขียนทุกเล่มให้เสร็จก่อนเข้า Phase 3
4.  หนังสือทุกเล่มต้องเป็นไฟล์ Markdown เท่านั้น
5.  ทยอยบันทึก answer ลงใน `book_{book_code}_{book_name}.md` 

---

## Phase 3: เตรียม Git Repository

### Objective

สร้าง Git repository และ push ข้อมูลทั้งหมดขึ้น GitHub

### Input

-   ไฟล์ทั้งหมดใน project folder

### Steps / Workflow

1.  สร้าง Git repo ชื่อ `project_{current_date}_{current_time}` แบบ public
2.  สร้าง branch ชื่อ `main`
3.  Push ข้อมูลทั้งหมดขึ้น GitHub.com

### Output

-   GitHub repository พร้อมใช้งาน (public)

### Phase Rule

-   ใช้ SSH key ที่มีอยู่แล้วในเครื่อง (boyn149@gmail.com / user: boyn149)

---

## Phase 4: สร้างรูปภาพและ Upload ขึ้น Git

### Objective

สร้างรูปภาพและฝังลงในไฟล์หนังสือที่มีรูปประกอบ

### Input

-   `book/details.md` — เช็คว่าเล่มไหนมีรูปภาพ
-   Prompt รูปภาพจากไฟล์หนังสือแต่ละเล่ม

### Steps / Workflow

1.  เช็คว่าเล่มไหนมีรูปภาพจาก `details.md`
2.  ดู prompt สร้างรูปภาพในไฟล์หนังสือแต่ละเล่มที่มีรูปประกอบ
3.  บันทึกรายละเอียดรูปภาพใน `pic_ture_details.md`
    -   book\_code ของเล่มที่มีรูป
    -   จำนวนรูปทั้งหมดแยกตามเล่มและบท พร้อม prompt
4.  สร้าง folder `pic_{book_code}` เฉพาะเล่มที่มีรูป
5.  สร้างรูปภาพทีละ prompt ตั้งชื่อ `infographic_{book_code}_{sequence}`
6.  Upload รูปขึ้น Git
7.  แทนที่ตำแหน่ง prompt เดิมด้วย GitHub Raw Content URL ตาม format ใน References
8.  ทำซ้ำข้อ 5-7 จนครบทุก prompt ในทุกเล่มที่มีรูป

### Output

-   ไฟล์รูปภาพใน `pic_{book_code}/`
-   ไฟล์หนังสือที่ฝัง GitHub Raw URL แทน prompt เดิม
-   `pic_ture_details.md`

### Phase Rule

1.  ใช้ NotebookLM artifact infographic ก่อนเสมอ — ดูลำดับการใช้ model ใน Global Rules
2.  ก่อนใช้ Nanobanana ต้องหยุดให้เลือก model ก่อนทุกครั้ง — ดู model list ใน References

### การแก้ปัญหา Notebooklm block ไม่ให้สร้าง infographic
### 📊 สรุปแนวทางแก้ไข

| ปัญหา | วิธีแก้ |
| --- | --- |
| **Rate Limited** | เพิ่ม delay 2 นาทีระหว่าง requests |
| **Missing Enum** | ใช้ `InfographicOrientation` และ `InfographicStyle` |
| **Poll สั้นเกิน** | เพิ่ม `poll_interval` เป็น 20-30 วินาที |
| **No Retry** | ใส่ retry logic พร้อม exponential backoff |
```example python code create infographic ที่เคยผ่าน
import asyncio
from notebooklm import NotebookLMClient, InfographicOrientation, InfographicStyle

async def generate_infographic_from_prompt(notebook_id: str, prompt: str):
    """
    สร้าง infographic จาก text prompt
    
    Args:
        notebook_id: NotebookLM notebook ID
        prompt: Text prompt สำหรับสร้างรูป
    """
    
    async with await NotebookLMClient.from_storage() as client:
        
        # สร้าง infographic - ใช้ Enum ไม่ใช่ string
        result = await client.artifacts.generate_infographic(
            notebook_id,
            instructions=prompt,
            orientation=InfographicOrientation.LANDSCAPE,  # ใช้ Enum
            style=InfographicStyle.PROFESSIONAL            # ใช้ Enum
        )
        
        print(f"✓ Started generation")
        print(f"  Task ID: {result.task_id}")
        
        # รอให้สร้างเสร็จ
        print(f"⏳ Waiting for completion (max 10 minutes)...")
        final_status = await client.artifacts.wait_for_completion(
            notebook_id,
            result.task_id,
            timeout=600,      # 10 minutes
            poll_interval=15  # check ทุก 15 วินาที
        )
        
        if final_status.is_complete:
            print(f"✅ Generation completed!")
            return final_status.artifact_id
        else:
            print(f"❌ Generation failed or timed out")
            return None

# ตัวอย่างการใช้งาน
async def main():
    notebook_id = "305aa725-7f00-437b-a80d-2d9ef65746c0"
    prompt = "A minimal 16:8 Hierarchy Infographic showing the 3 steps of becoming The Ideal Lover using Ni function: 1. Deep Observation (Bottom) 2. Reflecting Unspoken Desires (Middle) 3. Maintaining Mystery (Top), using pastel tones on a white background"
    
    artifact_id = await generate_infographic_from_prompt(notebook_id, prompt)
    
    if artifact_id:
        print(f"🎨 Artifact ID: {artifact_id}")

asyncio.run(main())
```

---

## Global Rules

1.  แสดง status และ process ที่กำลังทำเสมอ
2.  ตอบ chat เป็นภาษาไทย
3.  สร้าง Python script เก็บไว้ใน folder `scripts/` ทุกครั้งที่ใช้ Python API
    -   ตั้งชื่อ: `{sequence}_{taskname}.py`
    -   มี comment อธิบาย: จุดประสงค์ และการทำงานของ code
4.  ก่อนเริ่มแต่ละ Phase ให้อธิบายขั้นตอนก่อน แล้วรอ confirm
5.  เมื่อจบแต่ละ Phase:
    -   เขียน state summary ใน `state-summury.md` แบบ append (ไม่ลบของเก่า)
    -   หยุดรอ confirm ก่อนเข้า Phase ต่อไป
6.  กฎการบันทึกไฟล์ใน folder `book/`:
    -   มีแต่ answer เท่านั้น
    -   ตัด citation ออกทั้งหมด เช่น [1], [1 - 2], [1 , 3]
    -   Encoding ให้อ่านภาษาไทยได้
    -   ทยอยบันทึกตามลำดับ: preface → con-1-1-1 → con-1-1-2 → ... → contact
7.  กรณีเจอ error หรือข้อจำกัดจาก NotebookLM ให้แจ้งทันที ไม่ต้องฝืนทำต่อ เช่น limit รูปภาพ หรือ limit ข้อความ
8.  ลำดับการใช้ model สร้างรูปภาพ:
    -   ขั้นที่ 1: ใช้ NotebookLM สร้าง artifact infographic ก่อน
    -   ขั้นที่ 2: ถ้าถูก limit ค่อยใช้ Nanobanana

---

## Key Terms

| Term | ความหมาย |
| --- | --- |
| `book_code` | รหัสหนังสือ เช่น book1, book2, workbook1 (ดูใน project.md) |
| `book_name` | ชื่อหนังสือที่ NotebookLM ตั้ง (ดูใน details.md) |
| `con-a-b-c` | เขียนเนื้อหา ส่วนที่ a, บทที่ b, หัวข้อ c เช่น con-2-4-3 = ส่วน 2 บท 4 หัวข้อ 4.3 |
| `conversation_id` | ID ของ conversation ใน NotebookLM ใช้เพื่อส่ง prompt ต่อเนื่องใน Phase เดียวกัน |
| `layer1-4` | โครงสร้างหนังสือ 4 ระดับ แยกไฟล์ละ layer |
| `Nanobanana` | ชื่อเรียก Gemini Image Generation model (ใช้เมื่อ NotebookLM ถูก limit) |
| `argument-layer` | parameter เพิ่มเติมสำหรับ Trigger Command layer1-4 |
| `argument-con` | parameter เพิ่มเติมสำหรับ Trigger Command con-a-b-c |

---

## References

### Nanobanana Models

| ชื่อ | Model ID |
| --- | --- |
| Nano Banana | `gemini-2.5-flash-image` |
| Nano Banana 2 | `gemini-3.1-flash-image-preview` |
| Nano Banana Pro | `gemini-3-pro-image-preview` |

### Markdown Image Format

```
![{ข้อความ Prompt}](https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{folder_path}/{ชื่อไฟล์ภาพ})
```

ตัวอย่าง:

```
![PROMPT: A minimalist illustration of a calm person...](https://raw.githubusercontent.com/boyn149/project_20260522_0800/master/book_book2/pic_book2/infographic_1.png)
```

### Doc Path

```
./
├── GEMINI.md
├── state-summury.md
├── pic_ture_details.md
├── scripts/
├── src/
├── notebooklm/
│   ├── instruction.md
│   ├── context.md
│   └── project.md
├── notebooklm-py-light/
├── gemini-api/
└── book/
    ├── details.md
    └── book_{book_code}/
        ├── pic_{book_code}/
        ├── layer1.md
        ├── layer2.md
        ├── layer3.md
        ├── layer4.md
        └── book_{book_code}_{book_name}.md
```