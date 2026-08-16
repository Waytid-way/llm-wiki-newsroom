---
title: "Do Human Thought Tools and AI Agent Harnesses Share Structure?"
type: synthesis
tags: [visual-thinking, second-brain, excalidraw, obsidian, pkm, graph-engineering, ai-agents, agent-architecture]
sources: [excalidraw-visual-thinking-karlos, graph-engineering-whrrari]
last_updated: 2026-08-16
---

# Do Human Thought Tools and AI Agent Harnesses Share Structure?

## Summary

ใช่ ในชั้นโครงสร้าง: ทั้งสองแนวทางย้าย "การคิด" ออกจากตัวคิด (สมองมนุษย์ / โมเดล) ไปไว้ในสิ่งประดิษฐ์ถาวรที่ประกอบกลับ จัดการ และตรวจสอบได้ — วิดีโอ Excalidraw ของ Karlos วางสมองที่สองไว้ที่ vault ที่ภาพวาดเป็นไฟล์ (ฝัง/ลิงก์สองทาง/ซ้อนกันได้) [[excalidraw-visual-thinking-karlos]] ส่วน graph engineering ของ rari (@0xwhrrari) วาง harness ไว้รอบโมเดล (nodes, edges, state, routers, gates) [[graph-engineering-whrrari]] ความตึงของคำตอบ: ระบบมนุษย์เน้นเสรีภาพเชิงพื้นที่และความหมายอิสระ ส่วนระบบ AI เน้นความตรวจสอบได้ (contract, verifier, gate) — คล้ายกันเป็นโครงสร้าง แต่ไม่ใช่กลไกเดียวกัน

## 1. สิ่งแวดล้อมรอบตัวคิด

ฝั่ง AI: harness engineering คือ "การสร้างสิ่งแวดล้อมรอบตัวโมเดล" — ชั้นที่สามในลำดับวิวัฒนาการ prompt → context → harness → loop → graph ตามบทความของ @0xwhrrari [[graph-engineering-whrrari]] ฝั่งมนุษย์: Obsidian vault คือสิ่งแวดล้อมรอบความคิด — "vault ก็คือโฟลเดอร์ปกติที่มีไฟล์ข้อความอยู่ข้างใน" ตามที่ Karlos เน้นย้ำ พร้อม wikilinks, embeds และ Graph View ที่เห็นเครือข่ายความรู้ [[excalidraw-visual-thinking-karlos]] (ประโยค "สิ่งแวดล้อมรอบความคิดมนุษย์" เป็นชั้นวิเคราะห์ของสังเคราะห์นี้ — แหล่งอ้างอิงทั้งสองพูดถึงสิ่งแวดล้อมของฝั่งตัวเองเท่านั้น)

## 2. Externalization ของความทรงจำ

ทั้งสองฝั่งย้ายความทรงจำออกจากตัวคิดไปไว้ใน artifact ที่ resume ได้ ฝั่ง agent: durable state (สถานะถาวรของงานที่ continue ต่อได้) ที่บันทึก task_id, current_node, completed_nodes, artifacts, decisions, budgets — กราฟต้องตอบได้ว่าเกิดอะไรขึ้นแล้ว ทำไมเลือกเส้นทางนี้ และ resume ที่จุดไหน [[graph-engineering-whrrari]] ฝั่งมนุษย์: แพตเทิร์น "back of note card" — ไฟล์ .excalidraw คือไฟล์ .md ที่มีโค้ดวาด + ข้อความสรุปในไฟล์เดียว (วาดหน้า เขียนหลัง) [[excalidraw-visual-thinking-karlos]] ความขนานคือการออกแบบ: ความทรงจำไม่ได้อยู่ในหัว/ในน้ำหนักโมเดล แต่อยู่ในไฟล์ที่เปิดแล้ว "คิดต่อ" ได้ จุดต่างสำคัญ (วิเคราะห์): durable state ของ agent ถูกออกแบบให้ machine-readable เพื่อ routing/checkpoint ส่วน back of note card ถูกออกแบบให้ human-readable เพื่อการทบทวน — เป้าหมายร่วมคือการไม่เริ่มต้นใหม่จากศูนย์

## 3. โครงสร้างการประกอบ: กราฟ กับ การซ้อน

ฝั่ง agent: งานถูกประกอบเป็น nodes/edges ด้วยรูปทรง 4 แบบ — chain, diamond (fan-out แล้ว join), router (classify → เส้นทาง), controlled cycle (work → verify → feedback) — และ parallelism ต้อง join อย่างตั้งใจ [[graph-engineering-whrrari]] ฝั่งมนุษย์: การฝังกระดานซ้อนกระดาน (nesting drawings) — นำกระดานย่อยมาฝังในกระดานใหญ่ แก้ย่อยแล้วใหญ่อัปเดตตาม ช่วยย่อยไอเดียใหญ่เป็นชิ้นเล็กแล้วรวมเป็นภาพใหญ่; Group Link ฝังเฉพาะพื้นที่ของกระดานลงในโน้ต [[excalidraw-visual-thinking-karlos]] ความขนานเชิงโครงสร้าง: ทั้งคู่มีองค์ประกอบย่อยที่ประกอบเป็นระบบใหญ่ได้ ต่างกันตรงที่ agent ใช้กฎตายตัว (routing, gates, verifiers) ควบคุมการประกอบ ส่วนระบบมนุษย์ปล่อยให้ลากวางอิสระตามพื้นที่ (spatial freedom)

## 4. จุดต่างที่ชี้ขาด: contract กับ เสรีภาพ

ฝั่ง agent ต้องการ contract ทุก node (one job, explicit input, structured output, clear failure state) และ verifier ที่ edge เพื่อหยุดงานอ่อนแอไม่ให้เดินหน้า — ระบบตรวจสอบได้เพราะจำกัดรูปทรงและบังคับโครงสร้างข้อมูล [[graph-engineering-whrrari]] ฝั่งมนุษย์ของ Karlos ไม่มี contract เลย: "เห็นภาพทุกอย่าง วาดอะไรก็ได้ เอาไปใส่ในโน้ต และทุกอย่างเชื่อมกันหมด" [[excalidraw-visual-thinking-karlos]] — นี่คือ tradeoff ไม่ใช่ข้อบกพร่องฝ่ายเดียว: ระบบ agent ยืดหยุ่นน้อยกว่าแต่เชื่อถือได้ในงาน production; ระบบมนุษย์ยืดหยุ่นสุดขั้วแต่ไม่มีใครรับประกันว่าลิงก์ไหน "ถูกต้อง" — เกณฑ์ความถูกต้องของมนุษย์คือการมองเห็น (visual comprehension) ไม่ใช่การตรวจสอบเชิงกลไก

## 5. คำเตือนเรื่องการเปรียบเทียบ

การเปรียบเทียบนี้เป็น structural analogy (ทั้งคู่ externalize ความคิด + ประกอบจากส่วนย่อย) ไม่ใช่ functional equivalence — สูตรลวงเช่น "second brain คือ durable state ของมนุษย์" ฟังดูจับใจแต่ข้ามความต่างที่ชี้ขาด: state ของ agent ถูกออกแบบให้ machine-readable และมี failure policy (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP) [[graph-engineering-whrrari]] ส่วนโน้ตมนุษย์ไม่มี semantics ของการล้มเหลว — ลิงก์ "พัง" ก็แค่ไม่มีความหมาย ไม่มี escalation path [[excalidraw-visual-thinking-karlos]] ข้อสรุปที่ปลอดภัย: นำหลักการของฝั่งหนึ่งไปยืมอีกฝั่งต้องผ่านการแปล — เช่น นำ "verifier ที่ edge" มาคิดเป็น "ลิงก์ review ท้ายโน้ตสำคัญ" ได้ แต่จะอ้างว่าเป็นกลไกเดียวกันไม่ได้

## Connections

- **Cluster overviews** — [[ai-agents-workflows|AI Agents & Workflows]] · [[pkm-note-taking|Personal Knowledge Management & Visual Thinking]]
- **Concepts** — [[GraphEngineering]] · [[AgentLoop]] · [[HarnessEngineering]] · [[VisualThinking]] · [[SecondBrain]]
- **Entities** — [[Excalidraw]] · [[Obsidian]]
- **Sources** — [[graph-engineering-whrrari|Graph Engineering (rari)]] · [[excalidraw-visual-thinking-karlos|วิดีโอ Excalidraw ของ Karlos]]