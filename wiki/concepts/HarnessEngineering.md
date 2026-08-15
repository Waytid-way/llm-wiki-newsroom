---
title: "Harness Engineering"
type: concept
description: "Harness engineering builds the environment/machine around the model — the layer where tools, files, and world interaction happen; sits between context and loop in the prompt→context→harness→loop→graph ladder."
tags: [ai-agents, workflows, agent-architecture]
sources: [graph-engineering-whrrari]
last_updated: 2026-08-16
---

## Overview

Harness engineering คือการสร้างสิ่งแวดล้อมรอบตัวโมเดล (the machine that surrounds the model) — ตัวกลางที่โมเดลใช้เรียก tools, อ่านไฟล์, และโต้ตอบกับโลกภายนอก ตามลำดับชั้นห้าชั้นของ @0xwhrrari: prompt engineering ปรับปรุงคำสั่ง (message), context engineering ควบคุมสิ่งที่โมเดลมองเห็น (memory), harness engineering สร้างสิ่งแวดล้อม (machine), [[AgentLoop|loop engineering]] ทำให้หน่วยงานดีขึ้นผ่าน feedback (run) และ [[GraphEngineering|graph engineering]] ประสานงานทั้งหมด (coordination) ตัวอย่าง harness เชิง production เช่น Claude Managed Agents ของ Anthropic ที่จับคู่ "agent harness ที่ปรับแต่งเพื่อประสิทธิภาพ" กับโครงสร้างพื้นฐาน production เพื่อให้ไปจาก prototype สู่การเปิดตัวได้ภายในไม่กี่วัน

## Connections
- [[GraphEngineering]] — กราฟวางโครงสร้าง coordination เหนือสิ่งแวดล้อมของ harness
- [[AgentLoop]] — loop คือ run ที่ทำงานภายใน harness
