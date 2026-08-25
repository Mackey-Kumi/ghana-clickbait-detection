# Annotation Codebook

Used identically by: Claude's AI pre-labeling pass, the primary annotator's
verification pass (`annotate/verify.py`), and the second annotator's blind
labeling of `data/processed/second_annotator_subset.csv`.

## Labels

- **Clickbait** — the headline uses deliberate curiosity gaps, emotional
  manipulation, vague references, excessive capitalisation, or false urgency to
  generate clicks rather than inform.
- **Informative** — the headline communicates the substance of the story clearly
  and without manufactured emotional hooks.
- **Ambiguous** — doesn't cleanly fit either label. Set aside and excluded from
  model training; kept in the dataset to measure annotation difficulty.

## Ghana-specific clickbait signals

- **Excessive capitalisation** — "FINALLY", "EXPOSED", "SHOCKING", "JUST IN"
- **Vague celebrity references** — "popular Ghanaian actress", "prominent
  businessman", "well-known pastor"
- **Curiosity gap phrasing** — "what happened next will surprise you", "see what
  she said"
- **False urgency markers** — "BREAKING", "JUST IN", "DEVELOPING"
- **Emotional bait** — "breaks down in tears", "fights back", "storms out"
- **Incomplete enumeration** — "5 things Ghanaians do that...", "the real reason
  why..."

## Deciding

A headline showing one or more of the signals above, where the signal is doing
the work of generating curiosity rather than conveying information, is
Clickbait. A headline that names names, states the actual news, or would let a
reader accurately summarize the story from the headline alone is Informative —
even if it covers a dramatic or emotional topic. When a headline is genuinely
hard to place (e.g. it names the story but also uses one mild curiosity-gap
phrase), mark it Ambiguous rather than guessing.
