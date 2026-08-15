---
title: "Graph Engineering: ออกแบบ AI Agent ให้เป็นกราฟ (บทความ @0xwhrrari)"
type: source
tags: [graph-engineering, ai-agents, agent-architecture, workflows]
published: 2026-08-10
scraped: 2026-08-16
source_file: raw/NewsScrap/graph-engineering-whrrari.md
source_url: "https://x.com/0xwhrrari/article/2086784668003598356"
last_updated: 2026-08-16
---

## Summary

บทความของ rari (@0xwhrrari) นำเสนอ "[[GraphEngineering|graph engineering]]" — การออกแบบ AI agent ให้เป็นแผนผังการทำงาน (execution map) ที่ประกอบด้วย nodes, edges, state, routers และ gates แทนการออกแบบเป็น chain เชิงเส้น (research → write → review → ship) ผู้เขียนโต้แย้งว่าปัญหาที่แท้จริงของ agent ปัจจุบันไม่ใช่ prompt แต่เป็น "รูปทรงของงาน" (the shape of the work) — ลำดับ (sequence) หลายขั้นตอนไม่ได้เป็น dependency จริง จึงควรแตกเป็น branch ที่รันพร้อมกันแล้ว join อย่างตั้งใจ บทความให้ศัพท์ 4 รูปทรงหลัก (chain, diamond, router, controlled cycle), หลักการให้ทุก node มี contract, การวาง verifier ที่ edge, durable state สำหรับ resume, ความล้มเหลวแบบเฉพาะจุด (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP), และเช็คลิสต์ 12 ข้อก่อนปล่อยระบบ

## Key Claims

- [analysis] @0xwhrrari — การออกแบบ agent แบบเส้นตรง (ทุกขั้นตอนรอขั้นตอนก่อนหน้า) ไม่มี branch, parallelize หรือ recovery — ครึ่งหนึ่งของขั้นตอนไม่จำเป็นต้องใช้ผลลัพธ์จากขั้นก่อนหน้าเลย; ปัญหาที่แท้จริงคือ "the shape of the work" ไม่ใช่ prompt
- [analysis] @0xwhrrari — graph engineering กำหนด workflow ด้วยคำศัพท์ชัดเจน: node (หน่วยงานที่มีขอบเขต), edge (ความสัมพันธ์ที่แท้จริง), state (ข้อมูลที่คงอยู่ข้าม node), router (กฎเลือก edge ถัดไป), gate (การตรวจสอบว่าดำเนินต่อได้หรือไม่)
- [analysis] @0xwhrrari — sequence ไม่เท่ากับ dependency: คำถามแรกคือ "ขั้นตอนถัดไปอ่านผลลัพธ์ของขั้นตอนก่อนหน้าจริงหรือไม่" ถ้าไม่ ให้ตัด edge ทิ้ง — chain ที่ช้าจะกลายเป็น parallel graph ที่เร็วขึ้น
- [analysis] @0xwhrrari — ทุก node ต้องมี contract ครบ 4: one job, explicit input, structured output, clear failure state — structured output (เช่น JSON schema ของ source_researcher) ทำให้ node route/test/replace ได้ และสลับโมเดลได้โดยไม่รื้อระบบ
- [analysis] @0xwhrrari — edge คือ data contract ("A สร้างข้อมูลที่ B ได้รับอนุญาตให้ใช้") ไม่ใช่แค่ลูกศรลำดับ; งานท่อประปา (flatten, dedup, filter null, join) ควรเป็น deterministic code — "A graph where every edge is another agent is paying tokens for its own wiring."
- [analysis] @0xwhrrari — กราฟ production ส่วนใหญ่ประกอบจาก 4 รูปทรง: chain (A→B→C เมื่อ dependency จริง), diamond (fan-out อิสระแล้ว join), router (CLASSIFY → quick path / full audit), controlled cycle (WORK → VERIFY → PASS/EXIT, FAIL → FEEDBACK → WORK) — ทุก cycle ต้องมี hard stop และ convergence rule
- [analysis] @0xwhrrari — parallelism ต้อง join อย่างตั้งใจ: ใช้ Promise.allSettled เพื่อไม่ให้ branch ที่ล้มเหลวพังทั้งสาย แต่ไม่ควรวาง barrier หลังทุก node — join คุ้มเมื่อ node ถัดไปต้องการชุดข้อมูลสมบูรณ์เท่านั้น; "Parallel is not automatically fast. Your topology decides where the system waits."
- [analysis] @0xwhrrari — routing ต้องตรวจสอบได้: classifier (probabilistic) เลือก แต่เส้นทางที่อนุญาต (deterministic) เป็นผู้บังคับขอบเขต — โมเดลได้ความยืดหยุ่นโดยไม่ได้อำนาจควบคุมไม่จำกัด
- [analysis] @0xwhrrari — node ที่มีค่าที่สุดคือ verifier ที่ edge — ไม่สร้างสิ่งใหม่ แต่หยุดงานอ่อนแอไม่ให้เดินหน้า; อย่าให้ agent เดียว generate + approve + publish งานตัวเองใน context เดียว
- [analysis] @0xwhrrari — ระบบ production ต้องมี durable state (task_id, current_node, completed_nodes, artifacts, decisions, evidence, budgets, retry_counts, human_approvals) — ย้าย reference ไป artifact แทน transcript; กราฟต้องตอบได้ 3 ข้อ: เกิดอะไรขึ้นแล้ว, ทำไมเลือกเส้นทางนี้, resume ที่จุดไหน — ถ้าตอบไม่ได้ "ยังเป็นแค่ demo"
- [analysis] @0xwhrrari — cycle ต้องมีเงื่อนไขลู่เข้าที่วัดผลได้ (completion test, max rounds, token/cost budget, บันทึกความพยายามผ่าน seen-set, escalation path) — "ทำซ้ำจนกว่าจะดี" ไม่ใช่เงื่อนไขหยุด
- [analysis] @0xwhrrari — ออกแบบความล้มเหลวเฉพาะจุด: RETRY (ชั่วคราว) / FALLBACK (โมเดล/source ไม่พร้อม) / SKIP (branch optional) / REPAIR (output ไม่ผ่าน) / ESCALATE (เสี่ยงเกินเกณฑ์) / STOP (ขอบเขตงบฯ/ความปลอดภัย); checkpoint หลัง node แพง, writes idempotent, worker workspace แยกกัน, log ทุก routing decision
- [analysis] @0xwhrrari — topology คือ cost model: โมเดลถูกสำหรับงานจำกัดขอบเขต (extraction, classification, formatting), โมเดลแรงสำหรับ decomposition, synthesis และ hard verification; multi-agent research ดีกว่าแบบ breadth-first แต่ token แพงกว่ามาก — tradeoff
- [fact] OpenAI (@OpenAIDevs, 2025-10-07) — ประกาศ AgentKit ประกอบด้วย ChatKit, Agent Builder (WYSIWYG workflow builder), Guardrails, Evals — ตัวอย่างว่า agent behavior ถูกออกแบบเป็น workflow ที่ตรวจสอบได้ (ทวีต 2.9 ล้านวิว)
- [fact] Anthropic (Claude Managed Agents, 2026-04-09) — production research ระดับใหญ่: lead agent + subagents ทำงานพร้อมกัน, synthesis, และ citation gate ก่อนผลถึงผู้ใช้ (ทวีต 21 ล้านวิว)
- [analysis] @0xwhrrari — ไม่ใช่ทุกงานต้องเป็นกราฟ: ใช้ single loop เมื่องานสั้น, context พอ, ไม่มี branch อิสระ, ความล้มเหลวต้นทุนต่ำ, มนุษย์รีวิวไว; "เริ่มด้วย loop เดียว วาดกราฟเมื่อ dependency บังคับ"
- [analysis] @0xwhrrari — ลำดับชั้นวิวัฒนาการ: PROMPT → CONTEXT → HARNESS → [[AgentLoop|LOOP]] → [[GraphEngineering|GRAPH]] จับคู่กับ message, memory, machine, run, coordination — "The model is only one node. The product is the system around it."

## Key Quotes

> "A loop helps one agent improve its work. A graph coordinates many loops into one system." — @0xwhrrari

> "A graph where every edge is another agent is paying tokens for its own wiring." — @0xwhrrari

> "Parallel is not automatically fast. Your topology decides where the system waits." — @0xwhrrari

> "The model is only one node. The product is the system around it." — @0xwhrrari

> "A prompter asks the agent to do more. An architect redesigns the graph so the system can do more safely." — @0xwhrrari

## Connections

- relates to: [[AgentLoop]] — กราฟคือชั้นถัดจาก loop (coordination ของหลาย loops); ผู้เขียนมีบทความ "Loop Engineering: The AI skill every builder needs in 2026" ในรายการอ่านต่อ
- relates to: [[HarnessEngineering]] — "Harness engineering สร้างสิ่งแวดล้อมรอบตัวโมเดล" ต่างจาก graph engineering ที่ประสานงานทั้งระบบ
- relates to: verification / citation gating — ตัวอย่าง Anthropic production research ที่มี citation gate ก่อนผลถึงผู้ใช้ สอดคล้องกับหลักการวาง verifier ที่ edge
- relates to: cost control — topology กำหนด latency/cost; ตัวอย่าง SIMPLE REQUEST vs COMPLEX REQUEST graph
