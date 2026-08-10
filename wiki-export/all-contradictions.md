# All CONTRADICTIONS (2)

---

---
title: "OSAID Definition vs Open Training-Data Requirement"
type: contradiction
tags: [OSAID, open-source-ai, training-data, licensing]
sources: [case-against-osaid, osi-open-source-ai-definition, mozilla-celebrates-osaid, open-source-ai-models-how-open]
last_updated: 2026-07-19
---

# OSAID Definition vs Open Training-Data Requirement

## Opposing Positions

When the [[OpenSourceInitiative]] released the Open Source AI Definition (OSAID) 1.0 on 2024-10-28, it made one choice that split the open-source community: a system can be "open source AI" without releasing its raw [[TrainingData]], provided it discloses enough "data information" to recreate a substantially equivalent system. The dispute is not about whether transparency matters but about where the line of "open" falls — and whether a definition that omits open data dilutes a term the community spent 26 years building.

**The definition camp** — the [[OpenSourceInitiative]], joined by [[Mozilla]] — holds that a clear, binary standard is more useful now than a maximalist one that almost nothing could meet. OSI argues that full-data mandates would relegate open-source AI to a niche, because some data (medical records, for example) cannot be legally shared; data information plus code plus parameters is, on this view, the workable definition that lets regulators and civil society distinguish genuine openness from [[OpenWashing]]. [[Mozilla]] endorses it as "an important step forward" while acknowledging that some disagree with aspects such as its training-data treatment and that the definition will need refinement over time.

**The open-data camp** — the [[FreeSoftwareFoundation]] and critics including OSI co-founder Bruce Perens, the Software Freedom Conservancy's Bradley Kuhn, Debian developer Sam Johnston, RedMonk's Stephen O'Grady, and OpenUK's Amanda Brock — holds that training data is effectively the source code of a model, so a system is not open unless the data and its processing scripts respect the four freedoms. On this reading the OSAID is "less than Open Source" and erodes the meaning of the term; some warn it threatens the future of "open source" itself. The FSF acknowledges narrow moral exceptions (such as personal data) but concludes these merely yield non-free applications whose use may be ethically excusable.

## Representative Evidence

- [[case-against-osaid]] — David Cassel rounds up the criticism; the [[FreeSoftwareFoundation]] holds a machine-learning application is not free unless its [[TrainingData]] and processing scripts respect the four freedoms, and Bradley Kuhn announced a campaign to run for the OSI board on a platform to repeal the OSAID.
- [[osi-open-source-ai-definition]] — the [[OpenSourceInitiative]]'s canonical statement defines openness by four freedoms plus access to data information, code, and parameters, and names combating [[OpenWashing]] as the motivation: "Companies are calling AI systems 'Open Source' even though their licenses contain restrictions."
- [[mozilla-celebrates-osaid]] — [[Mozilla]] (Ayah Bdeir, Imo Udom, Nik Marda) endorses the definition as "an important step forward" and argues a binary standard gives developers, advocates, and regulators needed precision, while acknowledging that some disagree with aspects such as the training-data treatment and that the definition will need refinement over time.
- [[open-source-ai-models-how-open]] — a Hunton legal primer notes OSI's strict standard requires data information, code, and parameters as the preferred form for modification, framing why the data question is the dividing line between full open source and lesser categories.

## Derived Tensions & Generational Readings

A procedural grievance runs alongside the substance: the OSAID was approved by OSI's 10-person board rather than a full membership vote, which critics cite as evidence the standard lacks community mandate. This turns a definitional debate into a governance one — Kuhn's board-repeal campaign is the clearest expression of the move from arguing the merits to contesting the institution.

The two camps also read the history of "open source" differently. Perens, an OSI co-founder, argues the 26-year-old Open Source Definition can simply be applied to AI, treating the OSAID as an unnecessary and weaker fork. The definition camp reads the same history as proof that new components (data, weights) demand a new, adapted standard. The disagreement is partly generational within the movement: founders defending an inherited bright line against stewards adapting it to a new technical reality.

A live qualifier on both sides is the legal-data problem. OSI's medical-AI exception is real, and the FSF concedes it; the open question is whether that exception justifies a general data-information standard or only a narrow carve-out. Until that is settled, each camp can claim the hard cases support its position.

## Interpretive Direction

In the short term, the practical consequence is two coexisting standards rather than one: the OSAID as the de facto reference, and a stricter open-data criterion under development by the [[FreeSoftwareFoundation]]. On the narrow question of adoption, the OSAID has the momentum — at least 20 endorsing organizations and a validated-model list — but on the question of legitimacy, the board-vote grievance and the repeal campaign leave it contested. The open-data releases the critics point to — Pleias's dataset, Ai2's LLMs, AMD's "fully open" 1B models — weaken the "open data is unworkable" defense without settling whether it should be mandatory, since none is tied to a validated model. The point to monitor was the OSI board election that Bradley Kuhn announced in 2024-12 he would contest; as of 2026-07-19 this corpus records no outcome, so the repeal platform's fate is unresolved rather than decided. If it gains ground there, the definition itself, not just its reception, is back in play.


---

---
title: "Residual Fragmentary Issues"
type: contradiction
tags: [residual, open-source-ai]
sources: [open-source-ai-models-how-open]
last_updated: 2026-06-26
---

# Residual Fragmentary Issues

## Opposing Positions

This page is the residual-absorption bucket for source-to-source contradictions that do not converge onto a single axis of contention. Unlike a true theme, it has no one opposition structure; it groups leftover claims by character so they remain visible without being forced into an axis they do not belong to.

At present the corpus is small and its only registered contradiction maps cleanly onto a dedicated theme, so this bucket holds no claims. The grouping is kept in place — as the standing convention requires — so that future fragmentary oppositions (one-off factual disputes, time-shifted updates, or single-actor issues that lack a counterpart) have a home the moment they appear.

## Representative Evidence

No claims are currently assigned to this bucket, so there is no representative evidence to present. The single contradiction extracted from the corpus is analysed under its own theme rather than here. For background on how the surrounding debate is framed, the open-weights legal primer [[open-source-ai-models-how-open]] sets the technical context against which future fragmentary disputes would be read.

## Derived Tensions & Generational Readings

Because nothing has converged here, there is no derived tension to trace. The reason this bucket is empty rather than absent is structural: the corpus contains exactly one source-to-source contradiction, and that contradiction is a clear, single-axis dispute over whether open-source AI must include open training data — strong enough to stand as its own theme rather than be diluted into a residual pile.

## Interpretive Direction

The follow-up plan is simply to monitor ingestion. As new sources enter the wiki, any contradiction that is genuinely one-off — a fact check, a timeline correction, or an isolated single-actor claim with no opposing camp — should be absorbed here rather than spun into a thin standalone theme. Should a cluster of related fragments accumulate around a shared axis, the convention is to promote them out of this bucket into a named theme at that point, not before.

