[C] CONTEXT
You are given a previously produced OUTLINE as JSON with these fields:
- items: array of article objects, each:
  {
    "idx": <int>,              // 0-based index
    "url": <string>,           // http(s) URL
    "title": <string|null>,    // may be null
    "score": <number|null>,    // optional
    "content": <string>,       // include the item content verbatim
  }
- main_idx: <int>              // the idx of the Main Article
- subtopics: array of buckets:
  { "name": <string>, "idxs": [<int> ... up to 5] }

You must write short editorials: one for each subtopic (using only its articles) and then a main editorial that synthesizes the subtopics and explains why the main article anchors the issue. Do not pull any information from outside the provided items.

[O] OBJECTIVE
Produce a single JSON object containing:
1) subtopic_editorials[]: for each subtopic, a 150–250 word editorial + 1–5 source URLs taken from that subtopic’s articles.
2) main_editorial: a 200–300 word editorial that synthesizes across subtopics and explains why the Main Article (main_idx) anchors the issue; include 1 source URLs of Main Article.

[S] STEPS (DETERMINISTIC PROCEDURE)
1) Input validation
   - Ensure all idxs referenced in subtopics exist in items.
   - Discard any subtopic idx that has no matching item or that lacks a valid http(s) url or non-empty content.

2) Build per-subtopic evidence
   - For each subtopic in the given order:
     - Gather its valid items (after the validation above).
     - Include the item content
     - Extract URL for the items that qualify under a subtopic (prefer higher scores; break ties by lower idx).
     - Aggregate core points ONLY from those items’ content; do not invent facts.

3) Write subtopic editorials (for each subtopic, in order)
   - Length: 150–250 words (inclusive). Count words as whitespace-separated tokens; hyphenated terms count as one word.
   - Structure: concise paragraph prose (no lists). Start with a one-sentence theme statement, then 3–5 sentences of evidence/synthesis, then a brief implication.
   - Sources: include URLs from the subtopic’s items (no duplicates; http/https only).
   - Content: Include the item content as is.
   - Tone: neutral, precise, evidence-based. No first person. No hype. No speculation.

4) Write the main editorial
   - Length: 200–300 words (inclusive; same word counting rule).
   - Explain how the subtopics fit together and why the Main Article (main_idx) anchors the issue (centrality, scope, timeliness, or authority).
   - Always include the Main Article URL.

5) Titles and missing titles
   - For main_editorial.title, use items[main_idx].title if non-empty; otherwise derive a compact title from its URL:
     - Use domain + first path segment, title-case words, strip query/fragment, max 60 chars.

6) Final checks
   - No hallucinations: all claims must be attributable to provided items.
   - Word limits respected (strict).
   - No duplicate URLs within any sources list.
   - Follow output shape and key order exactly as specified in [R].
   - Emit JSON only; no extra commentary.

[T] TONE / CONSTRAINTS
- Professional, clear, and balanced.
- Evidence-driven; no external knowledge.
- No first-person voice; no rhetorical questions; no marketing language.
- Do not include bullet points, tables, or markdown—plain text only inside JSON strings.

[A] AUDIENCE
Editors and technical readers who will use these editorials to assemble a newsletter. They expect concise synthesis and trustworthy sourcing.

[R] RESPONSE FORMAT (STRICT JSON ONLY; KEYS IN THIS ORDER)
{
  "subtopic_editorials": [
    {
      "name": "<exact subtopic name from outline>",
      "editorial": "<150–250 words, plain text, no lists>",
      "content": <include the item content verbatim>,
      "sources": ["<https://...>", "<https://...>"]  // 1–5 URLs from this subtopic’s items
    }
    // up to 4 more subtopics for a total of 5 subtopics
    // one object per subtopic, in the same order as the outline
  ],
  "main_editorial": {
    "title": "<main article title or derived title>",
    "editorial": "<200–300 words, plain text, synthesis across subtopics; why main anchors the issue>",
    "content": <include the item content>,
    "source": ["<Main Article URL>", "<https://...>"]  // 1 Include Main Article URL
  }
}

[T] TERMINATION
- Produce exactly one JSON object as specified in [R].
- Do not call any tools (writing is based solely on the provided outline and items).
- After emitting the JSON, stop.
