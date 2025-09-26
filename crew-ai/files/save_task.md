[C] CONTEXT
Two prior artifacts are available in context:

1) OUTLINE JSON
   {
     "main_idx": <int>,
     "subtopics": [ { "name": <string>, "idxs": [<int> ... up to 5] } ... up to 5 ],
     "items": [
       { "idx": <int>, "url": <string>, "title": <string|null>, "score": <number|null>, "content": <string> },
       ...
     ]
   }

2) EDITED WRITER JSON
   {
     "subtopic_editorials": [ { "name": <string>, "editorial": <string>, "content": <string>, "sources": ["<url>", ... 2–4] }, ... ],
     "main_editorial": { "title": <string>, "editorial": <string>, "content": <string>, "sources": ["<url>", ... 2–4] }
   }

You also have access to a single tool:
- save_json(path: string, payload: object) → confirmation string

You must assemble the final newsletter payload (including the **Main Topic**) and save it.

[O] OBJECTIVE
Deterministically merge OUTLINE + EDITED WRITER into a single JSON that:
- Builds the **Main Editorial** (title/editorial/sources) using EDITED WRITER, with strict fallbacks informed by OUTLINE.main_idx and OUTLINE.items.
- Builds each **Subtopic** with its final editorial and mapped articles (title/url/content excerpts).
- Matches the exact target schema in [R].
- Saves via save_json to "{output_path}".

[S] STEPS (DETAILED, DETERMINISTIC)
1) Validate OUTLINE integrity
   - Ensure OUTLINE.main_idx refers to an item in OUTLINE.items.
   - Ensure every OUTLINE.items[i] has a unique integer idx and a valid http(s) url.
   - For each OUTLINE.subtopics[k].idxs: keep only idx values that exist in OUTLINE.items (preserve order; cap at 5).

2) Assemble the **Main Topic** (Main Editorial)
   2.1 Identify main_item := the object in OUTLINE.items with idx == OUTLINE.main_idx.
   2.2 Title resolution (deterministic):
       - If EDITED.main_editorial.title is a non-empty string → use it.
       - Else if main_item.title is a non-empty string → use it.
       - Else derive from main_item.url:
         • Take domain and first path segment; Title Case; strip query/fragment; truncate to ≤60 chars.
   2.3 Editorial body:
       - Use EDITED.main_editorial.editorial verbatim (no rewriting).
   2.4 Sources list (2–4 urls total):
       - Start with EDITED.main_editorial.sources in order, removing duplicates while preserving first occurrence.
       - Ensure main_item.url is included. If absent and total would exceed 4, drop the last URL to make room for main_item.url.
       - Keep only valid http(s) URLs. Cap at 4.
   2.5 Produce the main_editorial object:
       {
         "title": <resolved title>,
         "editorial": <edited main editorial verbatim>,
         "content": <include main_item.content>,
         "sources": [<include main_item.url>]
       }

3) Build subtopics with articles
   For each OUTLINE.subtopics entry (preserve order):
   3.1 name := subtopic.name as-is.
   3.2 articles := map each idx in subtopic.idxs to its OUTLINE.items entry (ignore missing after validation).
       For each mapped item emit:
         {
           "title": item.title if non-empty else null,
           "editorial": <edited subtopic editorial verbatim>,
           "url": item.url,
           "articles": [
              { "title": "<title|null>", "url": "<url>", "content": "<excerpt or body>" }
              // up to 4 more
            ]
         }
   3.3 Deduplicate articles by URL within the subtopic (keep first), cap at 5.
   3.4 Editorial text:
       - Find the matching EDITED.subtopic_editorials entry by exact name.
       - Use its editorial verbatim (no rewriting). If no match, use "".
   3.5 Construct subtopic object:
       { "name": name, "editorial": <verbatim or "">, "articles": [ ... up to 5 ... ] }

   Excerpt rule (deterministic and safe):
   - excerpt(text) := first 1200 characters, trimmed at the last whitespace ≤1200; strip leading/trailing whitespace.
   - If text is empty or null, use "".

4) Assemble final object strictly per [R]
   - Keys and order exactly as specified.
   - No extra fields.
   - Subtopics in the same order as OUTLINE.subtopics.

5) Persist and stop
   - Call save_json once with:
     - path = "{output_path}"
     - payload = <the final object>
   - Return only the confirmation string from save_json and stop.

[T] TONE / CONSTRAINTS
- Deterministic rules only; no heuristics beyond those stated.
- Do not modify any edited prose; use edited text verbatim.
- No external data; no hallucinations.
- Maintain ordering constraints; enforce caps (sources ≤4; articles/subtopic ≤5).

[A] AUDIENCE
Automation and editors consuming a machine-stable JSON for downstream publishing.

[R] RESPONSE FORMAT (STRICT FINAL JSON TO PRODUCE & SAVE)
{
  "main_editorial": {
    "title": "<main title resolved in Step 2.2>",
    "editorial": "<edited main editorial verbatim>",
    "content": <include main_item.content>,
    "sources": ["<url>"]            // MUST include main_item.url
  },
  "subtopics": [
    {
      "name": "<subtopic>",
      "editorial": "<edited subtopic editorial verbatim or empty string>",
      "articles": [
        { "title": "<title|null>", "url": "<url>", "content": "<excerpt or body>" }
        // up to 4 more
      ]
    }
    // up to 4 more subtopics
  ]
}

[T] TOOL USE & TERMINATION
- Invoke only: save_json(path="{output_path}", payload=<final object>).
- Call save_json exactly once.
- After returning the confirmation string, stop.
