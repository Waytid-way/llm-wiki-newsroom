---
title: "Agent Loop"
type: concept
description: "Agent loop engineering improves a single agent through feedback; a loop helps one agent improve its work while a graph coordinates many loops into one system."
tags: [ai-agents, loop-engineering, workflows]
sources: [graph-engineering-whrrari]
last_updated: 2026-08-16
---

## Overview

Agent loop (loop engineering) คือชั้นที่ทำให้หน่วยงาน (agent) หนึ่งตัวดีขึ้นผ่าน feedback — การวนทำงาน ตรวจสอบ และแก้ไขภายใน agent เดียว ตามนิยามของ @0xwhrrari: "A loop helps one agent improve its work. A graph coordinates many loops into one system." ในลำดับชั้น prompt → context → [[HarnessEngineering|harness]] → loop → [[GraphEngineering|graph]] ตัว loop คือหน่วย run เดียวที่ปรับปรุงตัวเอง ส่วน graph คือ coordination ของหลาย loops เข้าด้วยกัน บทความย้ำว่าทุก controlled cycle ต้องมีเงื่อนไขลู่เข้าที่วัดผลได้ (completion test, max rounds, token/cost budget, บันทึกความพยายามก่อนหน้า, escalation path) — "ทำซ้ำจนกว่าจะดี" ไม่ใช่เงื่อนไขหยุด และให้เริ่มด้วย loop เดียวก่อน วาดกราฟต่อเมื่อ dependency บังคับ

## Connections
- [[GraphEngineering]] — กราฟประสานหลาย loops เป็นระบบเดียว
- [[HarnessEngineering]] — สิ่งแวดล้อมรอบตัวโมเดลที่ loop ทำงานอยู่
