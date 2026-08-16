# Overview

<!-- AUTO:STATS BEGIN -->
This wiki is a knowledge base comprising **6 source documents** (2024~2026), **7 entities**, **11 concepts**, **5 field overviews**, **1 analysis reports**, **0 associative trails**, and **0 timelines**.

Sources are automatically classified into 5 topic clusters via Leiden topology clustering: **Open-Source AI Definition(4)**, **Personal Knowledge Management & Visual Thinking(1)**, **AI Agents & Workflows(1)**, **Open Weights(1)**, **Licensing & Open-Washing(3)**. A single source may span multiple clusters (listed in every catalog where its weight is ≥0.3); for the full cluster list and members, see [[index]] or `graph/_clusters.json`.
<!-- AUTO:STATS END -->

This wiki maps the debate over what "open source" should mean for AI systems. The corpus gathers the [[OpenSourceInitiative]]'s 2024 attempt to fix a definition, the endorsement and criticism it drew, and the looser "open weights" releases that dominate the market in practice. Three groupings organize the field: the formal definition and its data dispute, the weights-only middle ground, and the licensing terms and open-washing that surround both. The strongest evidence base sits with the definition grouping, where the [[OpenSourceInitiative]] is the recurring claimant across multiple sources. The corpus has since expanded beyond the open-source debate: the AI-agents cluster reframes agent design as execution graphs, and the PKM cluster covers visual thinking and note-taking tooling.

## Recent Changes

- 2025-05-19 — A legal primer frames the open-weights middle ground against the strict definition, using [[DeepSeek]] R1 as its leading example.
- 2025-01 — [[DeepSeek]] releases R1 with MIT-licensed weights but withheld training data, the defining open-weights case.
- 2024-12-05 — Criticism of the definition's omission of open training data is rounded up, led by critics from Debian, the Software Freedom Conservancy, and OSI co-founder Bruce Perens, with the [[FreeSoftwareFoundation]] anchoring the position.
- 2024-10-28 — The [[OpenSourceInitiative]] releases the Open Source AI Definition 1.0; [[Mozilla]] endorses it the same day, and [[Meta]]'s Llama 2 is judged non-compliant.

## 1. [[open-source-ai-definition|Open-Source AI Definition]]

On 2024-10-28 the [[OpenSourceInitiative]] released the Open Source AI Definition 1.0, the first binary standard for open AI: a system either grants the four freedoms — use, study, modify, share — or it does not, and qualifying requires data information, source code, and parameters. OSI validated Pythia, OLMo, Amber, CrystalCoder, and T5, and judged Llama 2 non-compliant.

The grouping's actors split three ways. The [[OpenSourceInitiative]] is the standard-setter; [[Mozilla]] is the prominent endorser, framing openness as an AI-safety precondition; the [[FreeSoftwareFoundation]] anchors a broader critic coalition building a stricter alternative. The anchor concept is [[OpenSourceAI]], and the contested component is [[TrainingData]].

The central collision is whether a workable binary standard or a maximalist open-data requirement should define "open." OSI and [[Mozilla]] back the imperfect-but-clear definition as a workable floor — Mozilla with a stated intent to raise the data bar over time. The critics call the missing training data disqualifying now rather than a defect to refine later. The procedural fact that a 10-person board, not the full membership, approved the definition feeds the dispute.

Details: [[open-source-ai-definition|the Open-Source AI Definition field]].

## 2. [[open-weights|Open Weights]]

[[DeepSeek]]'s R1, released 2025-01 under the MIT license with public weights but a withheld training corpus, is the defining case of the weights-only middle ground. It drew attention partly on a roughly $6 million training-cost claim that made a cheap-to-adapt release commercially compelling.

The grouping centers on [[DeepSeek]] as provider and on two concepts: [[OpenWeights]], the posture of publishing parameters while keeping data secret, and [[FineTuning]], the adaptation capability that makes such a release useful. It is defined by contrast with the fuller [[OpenSourceAI]] standard rather than by a dense actor roster.

The tension is practical adaptability against genuine transparency. Publishing weights lets users fine-tune without retraining, but the withheld data and algorithms mean the model cannot be fully audited, reproduced, or inspected for bias — which is precisely the partial release the strict definition was written to exclude.

Details: [[open-weights|the Open Weights field]].

## 3. [[licensing-open-washing|Licensing & Open-Washing]]

This grouping covers the terms and rhetoric of "open" AI. [[Meta]]'s Llama, released in early 2023 under a custom community license with usage restrictions, is the reference case the [[OpenSourceInitiative]] cites as non-compliant and as the canonical example of open-washing.

Licensing is where open-source AI diverges from software: permissive families (MIT, Apache) and copyleft families (GPL) were written for code, but a model adds data and weights that no software license covers. [[ModelLicensing]] and [[OpenWashing]] are the anchor concepts; [[Meta]] is the contested issuer, with [[OpenSourceInitiative]] judging and [[Mozilla]] advocating.

The collision is whether a familiar permissive license is sufficient signal of openness or whether component completeness is the real test. [[DeepSeek]] R1's MIT-licensed-but-data-less release shows the two are independent, and as "open source" enters regulation, a soft line lets restricted models claim benefits meant for open ones.

Details: [[licensing-open-washing|the Licensing & Open-Washing field]].

## 4. [[ai-agents-workflows|AI Agents & Workflows]]

This grouping is the corpus's first out-of-domain expansion: [[GraphEngineering|graph engineering]] reframes AI agent design as an explicit execution map of nodes, edges, state, routers and gates instead of a linear chain (research → write → review → ship) that serializes steps which never consume each other's output. The argument, from @0xwhrrari's article, is that the real problem is "the shape of the work" — sequence is not dependency, so independent steps should fan out and join deliberately rather than wait in line.

The taxonomy sits on a five-layer ladder: prompt → context → [[HarnessEngineering|harness]] → [[AgentLoop|loop]] → graph, where a loop improves one agent and a graph coordinates many loops. The cost of the flexibility is token spend — topology is the cost model — so the practice demands verifiers at the edges, durable state for resume, per-node failure policies (RETRY/FALLBACK/SKIP/REPAIR/ESCALATE/STOP), hard stops on cycles, and a 12-point checklist before shipping. The author's caution applies to the wiki itself: start with a single loop and draw the graph only when dependencies force it — this cluster is currently a single source.

Details: [[ai-agents-workflows|the AI Agents & Workflows field]].

## 5. [[pkm-note-taking|Personal Knowledge Management & Visual Thinking]]

This grouping is the corpus's second out-of-domain expansion, into personal knowledge management. It centers on the thesis of Karlos's Excalidraw tutorial (39 min, ~5.45M-download plugin): visual thinking — the practice of thinking through sketches, diagrams, and knowledge maps, attributed to da Vinci and Einstein — is the key to unlocking ideas, but subscription note apps that keep drawings isolated (Notability, OneNote, Microsoft 365) waste that power. [[Excalidraw]] answers by making drawings first-class citizens of an [[Obsidian]] vault: drawings are markdown files that embed in notes in real time, link bidirectionally with notes, nest inside other drawings, and carry a "back of note card" text block in the same file.

The cluster's anchor concepts are [[VisualThinking]] (the thesis) and [[SecondBrain]] (the externalized knowledge system the drawings plug into); its entities are [[Excalidraw]] (the plugin, by Zsolt Viczian) and [[Obsidian]] (the local-first markdown host with wikilinks, embeds, and graph view). The tension axis is integration versus isolation: whether drawings live inside the knowledge graph, where they can be linked, embedded, and referenced across notes, or in standalone apps that hold them apart from everything else. This cluster is currently a single source.

Details: [[pkm-note-taking|the Personal Knowledge Management & Visual Thinking field]].

## Cross-Domain Threads

**One word, three standards.** The whole corpus is a fight over a single phrase. The definition grouping wants "open source" to mean the four freedoms plus reproducible components; the open-weights grouping uses "open" to mean runnable-and-adaptable; the licensing grouping shows how the word gets attached to releases that satisfy neither. The [[OpenSourceInitiative]]'s binary definition is the attempt to collapse these three readings into one, and the resistance to it — from the [[FreeSoftwareFoundation]] on one flank and from market practice on the other — is what keeps the field unsettled.

**Training data as the fault line.** [[TrainingData]] is the component that recurs across all three groupings. The definition grouping fights over whether it must be released, the open-weights grouping is defined by withholding it, and the licensing grouping shows that a permissive license says nothing about it. Whether "open" requires open data is therefore the single question that, once answered, would resolve most of the surrounding disputes at once.
