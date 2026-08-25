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
- **Vague hype descriptors** — "huge", "plush", "stunning", "dazzling", "fine
  figure", "adorable" used with no verifiable detail attached (no number, name,
  location, brand) — the entire content is "impressive thing exists, go look"

## Deciding

A headline showing one or more of the signals above, where the signal is doing
the work of generating curiosity rather than conveying information, is
Clickbait. A headline that names names, states the actual news, or would let a
reader accurately summarize the story from the headline alone is Informative —
even if it covers a dramatic or emotional topic. When a headline is genuinely
hard to place (e.g. it names the story but also uses one mild curiosity-gap
phrase), mark it Ambiguous rather than guessing.

## A quote is not automatically informative

A headline built around a quote can look complete — the words really were
said, nothing is fabricated — while still functioning as bait, because a
quote by itself is decontextualized. Reading it doesn't tell you what
actually happened; you still have to click through to find out. A quote does
not earn Informative just for being real and fully-formed.

**The test: does the framing around the quote add a fact you couldn't get
from the quote alone** — a named institution, a concrete action, a
consequence, a specific topic — or does it only tell you *who is speaking* or
*that this is emotionally intense* (a label like "reveals", "shares her
story", "opens up") without adding anything else?

- **Informative**: "'I apologise' – Dr Yamson admits MTN Ghana was late to
  condemn xenophobic attacks." The quote alone says nothing. The attribution
  adds a real fact you didn't have before: a named executive, at a named
  company, apologizing for a specific, describable failure. You now
  understand the actual event, not just that someone said something.
- **Clickbait**: "My Manager Wanted To Rape Me – Ruby Of Date Rush." The
  attribution tells you *who* is speaking (a named reality-TV personality)
  but adds no fact about the allegation itself — no report filed, no named
  accused, no outcome. You know exactly as much about what happened as the
  raw quote gave you; the name is there to identify the personality for
  clickability, not to anchor the story.
- **Clickbait**: "I was drugged and made to sleep with 30 men every day –
  16-year-old trafficked girl shares sad story." "Shares sad story" doesn't
  add a fact either — it just re-labels the quote you already read as an
  emotional teaser, functionally identical to "reveals what she did." No
  perpetrator, arrest, rescue, or legal action is named.

Disturbing subject matter (trafficking, assault, abuse) is not itself a
Clickbait signal — serious stories are often disturbing, and a headline
shouldn't be marked Clickbait merely for covering a distressing topic. The
same anchoring-fact test applies regardless of topic: contrast the trafficking
example above with "Man hits stepdaughter with cement blocks to death after
sexually assaulting her" — equally graphic, but third-person, stating the
action and its consequence directly, with nothing held back for the click.

## Vague hype adjectives are not description

The same anchoring-fact test applies to ordinary declarative headlines, not
just quotes. A headline can be a complete, grammatical sentence with a named
subject and still convey no checkable information, if its only content is
subjective hype language — "huge," "plush," "stunning," "expensive,"
"adorable" — with nothing a reader could verify (a number, a brand, a
location, a specific claim). If the entire point is "something impressive
exists, go watch the video / see the photos," the headline's function is
identical to a curiosity gap: it drives a click to the media, not to inform.

- **Clickbait**: "Kofi Kinaata Puts His Huge House And Plush Living Room On
  Display (Watch Video)." "Huge" and "plush" are unquantified — no size, no
  location, no detail. Nothing here could be summarized as an actual fact;
  the headline's only job is to make you want to watch the video.
- **Informative**: "Davido Spoils Bride Chioma with $300K Richard Mille
  Diamond Watch at Miami Wedding." Also a wealth-flex story, but every claim
  is checkable — a specific watch brand and model, a dollar figure, a named
  event and location. A reader learns the actual fact without watching
  anything.

Naming the person and the general topic (a house, an outfit, a car) is not
enough on its own — the test is whether *any* of the descriptive content is
specific enough to be true or false, or whether it's all unfalsifiable
superlatives standing in for the actual content.
