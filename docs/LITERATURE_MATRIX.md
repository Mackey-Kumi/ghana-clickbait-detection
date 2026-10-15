# Literature Matrix

The papers this project builds on, what each one did, and how it shaped a
decision in this project. Full citations are in the manuscript's reference
list.

| Paper | Data | Method | Key finding | How it is used in this project |
|---|---|---|---|---|
| Loewenstein (1994), *Psychological Bulletin* | Review of curiosity research | Theory | Curiosity is triggered by a gap between what we know and what we want to know ("information gap") | Theoretical basis for the codebook's definition of clickbait as *withholding* information |
| Chen, Conroy & Rubin (2015), ACM Workshop on Multimodal Deception Detection | Conceptual, with examples | Proposes lexical, semantic and image cues | Clickbait is a form of misleading content ("false news") | Motivation; supports treating clickbait as a reader-harm issue |
| Potthast, Köpsel, Stein & Hagen (2016), ECIR | ~3,000 tweets from news accounts | Hand-crafted features + classifier | First clickbait corpus; n-grams and specific "bait" phrases are strong signals | Inspired the TF-IDF n-gram baseline and the codebook's phrase-level signals |
| Chakraborty, Paranjape, Kakarla & Ganguly (2016), ASONAM | ~15,000 headlines; clickbait from BuzzFeed/Upworthy etc., non-clickbait from Wikinews/NYT | SVM on linguistic features | ~93% accuracy; built a browser extension | Showed the source-confound risk (clickbait and non-clickbait taken from different sites), which motivated per-headline labelling and the held-out-outlet test |
| Potthast, Gollub, Hagen & Stein (2018), Clickbait Challenge 2017 | ~38,000 crowd-annotated tweets | Shared task; many neural systems | Turned clickbait detection into a benchmark; neural models led | Background for comparing classical vs. neural models |
| Devlin, Chang, Lee & Toutanova (2019), NAACL | Large unlabelled corpora | BERT pre-training + fine-tuning | Fine-tuning a pre-trained transformer beats task-specific models on small labelled sets | Justifies fine-tuning a pre-trained model on ~800 training headlines |
| Sanh, Debut, Chaumond & Wolf (2019), arXiv | Same as BERT | Knowledge distillation | DistilBERT keeps most of BERT's accuracy while being ~40% smaller and faster | Choice of DistilBERT for Stage 4 (no local GPU, free Kaggle T4) |
| Williams, Nangia & Bowman (2018), NAACL | MultiNLI, ~433k sentence pairs | Natural language inference corpus | Broad-coverage NLI training data | The data `bart-large-mnli` was fine-tuned on |
| Lewis et al. (2020), ACL | Large text corpora | BART denoising seq2seq pre-training | Strong general-purpose encoder-decoder model | Base model of `facebook/bart-large-mnli` used in Stage 5 |
| Yin, Hay & Roth (2019), EMNLP-IJCNLP | Several text classification benchmarks | Zero-shot classification as NLI entailment | Labels rephrased as hypotheses allow classification without training data | Method behind the Stage 5 zero-shot comparison; motivated testing two label wordings |
| Gilardi, Alizadeh & Kubli (2023), PNAS | Several annotation tasks | ChatGPT vs. crowd workers | LLMs can match or beat crowd workers on some annotation tasks | Motivated AI pre-labelling, but only as drafts verified by a human (16.7% overridden) |
| Cohen (1960), *Educational and Psychological Measurement* | n/a | Cohen's kappa | Chance-corrected agreement between two raters | Inter-annotator agreement measure (κ = 0.057) |
| Landis & Koch (1977), *Biometrics* | n/a | Agreement benchmarks | Scale for interpreting kappa ("slight", "fair", ...) | Used to interpret κ = 0.057 as "slight" agreement |
| Pedregosa et al. (2011), JMLR | n/a | scikit-learn library | Standard ML toolkit | TF-IDF + Logistic Regression baseline, metrics |
| Wolf et al. (2020), EMNLP Demos | n/a | Hugging Face Transformers library | Standard transformer toolkit | DistilBERT fine-tuning and zero-shot pipeline |

**Gap this project addresses:** none of the clickbait datasets above cover
Ghanaian news, and Ghanaian clickbait has its own conventions (vague celebrity
references, decontextualised quotes, "(Watch Video)" tags, vague hype
adjectives). This project builds and labels a Ghanaian dataset and compares
the three modelling approaches on it.
