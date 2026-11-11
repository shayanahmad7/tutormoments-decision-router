# Evaluator evidence audit

No scores changed. Normalization removes whitespace, Markdown emphasis and quote glyph/case differences. Explicit ellipses checked as ordered verbatim segments. Wording differences remain flagged.

The original exact-match flags, saved responses and ratings remain unchanged. The CSV lists every flagged quotation with the actual generated reply. This review checks quotation provenance, not correctness of the evaluator judgment.

primary: 26 formatting or case only, 1 wording changed or omitted, 3 explicit ellipsis with verbatim segments.
audit: 7 formatting or case only, 2 wording changed or omitted.

## Same fixed 32 cases
| Condition | Gemini passes | Claude passes |
|---|---:|---:|
| self_detailed | 20/32 | 16/32 |
| jev_directed | 19/32 | 22/32 |
| decisions_directed | 21/32 | 22/32 |
| always_scaffolding | 16/32 | 15/32 |
| always_rigor | 24/32 | 22/32 |
| teacher_directed | 26/32 | 23/32 |
| opposite_teacher | 14/32 | 14/32 |

Across the 96 independently rated replies, pass/fail agreement was 75/96 (78.1%), Cohen kappa 0.551. The 32 cases were fixed before outcomes, balanced by source category, one per student. This is a second automated evaluator, not human validation.
