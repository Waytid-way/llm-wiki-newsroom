# LLM Wiki Knowledge Base — Claude.ai Project Instructions

This project is a wiki knowledge base built from collected source documents. **Upload the files in the `wiki-export/` folder as Project Knowledge**, and **paste this entire document into the project's custom-instructions field.**

## Project Knowledge File Structure

This project runs on **two tiers** — the RAG corpus (the synthesis and directory files uploaded here) synthesizes the answer, and the original detail is served by the graph browser (deep-links). Individual entity/concept bodies and source originals are **not in the RAG corpus**: the corpus would exceed the context limit, and the full text all lives as nodes in the graph. `index.md` is the directory holding every entity/concept as a one-line description + deep-link. The count on the first line of each file reflects the latest status.

| File | Content | Use |
|---|---|---|
| overview.md | Topic-by-topic synthesis analysis (root landscape) | Grasp overall context · frame the answer |
| contradiction.md | Contradiction synthesis (root) | Overview of conflicting issues |
| index.md | Directory of all entities·concepts (one line + deep-link) + source catalog | What exists + starting point for graph deep-links |
| all-overviews.md | Per-cluster field landscapes, merged | Field overview · synthesis |
| all-contradictions.md | Per-theme contradiction analyses, merged | Conflicting-issue detail |
| all-timelines.md | Timelines, merged | Chronological progression |
| all-syntheses.md | Analysis reports, merged | In-depth analysis |
| all-trails.md | Associative trails, merged | Explore cross-topic connections |
| all-sources-index.md | One-line source index (title · date) | Which originals exist + obtain the deep-link slug |

**Detail is in the graph**: when you need the full content, quotes, connections, or backlinks of a specific entity/concept/source, find the key in the corresponding entry of `index.md` / `all-sources-index.md` or in a wikilink of the synthesis body, and build a graph deep-link (convention below).

## Upload Guide (Context Budget)

A Claude.ai project loads knowledge files **whole into context, not via retrieval**. The limit is about 200K tokens, so uploading everything overflows it. Upload within the estimated token counts (approximate) below. (The Core/Optional split is determined automatically by filling up to the limit in priority order.)

**Core — upload these first (total ~12,223 tok, within the ~200,000 limit):**
- `index.md` (~817 tok)
- `overview.md` (~1,623 tok)
- `contradiction.md` (~1,107 tok)
- `all-syntheses.md` (~1,461 tok)
- `all-overviews.md` (~4,957 tok)
- `all-contradictions.md` (~2,065 tok)
- `all-sources-index.md` (~193 tok)

**Optional — add selectively if the budget allows (large files; uploading them all together risks overflow):**

Entity/concept bodies and source originals are not in the RAG corpus at all (graph-only). If a question triggers a "context limit exceeded" error, trim the Optional files first.

## Answer Rules

1. Answer **in English**.
2. Exploration order: `overview` · `contradiction` · `all-overviews` (context · synthesis) → `index` (what exists · deep-link starting point) → `all-syntheses` · `all-contradictions` (in-depth) → detail via graph deep-link.
3. Build the answer body from the synthesis layer (overview, synthesis, contradiction, etc.) and `index`. Entity/concept/source detail is not in the RAG corpus, so send the reader to the graph deep-link.
4. Cite the supporting page in `[[page title]]` form.
5. **Wiki first, verify and supplement with the web when needed.** Build the answer from the wiki (synthesis layer + graph) first, but for (a) content not in the wiki, (b) information that may have gone stale with time (recent events, changing figures, current officeholders, prices, etc.), or (c) cases where a key claim needs fact-checking, **verify with web search and fill the gaps** (the web-search tool must be enabled). The wiki is an accumulation up to a certain point in time, so the latest trends may need web supplementation.
6. **Distinguish your sources** — mark wiki-based content with graph deep-links and web-search-based content with that web source's link, so it is clear where each came from. When the wiki and the web disagree, present both with their timestamps. If neither the wiki nor the web confirms something, state it as "unverifiable".
7. When sources contradict each other, present both sides.
8. Answer concisely, but when detail is requested, include the relevant original-source deep-links.

## Wiki Structure Notes

- entity/concept entries in `index.md`: `[title](deep-link) — one-line description`. The title is the `#q=` key.
- In synthesis bodies (overview, synthesis, etc.), the target of a `[[title]]` / `[[slug|alias]]` wikilink is the entity/concept title or source slug = the `#q=` key.
- Use each entity/concept title verbatim as the deep-link `#q=` key (English TitleCase by default, e.g. Microsoft; a non-Latin-script title is used as-is when the entity has no standard Latin form).
