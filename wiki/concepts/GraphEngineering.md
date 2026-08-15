---
title: "Graph Engineering"
type: concept
description: "Graph engineering designs AI agents as explicit execution maps (nodes/edges/state/routers/gates) instead of a single model loop; sequence is not dependency, topology is the cost model, the model is only one node."
tags: [graph-engineering, ai-agents, workflows, agent-architecture]
sources: [graph-engineering-whrrari]
last_updated: 2026-08-16
---

## Overview

Graph engineering คือการเปลี่ยนขั้นตอนการทำงานของ AI agent ให้เป็นแผนผังการทำงานที่ชัดเจน (explicit execution map) แทนการซ่อนการตัดสินใจทั้งหมดไว้ใน model loop เดียว — ระบบถูกกำหนดเป็น nodes และ edges โดย node คือหน่วยงานที่มีขอบเขตชัดเจน (agent, tool call, deterministic function, verifier หรือ human approval) และ edge คือความสัมพันธ์ที่แท้จริงระหว่าง node (สิ่งที่ได้รับอนุญาตให้รันต่อ และข้อมูลที่ข้ามผ่านได้) แนวคิดหลักจาก @0xwhrrari: ลำดับ (sequence) ไม่เท่ากับ dependency — ถ้า node ถัดไปไม่ได้อ่านผลลัพธ์ของ node ก่อนหน้า ต้องตัด edge ทิ้ง; รูปทรง (topology) ของกราฟคือโมเดลต้นทุนของระบบ; "The model is only one node. The product is the system around it." Graph engineering คือชั้นสุดท้ายของลำดับวิวัฒนาการ prompt → context → [[HarnessEngineering|harness]] → [[AgentLoop|loop]] → graph

## Connections
- [[AgentLoop]] — loop ทำให้ agent หนึ่งตัวดีขึ้น; graph ประสานหลาย loops เป็นระบบเดียว
- [[HarnessEngineering]] — harness สร้างสิ่งแวดล้อมรอบตัวโมเดล; graph วางโครงสร้าง coordination เหนือสิ่งแวดล้อมนั้น
