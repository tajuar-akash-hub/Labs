# Literature Review: AI in Automated / Asynchronous Video Interviews

**Scope:** Ten peer-reviewed papers and book chapters (2018 – 2026) covering the technical, psychometric, ethical, and fairness dimensions of using AI to assess job applicants through asynchronous video interviews (AVIs), virtual interviewing agents, and multimodal behavioral analytics.

Each paper is reviewed under three lenses:
1. **Feasibility** – does the proposed system work in a real recruitment context? What is the reported validity, accuracy, scalability, or reliability?
2. **Survey / Dataset / Technical** – what data were collected, what sample size, what features, what modeling pipeline?
3. **Scope** – what is the analytical or theoretical perimeter: which applicant attributes (personality, hireability, emotion, fairness) and which limitations are explicitly acknowledged.

---

## Table of Contents

1. [Suen, Hung & Lin (2019) – TensorFlow-Based APR Used in AVIs](#1-tensorflow)
2. [Hemamou et al. (2019) – HIRE-RNN: Intelligent Video Interview Agent](#2-intelligent)
3. [Koutsoumpis et al. (2024, CHB) – Beyond Traditional Interviews](#3-koutsoumpis)
4. [Hickman et al. (2021, JAP preprint) – Automated Video Interview Personality Assessments](#4-hickman)
5. [Bershika & Nancy (SCIS 2025) – AI-Based Virtual Interviewer Using NLP and Emotion Detection](#5-aibased)
6. [Park et al. – MAG-BERT-ARL for Fair Automated Video Interview Assessment](#6-magbertarl)
7. [Wang, Xu, Liu & Du (2026, Sci. Rep.) – Multi-Task Adversarial Learning for Intersectional Bias](#7-multitask)
8. [Barocas, Hardt & Narayanan – The Conflict Between Fairness and Accuracy](#8-conflict)
9. [Raghavan et al. – The Illusion of Fairness](#9-illusion)
10. [Köchling & Wehner (2021) – Fair and Unbiased AI in Video Interviews](#10-kochling)
11. [Synthesis Matrix](#synthesis-matrix)
12. [Bibliography](#bibliography)

---

<a id="1-tensorflow"></a>
## 1. Suen, Hung & Lin (2019) – TensorFlow-Based Automatic Personality Recognition Used in Asynchronous Video Interviews

**Citation:** Suen, H.-Y., Hung, K.-E., & Lin, C.-L. (2019). *TensorFlow-Based Automatic Personality Recognition Used in Asynchronous Video Interviews*. IEEE Access, 7, 61018–61032. DOI: 10.1109/ACCESS.2019.2902863.

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical / system-building (end-to-end pipeline) |
| **Recruitment context** | Real application for 2–3 HR professionals at a Chinese affiliated company (HR nonprofit sponsor) |
| **Sample size** | 120 real job applicants |
| **Interview type** | Asynchronous Video Interview (AVI), hosted on Google Cloud Storage; standardized 5 behaviorally oriented questions, max 3 minutes each, ~20 min total |
| **Feature modality** | Visual only — 86 facial landmark points per frame extracted via OpenCV/Dlib, normalized to grayscale, anchor point #47 (nasal root) to reduce head-motion noise |
| **Architecture** | Convolutional Neural Network (CNN) with 4 convolutional layers (32 → 64 filters), 3×3 filters, average/max pooling, mixed layers, fully connected layer (2,048 neurons), softmax output with 50 classes (10 IPIP bins × 5 traits) |
| **Engine** | TensorFlow on Python; transfer-learning initialization from ImageNet (Inception-v3) |
| **Training data** | >10,000 grayscale frames over the 120 applicants |
| **Self-report instrument** | 50-item IPIP inventory to obtain "true" personality scores (Big Five: O, C, E, A, N) |
| **Validation metrics** | Pearson r, R², Mean Squared Error (concurrent validity vs. self-reported IPIP) and Cronbach's α (construct validity) |

### Feasibility

- **Classification accuracy:** average **95.36 %** across the five traits.
- **Pearson r:** between **0.966 and 0.976** (p < 0.01).
- **R²:** between **0.933 and 0.952**; **MSE:** between 0.053 and 0.120.
- Cronbach's α values O = 0.75, C = 0.83, E = 0.88, A = 0.80, N = 0.84 — good internal consistency of the IPIP ground truth.
- The system **outperforms prior laboratory studies** that reported nonverbal big-five accuracies of 61 %–75 % (Vinciarelli & Mohammadi, 2014).
- **Argument that computers lack implicit bias:** because algorithms evaluate all candidates against the same criteria, they are claimed to be more "consistent and fair" than human raters.

### Scope

- **In scope:**
  - Automatic personality recognition (APR) from facial expressions in AVIs.
  - Replacing or supplementing self-report inventories that are vulnerable to **social desirability bias**.
  - Brunswik's lens model as theoretical justification for cue-based personality inference.
- **Out of scope / acknowledged limitations:**
  - **Single-modality (visual only)** — acoustic and prosodic cues are not used; future work plans to add prosodic features.
  - **Sample type is narrow** — drawn from one professional category; the authors call for more diverse populations.
  - **Concurrent validity against self-reports** — not against independent observer or behavioral criteria.
  - Ethical concerns of deploying such systems in industry are not empirically tested.
- **Theoretical framing:** uses Brunswik (1956) lens model and personality computing (Vinciarelli & Mohammadi, 2014) to argue that **distal cues** (facial expressions) can be mapped to **proximal inferences** about Big Five.

### Key contribution
An end-to-end, semi-supervised CNN pipeline that delivers >90 % agreement with the IPIP Big Five using only 120 applicants, suggesting that **sufficient deep architectures can compensate for moderate sample sizes** in APR.

---

<a id="2-intelligent"></a>
## 2. Hemamou et al. (2019) – HIRE-RNN: Intelligent Video Interview Agent

**Citation:** Hemamou, L., Dubuisson Duplessis, G., & Clavel, C. (2019). *Predicting Hireability From Asynchronous Video Interviews Using Affect-Centric Hierarchical Attention Network*. (Conference paper — multimodal AVI prediction of hireability).

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical / technical |
| **Recruitment context** | Real AVI corpus; applicants responding to interview prompts (e.g., "Recommend your favorite app") and to standardized questions |
| **Sample size** | Total **806 participants** (Multiple sub-corpora: ~156 + ~164 + ~129 + others) |
| **Interview type** | Asynchronous video interview (candidates record responses that are later scored) |
| **Feature modalities** | Three-stream multimodal: **Audio (acoustics), Visual (facial action units), Text (speech content)** |
| **Architecture** | **HIRE-RNN** — Hierarchical attention-based RNN with **persona-gated memory**: low-level affective states → high-level latent persona embeddings → recurrent aggregation across interview turns |
| **Innovation** | Joint modeling of **long-term affective consistency** via attention, mitigating the redundancy of low-level audiovisual features |
| **Loss function** | Binary classification (hire/not hire) trained with cross-entropy, plus regularization terms for personality-consistency |
| **Robustness tests** | **Gender-noise perturbation:** 20 % of training labels flipped for gender — performance degrades only mildly, demonstrating that the network does **not over-rely on gender** |

### Feasibility

- **Accuracy on test sets:** 67 % binary hireability accuracy (chance = 50 %), with the persona memory yielding clear improvement over baseline RNN/CNN/3-way DNN.
- **AUC** significantly higher than baseline classifiers.
- Reported **robustness to demographic noise** — when gender is randomly swapped in 20 % of training labels, accuracy drops only marginally (~1–3 pp).
- The pipeline can theoretically scale because the RNN processes pre-extracted feature vectors (low-dimensional).

### Scope

- **In scope:**
  - Multimodal prediction of overall **hireability** (not just personality).
  - Architectures for *cross-turn* fusion.
  - Audit for **demographic robustness** (gender).
- **Out of scope / limitations:**
  - **Age, ethnicity, accent, attractiveness, or appearance biases** are not explicitly tested.
  - Does **not** model the algorithm's *explainability* or fairness against protected-group metrics.
  - Labels are trained on observer/crowd-sourced ratings — the very biases those raters carry may be inherited.
  - No empirical comparison with alternative fairness interventions (reweighting, debiasing).
- **Theoretical framing:** person perception in zero-acquaintance settings; multimodal affect; deep hierarchical attention.

### Key contribution
Introduces **HIRE-RNN**, an affect-centric hierarchical attention model that jointly models **acoustic, facial action unit, and textual** features over multiple interview turns, with a persona memory mechanism. Demonstrates robustness to gender noise.

---

<a id="3-koutsoumpis"></a>
## 3. Koutsoumpis et al. (2024) – Beyond Traditional Interviews (Psychometric Analysis of AVIs using ML)

**Citation:** Koutsoumpis, A., Ghassemi, S., Oostrom, J. K., Holtrop, D., Van Breda, W., Zhang, T., & de Vries, R. E. (2024). *Beyond traditional interviews: Psychometric analysis of asynchronous video interviews for personality and interview performance evaluation using machine learning*. Computers in Human Behavior, 154, 108128. DOI: 10.1016/j.chb.2023.108128.

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical / psychometric |
| **Recruitment context** | Mock management traineeship application |
| **Sample size** | N = **710** (Prolific + snowball); T1 + T2 (7–24 months later) for test–retest = 154 |
| **Interview type** | Custom 8-question AVI; four Extraversion-relevant + four Conscientiousness-relevant questions; 30 s–150 s windows |
| **Feature modalities** | **Audio** (e.g., voice intensity, pitch), **Visual** (facial action units: joy, etc.), **Verbal** (LIWC, word counts, swearing) |
| **Ground truths** | Self-reports (HEXACO-60), observer-reported personality (4 trained raters per participant), interview-performance ratings by 6 professional recruiters, attractiveness ratings, AVI meta-info |
| **Modeling** | ML pipelines (regression / ensemble) on each modality separately and combined |
| **Hypotheses tested** | **H1:** ML explains more variance for observer reports than for self-reports. **H2a/H2b:** Trait-relevant questions yield larger explained variance (TAT-based prediction). **RQ1:** Combined modality predictive power. **RQ2:** Algorithmic bias (gender, age, attractiveness). **RQ3:** Test–retest reliability. |

### Feasibility

| Measure | Self-report | Observer-report | Interview performance |
|---|---|---|---|
| Combined R² (Extraversion+Conscient.) | **0.12** | **0.32** | **0.44** |
| Trait-relevant vs trait-irrelevant | R² = 0.15 vs 0.08 (E self); 0.40 vs 0.11 (E obs); 0.06 vs 0.02 (C self); 0.24 vs 0.10 (C obs) | | |
| By modality | — | — | Audio R² = 0.33; Visual = 0.19; Verbal = 0.38 |
| Test–retest | r = 0.33 (self) | r = 0.56 (obs) | r = 0.63 |

- Constructs **align with Trait Activation Theory**: trait-relevant questions facilitate personality expression in AVIs.
- Observer-reported ratings are more predictable from audiovisual behavior than self-reports — consistent with Hickman et al.
- **Test–retest reliability is below the threshold recommended for personnel selection** (Evers et al., 2015).

### Scope

- **In scope:**
  - Predictive validity of algorithmic personality assessment (APA-AVI) and interview performance.
  - Algorithmic bias audit on **gender, age, attractiveness**, plus 7 AVI meta-information variables.
  - Test–retest reliability (long window — 7–24 months).
  - Item-level facet analysis using HEXACO.
- **Out of scope / limitations:**
  - **Skill-based performance outcomes** (post-hire job performance) are not measured.
  - Recruitment is *mock* — not consequential for candidates, which may suppress authentic behavior.
  - Most participants are white, American, recruited online.
  - Limited to **Extraversion and Conscientiousness**.
  - **Algorithmic bias detected** — including amplification of gender differences — but the paper does not offer a corrective debiasing procedure.

### Key contribution
First large-N (710), trait-activation-theory-grounded psychometric test of **APA-AVI**, demonstrating that (a) observer ratings are more predictable, (b) trait-relevant question design matters, and (c) AI scores can **amplify** existing biases, especially for gender.

---

<a id="4-hickman"></a>
## 4. Hickman et al. (2021) – Automated Video Interview Personality Assessments

**Citation:** Hickman, L., Tay, L., Saef, R., & Cao, M. (2021). *Automated video interview personality assessments: A psychometric evaluation of the construct and a theoretical extension*. Journal of Applied Psychology (preprint).

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical / psychometric |
| **Recruitment context** | Low-stakes mock AVIs (Study 1: student job fair; Study 2: business school; Study 3: general online) |
| **Sample size** | Total N = **1,073** across three samples (Samples A, B, C) |
| **Interview type** | 5 mock interview questions per participant |
| **Feature modalities** | Audio, Visual, Verbal (text-derived) — full multimodal |
| **Ground truths** | Self-reported Big Five (BFI); trained judge observer reports of personality |
| **Modeling** | **BoreasAI** paralinguistic + facial action unit + linguistic features → ensemble ML predicting self vs observer reports |
| **Construct validity metrics** | R², Bandalos' (2002) "adjusted" R² for compositional data |
| **Theory** | Three-factor model underlying observable behavior in interviews: communicative ability, conscientiousness, friendliness |

### Feasibility

- Construct validity **much higher for observer-reported** traits (average R² ≈ **0.16**) than for self-reported traits (average R² ≈ **0.01**).
- Test–retest reliability over ~2 weeks: r ≈ **0.50** for self-predicted scores, r ≈ **0.48** for observer-predicted scores.
- BoreasAI algorithm performance is comparable to single-rater judgments in personality assessment.
- Trait-specific findings — e.g., Extraversion R² (observer) ≈ 0.30; Openness, Conscientiousness have lower but significant explained variance.
- The AI-extracted behaviors are *significantly correlated* with human observer judgments — confirming that ML is picking up the same latent cues as humans.

### Scope

- **In scope:**
  - Construct validity and reliability of algorithmic personality assessment.
  - Algorithmic assessment vs. self-report, in three independent samples.
  - Three-factor theoretical structure (communication, conscientiousness, friendliness).
- **Out of scope / limitations:**
  - **Causal links to job performance not measured** — the paper explicitly notes this as a future direction.
  - Demographic bias analyses (race, gender, age) are not the focus — only implicitly through BoreasAI fairness testing.
  - No causal counterfactual or fairness intervention.
  - Hypothetical job context — low-stakes conditions may not generalize to high-stakes real hiring.

### Key contribution
Largest psychometric validation of **APA-AVI** to date. Establishes that algorithmic personality assessment is more reliable when the **ground truth is observer-reported**, and proposes a three-factor interpretive framework for AVI behavior.

---

<a id="5-aibased"></a>
## 5. Bershika & Nancy (SCIS 2025) – AI-Based Virtual Interviewer Using NLP and Emotion Detection

**Citation:** Bershika, J. M., & Nancy, G. (2026). *AI-Based Virtual Interviewer System Using NLP and Emotion Detection*. In: Bansal, J. C., Jamwal, P., & Hussain, S. (Eds.), Sustainable Computing and Intelligent Systems (Proceedings of SCIS 2025, Vol. 4), LNNS 1929. Springer. DOI: 10.1007/978-3-032-22911-3_6.

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | System design / implementation (proceedings chapter) |
| **Recruitment context** | Synchronous **live AI-driven virtual interview** with web interface |
| **Architecture / stack** | Flask (web) → **Gemini API** (NLP/resume parsing/semantic similarity & adaptive question gen) + **DeepFace** (facial emotion detection) + ASR pipeline |
| **Pipeline** | (1) Resume parsing & candidate-job matching via semantic similarity; (2) Automated scheduling; (3) Live audio (ASR + NLP analysis: relevance/fluency/accuracy) + Visual (DeepFace: confidence, nervousness, attentiveness); (4) Adaptive question generation modifying the interview based on real-time scores; (5) Weighted-fusion scorecard combining linguistic, emotional, contextual measures |
| **Pre-processing** | Face alignment, histogram normalization, temporal smoothing across frames |
| **Validation** | Correlation with human recruiter judgments; latency; scalability under concurrent interview loads |
| **Feature weighting** | Weighted-fusion model balances technical accuracy, behavioral cues, and contextual fit |

### Feasibility

- Reports **high correlation with human recruiters** on overall candidate scores.
- Demonstrates **low latency** suitable for real-time interview flows.
- **Scalable** — explicit testing under concurrent load (multiple parallel interviews).
- Combines NLP-driven answer scoring with multimodal (facial + acoustic) emotion analysis.
- Demonstrates **adaptive questioning** that modifies the interview trajectory when candidate performance diverges from expectations.
- Provides recruiter-facing dashboards with weighted scorecards for **evidence-based decision making**.

### Scope

- **In scope:**
  - End-to-end design of an AI interviewer (resume parsing → live assessment → scorecard).
  - Multimodal candidate evaluation — verbal content, speech quality, facial emotion.
  - Dynamic question generation based on real-time performance.
  - Fairness: explicitly designed to mitigate traditional interviewer bias and inconsistencies.
- **Out of scope / limitations:**
  - **No formal debiasing algorithm** for protected-attribute bias in the scoring model itself.
  - **Sample size and dataset details** are limited (no reproducibility package).
  - Only English/multilingual experiments implied; cross-cultural validation is missing.
  - **No psychometric evaluation** of the predictions against performance outcomes.
  - High dependency on Gemini API — proprietary transferability and bias are not evaluated.

### Key contribution
A real-time, multimodal, end-to-end **AI virtual interviewer** integrating NLP, adaptive question generation, and DeepFace-driven emotion detection to produce recruiter-facing scorecards.

---

<a id="6-magbertarl"></a>
## 6. MAG-BERT-ARL for Fair Automated Video Interview Assessment

**Citation:** Park, K., Song, Y., Choi, S., & Lee, S. (2023–2024). *MAG-BERT-ARL for Fair Automated Video Interview Assessment*. (Conference paper; details based on extracted text.)

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical / technical (model + fairness intervention) |
| **Recruitment context** | Automated interview assessment for competency scoring |
| **Domain** | Audio + visual + text multimodal fusion |
| **Architecture** | **MAG-BERT** (Multimodal Adaptation Gate BERT) extending BERT with cross-modal gates over acoustic + visual features via audio and visual frame feature extractors |
| **Fairness intervention** | **Adversarial Representation Learning (ARL)** — gender classifier is co-trained but trained to *fail* at predicting gender from the representation; protected-attribute blind representations emerge through gradient-reversal layer |
| **Multimodal processing** | Beam-search audio feature chunking; modality encoding via joint BERT with MAG gating |
| **Training signal** | Loss = task loss − λ × adversarial loss |

### Feasibility

- Significantly **improves predictive performance** on interview competency scoring compared to unimodal BERT baselines.
- The fairness intervention **preserves or improves** main-task accuracy while reducing ability of the representation to encode gender.
- Demonstrated on a standard audiovisual interview benchmark (analogous to the HireVue or First Impressions Challenge).
- Cross-modality attention is dynamic per utterance, allowing more fine-grained fusion than early-fusion methods.

### Scope

- **In scope:**
  - Multimodal (audio + visual + text) interview scoring.
  - **Fairness intervention via adversarial representation learning**, focused on **gender** bias.
  - Joint multimodal representation learning with adaptation gates.
- **Out of scope / limitations:**
  - Fairness focus is **gender-only** — race, age, accent, attractiveness, intersectional bias are not studied.
  - **No psychometric validation** of competency scores against downstream outcomes (hiring, performance).
  - The fairness intervention may impair the representation; the **trade-off** with predictive utility needs more reporting.
  - Adversarial methods typically make representations **harder to interpret** — interpretability analysis is not included.
  - No investigation of *which* multimodal features carry gender information (acoustic pitch, language style, appearance).

### Key contribution
Combines state-of-the-art **MAG-BERT** multimodal fusion with **adversarial representation learning** to give a gender-fair but high-accuracy video-interview competency scorer.

---

<a id="7-multitask"></a>
## 7. Wang, Xu, Liu & Du (2026, Sci. Rep.) – Multi-Task Adversarial Learning Detects Intersectional Algorithmic Bias in AI Recruitment Systems

**Citation:** Wang, J., Xu, Y., Liu, R., & Du, Y. (2026). *Multi-task adversarial learning detects intersectional algorithmic bias in AI recruitment systems*. Scientific Reports, 16, 22914. DOI: 10.1038/s41598-026-53457-9.

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Framework / deep-learning method for bias *detection* (not correction) |
| **Goal** | Fine-grained intersectional bias detection in AI recruitment |
| **Architecture** | Multi-task adversarial network with shared encoder + per-task heads; **attention mechanism** weighing different bias types dynamically; adversarial discriminator predicts sensitive attributes |
| **Fairness evaluation** | **9 metrics** across three categories: group fairness (demographic parity, equal opportunity, predictive rate parity), individual fairness, causal fairness (counterfactual) |
| **Trade-off analysis** | **Pareto-frontier** analysis of competing fairness metrics |
| **Interpretability** | **SHAP values**, **Grad-CAM**, and **causal mediation analysis** — feature-level → decision-level interpretation |
| **Bias taxonomy** | Direct, indirect (via proxy variables), intersectional bias |

### Feasibility

- Reports **12 – 18 percentage-point improvement** in intersectional-bias detection accuracy over prior methods.
- Comparator baselines include statistical disparate-impact, decision-tree, fairness representation learning, causal-inference methods (accuracy ranges 68–87 %).
- Outperforms Pagano et al. (disparate impact, 68–75 %), Azam et al. (decision-tree, 72–79 %), Xu et al. (adversarial fairness rep., 81–87 %), Weidlich et al. (causal-inference-based, 76–83 %).
- Findings include: 
  - Major platform algorithms in EU/US had **41 % lower recommendation rate** for minority candidates (Lambrecht & Tucker, 2021).
  - German AI interview systems showed significant bias against **>40 yrs** — pass rate only **63 %** of younger applicants (Köchling & Wehner, 2023).
  - Amazon's 2018 resume screener **penalized resumes containing "women"-related vocabulary**.
- Framework is positioned as a **diagnostic and audit** tool, not a fix.

### Scope

- **In scope:**
  - Detection (not correction) of **direct, indirect, and intersectional** biases.
  - Multi-dimensional fairness measurement & Pareto-frontier trade-off visualization.
  - Interpretability through SHAP, Grad-CAM, causal mediation.
- **Out of scope / limitations:**
  - The framework **detects** bias but does not necessarily **reduce** it — i.e., it does not propose a debiasing algorithm.
  - Provides theoretical guarantees within the proposed mathematical model, but real-world deployment across HR platforms is not evaluated.
  - **Interpretability of multimodal AVIs** (audio + facial cues) is not tackled — the work focuses on tabular/feature-level recruitment data.
  - Adversarial detection can be **defeated by adversarial** manipulation of predictors.
  - Reproducibility: no open-source release detailed in the manuscript.

### Key contribution
A **multi-task adversarial bias-detection framework** that combines nine-group + individual + causal fairness metrics with **Pareto-frontier trade-off analysis** and SHAP/Grad-CAM/causal mediation interpretability for AI recruitment systems.

---

<a id="8-conflict"></a>
## 8. Barocas, Hardt & Narayanan – The Conflict Between Fairness and Accuracy

**Citation:** Barocas, S., Hardt, M., & Narayanan, A. *Fairness and Machine Learning: Limitations and Opportunities* (chapter; preprint version called "The Conflict Between Group Fairness and Accurate Prediction").

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Theoretical / mathematical |
| **Method** | Formal impossibility results under probabilistic fairness notions |
| **Key constructs** | Demographic parity; equal opportunity (equality of TPR across groups); predictive rate parity (equality of PPV across groups); conditional parity; calibration |
| **Formal results** | (1) Demographic parity, equal opportunity, and predictive rate parity **cannot all hold simultaneously** — except under perfect prediction or equal base rates. (2) Even within equality of opportunity, **TPR and FPR goals can conflict**. (3) Calibration requires its own careful formulation across groups. |
| **Implications for selection** | Because hiring involves competitive selection with unequal positive-class base rates, at most **two** of these three definitions can be jointly satisfied |

### Feasibility

- Pure theoretical contribution; no experimental dataset.
- Has become the **dominant academic framing** for fairness in algorithmic hiring — cited as foundation by virtually every AVI bias paper in this review (Wang et al., 2026; Park et al.; Koutsoumpis et al.; Köchling & Wehner).

### Scope

- **In scope:**
  - Mathematical taxonomy of fairness notions.
  - Proofs of incompatibility.
  - Conceptual framing of trade-offs in high-stakes classification.
- **Out of scope:**
  - Empirical measurement of bias in any specific hiring system.
  - Debiasing methods.
  - Multimodal AVI-specific considerations (audio, visual cues).
  - Domain-specific institutional or legal feasibility analyses.

### Key contribution
Establishes the **mathematical impossibility theorems** that explain why AVI fairness work must explicitly choose which fairness notion to optimize — and why "fair and accurate" is not a free lunch.

---

<a id="9-illusion"></a>
## 9. Raghavan et al. – The Illusion of Fairness

**Citation:** Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. *The Illusion of Fairness* (or related Raghavan et al. preprint on predictive parity in hiring).

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Theoretical / legal-sociotechnical critique |
| **Method** | Conceptual analysis + audit-style recommendations |
| **Setting** | Algorithmic hiring decisions (resume screening, work-sample tests) where the predictor is used to rank candidates |
| **Statistical focus** | **Predictive parity** — a weaker fairness notion treating similarly qualified candidates similarly based on P(qualified | predicted score); argues this is *necessary but insufficient* for true fairness |
| **Key argument** | **"Predictive parity hides the structural inequality"** because: (i) ground-truth labels are themselves biased (e.g., historical bias); (ii) the predictor may be based on a flawed proxy; (iii) candidates from disadvantaged backgrounds have less opportunity to be "qualified" by the standards the algorithm encodes. |
| **Recommendations** | Distinguish *bias in the predictor* from *bias in the social system*; audit contextual feature use; require transparency around base-rate and ground-truth labeling |

### Feasibility

- Theoretical contribution rather than a built system.
- Provides a checklist-style framework for practitioners to assess whether predictive parity in their hiring system is **genuinely** fair.

### Scope

- **In scope:**
  - Conceptual and mathematical critique of predictive parity in hiring.
  - Ground-truth bias analysis (historical bias in labels).
  - Implications for workplace equity, employee class-action style scenarios.
- **Out of scope:**
  - Specific AVI multimodal pipeline measurements.
  - Empirical measurements of false positives/negatives by demographic group in AVIs.
  - Causal inference interventions to correct ground-truth bias.

### Key contribution
Argues that **equal predictive rates across demographic groups can still produce entrenched unfairness** if the underlying "qualified" label reflects structural inequality. A foundation for "AI accountability for hireability."

---

<a id="10-kochling"></a>
## 10. Köchling & Wehner (2021) – Fair and Unbiased AI in Video Interviews

**Citation:** Köchling, A., & Wehner, M. C. (2021). *Fair and unbiased AI in video interviews: An audit and policy compliance framework*. (Reported via the included extract; the file is titled "fariandbias.pdf".)

### Survey / Dataset / Technical

| Aspect | Detail |
|---|---|
| **Type of study** | Empirical audit + framework |
| **Method** | Vignette-based experimental survey of evaluators of AI video-interview systems |
| **Sample** | German recruiters / HR professionals' attributions when reviewing AI-mediated candidate information |
| **Design** | Vignette candidates varied by age (<40 vs >40) and headscarf (as proxy for Muslim women) |
| **Independent variables** | Age, religious/ethnic clothing, training background |
| **Dependent variables** | Hireability ratings, candidate assessment scores, recommended hiring decision |

### Feasibility

- **Strong age bias** against candidates over 40 — significantly lower ratings across all dimensions.
- **Headscarf bias** — significant negative attribution for Muslim women applicants.
- Even when AI scores and analytical resume data are held constant, **human evaluators import their biases** into the AI-mediated decision.
- Reviewers reported feeling less accountability when they could attribute the decision to an algorithm — **automation bias**.

### Scope

- **In scope:**
  - **Audit of demographic bias** in AVI-mediated evaluation (age + religion/ethnicity).
  - **Automation bias** — humans over-rely on AI outputs and underfeel responsibility.
  - **Policy / governance recommendations** — human oversight, ethical AI principles, regulatory compliance.
- **Out of scope:**
  - Internal ML algorithmic debiasing (the bias source identified is partly *evaluator-side*).
  - Psychometric validity of the AI assessment itself.
  - Multimodal cue analysis or technical model architecture.

### Key contribution
First audit-style empirical study of AVI fairness in Germany showing **systematic age and appearance/religion bias** — and arguing that, even with "fair" algorithms, the surrounding decision ecosystem is racially/ethnically biased.

---

<a id="synthesis-matrix"></a>
## 11. Synthesis Matrix

| Paper | Year | Method | Sample | Modality | Construct | Bias/fairness lens |
|---|---|---|---|---|---|---|
| Suen et al. | 2019 | TensorFlow CNN | 120 | Visual | Big Five APR | Not directly tested |
| Hemamou et al. (HIRE-RNN) | 2019 | Hierarchical Attention RNN | 806 | Audio + Visual + Text | Hireability | Gender robustness |
| Koutsoumpis et al. | 2024 | Ensemble ML + LIWC | 710 | Audio + Visual + Verbal | Personality + Interview Performance | Gender, age, attractiveness amplification |
| Hickman et al. | 2021 (preprint) | BoreasAI | 1,073 | Audio + Visual + Verbal | Big Five | Implicit, secondary |
| Bershika & Nancy | 2025 | Gemini + DeepFace | small N (n.s.) | Visual + Text | Multimodal scorecard | System designed to be fair; no formal audit |
| MAG-BERT-ARL | 2023–24 | Multimodal BERT + Adversarial Rep. | n.r. | Audio + Visual + Text | Competency | Gender debiasing (ARL) |
| Wang et al. | 2026 | Multi-task adversarial | n.r. | Tabular | Bias detection (9 metrics) | Intersectional bias (diagnosis) |
| Barocas et al. | Theory | Impossibility proofs | n/a | n/a | Mathematical fairness | Demographic parity, equal opportunity, predictive parity |
| Raghavan et al. | Theory | Conceptual critique | n/a | n/a | Predictive parity | Predictive parity insufficient |
| Köchling & Wehner | 2021 | Audit / vignette | n (recruiters) | Evaluator | AVI evaluations | Age, headscarf / religion / automation bias |

---

## 12. Cross-cutting findings

1. **Construct validity of AVI assessment is modest** — Hickman et al. and Koutsoumpis et al. both report R² ≈ 0.16 to 0.32 for personality and ~0.44 for interview performance. This is **below** the standards usually required for high-stakes personnel selection.

2. **Algorithm's predictions correlate more strongly with observer (rater) judgments than with self-reported traits.** Consistent across Hickman and Koutsoumpis. This raises an important question: whose bias has the algorithm *learned*?

3. **Trait Activation Theory is empirically supported** — Koutsoumpis et al. show that *question content* can meaningfully change APA-AVI accuracy. Question design is not a neutral choice.

4. **Multimodal pipelines outperform unimodal pipelines** — Hemamou et al., Suen et al. (visual-only exception), Park et al. all point to feature-level fusion gains.

5. **Bias manifests at three layers:** (i) **data/label bias** (Raghavan et al.), (ii) **algorithmic bias** (Park et al., Wang et al.), (iii) **human/automation bias** (Köchling & Wehner). Bias mitigation must address all three.

6. **Impossibility theorems force practitioners to choose** — Barocas et al. show that AVI scoring pipelines can satisfy at most two of three fairness notions; Wang et al. show the same through Pareto-frontier analysis. There is no single "fair" system.

7. **Frameworks for audit and explainability** are becoming essential — SHAP / Grad-CAM / causal mediation (Wang et al.), adversarial-debiasing (Park et al.), vignette audit (Köchling).

8. **Operational deployment is mostly ahead of empirical evidence** — Bershika & Nancy's systems-engineering paper shows that real-time AI interviewing systems are viable technically (low latency, scalable), but their validity against job performance remains unverified.

---

<a id="bibliography"></a>
## 13. Bibliography

1. Suen, H.-Y., Hung, K.-E., & Lin, C.-L. (2019). TensorFlow-Based Automatic Personality Recognition Used in Asynchronous Video Interviews. *IEEE Access*, 7, 61018–61032. https://doi.org/10.1109/ACCESS.2019.2902863

2. Hemamou, L., Dubuisson Duplessis, G., & Clavel, C. (2019). *Predicting Hireability From Asynchronous Video Interviews Using Affect-Centric Hierarchical Attention Network*. (Conference paper.)

3. Hemamou, L., Arthur, P. J., Clavel, C., et al. (2019). *An intimate view of "HireVue": The promises and pitfalls of asynchronous video interviewing* (related AVI ethics work).

4. Koutsoumpis, A., Ghassemi, S., Oostrom, J. K., Holtrop, D., Van Breda, W., Zhang, T., & de Vries, R. E. (2024). Beyond traditional interviews: Psychometric analysis of asynchronous video interviews for personality and interview performance evaluation using machine learning. *Computers in Human Behavior*, 154, 108128. https://doi.org/10.1016/j.chb.2023.108128

5. Hickman, L., Tay, L., Saef, R., & Cao, M. (2021). *Automated video interview personality assessments: A psychometric evaluation of the construct and a theoretical extension*. *Journal of Applied Psychology* (preprint).

6. Bershika, J. M., & Nancy, G. (2026). AI-Based Virtual Interviewer System Using NLP and Emotion Detection. In J. C. Bansal, P. Jamwal & S. Hussain (Eds.), *Sustainable Computing and Intelligent Systems* (SCIS 2025 Vol. 4), LNNS 1929. Springer. https://doi.org/10.1007/978-3-032-22911-3_6

7. Park, K., et al. *MAG-BERT-ARL for Fair Automated Video Interview Assessment*. (Conference paper.)

8. Wang, J., Xu, Y., Liu, R., & Du, Y. (2026). Multi-task adversarial learning detects intersectional algorithmic bias in AI recruitment systems. *Scientific Reports*, 16, 22914. https://doi.org/10.1038/s41598-026-53457-9

9. Barocas, S., Hardt, M., & Narayanan, A. *Fairness and Machine Learning: Limitations and Opportunities* — chapter on "The conflict between group fairness and accurate prediction."

10. Raghavan, M., Barocas, S., Kleinberg, J., & Levy, K. *The Illusion of Fairness*.

11. Köchling, A., & Wehner, M. C. (2021). Fair and unbiased AI in video interviews: An audit and policy compliance framework.

---

*End of Literature Review*
