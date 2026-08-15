---
title: "AI Agents & Workflows"
type: overview
tags: []
cluster: ai-agents-workflows
sources: []
last_updated: 2026-08-16
---

# AI Agents & Workflows

## Overview

[[GraphEngineering|Graph engineering]] คือการออกแบบ AI agent ให้เป็นแผนผังการทำงาน (execution map) ที่ชัดเจนแทนการยัดทุกอย่างลงใน model loop เดียว — ระบบถูกนิยามเป็น nodes, edges, state, routers และ gates โดยให้ลำดับ (sequence) ที่ไม่ใช่ dependency จริงแตกเป็น branch ที่รันพร้อมกันแล้ว join อย่างตั้งใจ แนวคิดนี้มาจากบทความของ rari (@0xwhrrari) ซึ่งเป็น source แรก (และแหล่งเดียวในตอนนี้) ของ cluster นี้ คำสำคัญของกราฟ: ทุก node ต้องมี contract ครบ (one job, explicit input, structured output, clear failure state), edge คือ data contract ไม่ใช่แค่ลูกศรลำดับ, วาง verifier ที่ edge เพื่อหยุดงานอ่อนแอ, และ topology คือโมเดลต้นทุนของระบบ — โมเดลถูกสำหรับงานจำกัดขอบเขต โมเดลแรงสำหรับ decomposition/synthesis/การตรวจสอบที่ยาก

แนวคิดนี้อยู่ในลำดับชั้นวิวัฒนาการ prompt → context → [[HarnessEngineering|harness]] → [[AgentLoop|loop]] → graph: loop ทำให้ agent หนึ่งตัวดีขึ้นผ่าน feedback ส่วน graph ประสานหลาย loops เป็นระบบเดียว ("A loop helps one agent improve its work. A graph coordinates many loops into one system.") หลักการของบทความยังเตือนไม่ให้เปลี่ยนทุก prompt ให้เป็นไดอะแกรม — ให้เริ่มด้วย loop เดียว แล้ววาดกราฟต่อเมื่อ dependency บังคับ

แกนความตึง (tension axis) ของ cluster นี้คือ **flexibility vs. controllability** — กราฟให้ความยืดหยุ่น (parallelism, specialization, recovery) แต่ต้องแลกกับต้นทุน (token มากขึ้น) และต้องถูกควบคุมด้วย deterministic routing, gates, hard stops และเช็คลิสต์ 12 ข้อก่อนปล่อยระบบ

## Recent Changes

- 2026-08-10 — บทความ "Graph Engineering" ของ rari (@0xwhrrari) เผยแพร่บน X (1.4 ล้านวิว)
- 2026-08-16 — สรุปภาษาไทยถูก ingest เข้าสู่ wiki พร้อม concept hubs 3 ตัว (GraphEngineering, AgentLoop, HarnessEngineering)

## Key Entities & Concepts

**Concepts** (3) — [[GraphEngineering]] เป็นแกนหลักของ cluster (การออกแบบ agent เป็นกราฟ), [[AgentLoop]] คือชั้นที่ทำให้ agent เดียวดีขึ้นผ่าน feedback, และ [[HarnessEngineering]] คือสิ่งแวดล้อมรอบตัวโมเดลที่ loops และ graph ทำงานอยู่

**Entities** (0) — ยังไม่มี entity page; บุคคลที่เกี่ยวข้องคือผู้เขียนบทความ rari (@0xwhrrari) ซึ่งยังไม่ถึงเกณฑ์การสร้าง stub

## Subtopics

**การออกแบบกราฟ** — ศัพท์พื้นฐาน: node (หน่วยงานที่มีขอบเขต), edge (ความสัมพันธ์), state (ข้อมูลคงอยู่ข้าม node), router (กฎเลือกเส้นทาง), gate (การตรวจสอบ) และรูปทรงหลัก 4 แบบ: chain, diamond (fan-out แล้ว join), router (classify → path), controlled cycle (work → verify → feedback) ที่ต้องมี hard stop และ convergence rule

**ความน่าเชื่อถือและต้นทุน** — verifier ที่ edge หยุดงานอ่อนแอ; durable state ทำให้ resume ได้หลัง crash; ความล้มเหลวออกแบบเฉพาะจุด (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP); topology กำหนด latency และ cost — "Parallel is not automatically fast. Your topology decides where the system waits."

## Key Trends & Figures

- **จาก chain สู่ graph** — แนวโน้มหลัก: พฤติกรรม agent ถูกออกแบบเป็น workflow ที่ตรวจสอบได้มากขึ้น (เช่น OpenAI Agent Builder แบบ WYSIWYG, ประกาศ 2025-10-07) แทน chain ของ prompt ที่ซ่อนอยู่
- **Production research scale** — Claude Managed Agents (public beta, 2026-04-09) แสดงรูปแบบ lead agent + subagents ทำงานพร้อมกัน + citation gate ก่อนผลถึงผู้ใช้ (ทวีต 21 ล้านวิว)
- **Tradeoff ที่วัดได้** — Anthropic รายงาน multi-agent research ดีกว่า single agent ในงาน breadth-first แต่ใช้ token มากกว่ามาก; topology กำหนดทั้ง latency และ cost
- **ตัวเลขจากบทความ** — บทความต้นทางมียอดดู 1.4 ล้านวิว (เผยแพร่ 2026-08-10); ทวีต OpenAI AgentKit 2.9 ล้านวิว

## Adjacent Domains & Scope

- [[open-source-ai-definition|Open-Source AI Definition]] — cluster เดิมของ wiki ที่ว่าด้วยมาตรฐาน open-source AI; ไม่มีความเชื่อมโยงเชิงเนื้อหากับ graph engineering ในตอนนี้
- [[open-weights|Open Weights]] — cluster ว่าด้วยการเผยแพร่ weights ของโมเดล; ต่าง domain กันโดยสิ้นเชิง

<!-- AUTO:MEMBERS BEGIN -->
## Key Members (auto-extracted, top 15 by intra-cluster connectivity)

**Entities** (0)
- _none_

**Concepts** (3)
- [[AgentLoop]]
- [[GraphEngineering]]
- [[HarnessEngineering]]
<!-- AUTO:MEMBERS END -->

<!-- AUTO:SOURCES BEGIN -->
## Sources

1 total — see [AI Agents & Workflows catalog](../sources/_catalog-ai-agents-workflows.md).

Top 1 by weight:
- [[graph-engineering-whrrari]] _(w=1.00)_
<!-- AUTO:SOURCES END -->
