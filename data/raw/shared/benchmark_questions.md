# Evidence AI RAG Benchmark Questions (Phase 112)

**Purpose:** These 10+ ready-to-run questions validate the cross-document retrieval and synthesis capabilities of the Evidence AI RAG system. Each question references actual doc_ids from the current corpus to ensure coverage and allow immediate benchmark testing.

**Document Coverage Status:** ✓ 37 documents in corpus (DEVAL: 16, UNDP: 5, IKI: 3, plus 13 additional DEVAL PDFs)

**Last Updated:** 2025-11-19

---

## 1. Climate & Energy Resilience Theme

### Q1.1: Climate Adaptation Strategies Across African Regions
**Question:** Compare climate adaptation and resilience strategies documented in UNDP evaluations from Kenya and Sahel countries. What are the common approaches and regional differences?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2024001` (Kenya climate resilience evaluation)
- `UNDP-EVAL-2022198` (Joint UNDP-GIZ Sahel resilience programming)

**Evaluation Metrics:**
- Document retrieval accuracy (both docs retrieved)
- Cross-document synthesis quality (comparison extracted)
- Citation attribution fidelity

**Expected Answer Coverage:**
- Kenya: climate-smart agriculture, early warning systems, smallholder farmer training
- Sahel: community savings groups, livelihood support, adaptive programming under security constraints
- Regional differences: scale of beneficiaries, implementation challenges, donor coordination

**Difficulty Level:** Medium
**Document Count:** 2 (minimum required)

---

### Q1.2: Climate Finance Effectiveness in Infrastructure Projects
**Question:** Using IKI evaluations on grasslands and climate initiatives, what key lessons exist about financing mechanisms for climate mitigation projects? How cost-effective are the reported interventions?

**Referenced Doc_IDs:**
- `IKI-EVAL-2025-001` (Grasslands and savannahs climate initiatives)
- Additional IKI evaluations (as corpus grows from 3 to 300 documents)

**Evaluation Metrics:**
- Extraction of financial metrics and cost-effectiveness ratios
- Lesson distillation from multiple project evaluations
- Comparison across project types

**Expected Answer Coverage:**
- Financing models: national budgets, donor blending, community contributions
- Cost per hectare or per beneficiary where documented
- Lessons on co-benefits (biodiversity, livelihood)

**Difficulty Level:** Medium-High
**Document Count:** 1+ (pilot phase)

---

## 2. Governance & Rule of Law Theme

### Q2.1: Governance Strengthening in Fragile States
**Question:** Summarize the key findings and lessons from DEval and UNDP evaluations on governance capacity building. What institutional changes were documented in Bangladesh and what challenges appeared?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023087` (Bangladesh governance strengthening initiative)
- Multiple DEVAL evaluation reports (see benchmark_counts.csv: ~16 docs with SDG16 focus)

**Evaluation Metrics:**
- Institutional outcome extraction (committees established, officials trained)
- Challenge identification and mitigation strategies
- Learning transfer across country contexts

**Expected Answer Coverage:**
- Bangladesh: 450 local officials trained, 25 district governance committees
- Community trust improvement: 22% increase
- Institutionalization challenges and success factors
- Applicable lessons for other fragile state contexts

**Difficulty Level:** Medium
**Document Count:** 2-4 (currently available)

---

### Q2.2: Gender Equality and Women Empowerment in Governance
**Question:** What evidence exists in UNDP thematic evaluations about integrating gender into governance and social protection programming? Provide statistics on women's participation increases.

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023156` (Gender and women empowerment in Sub-Saharan Africa)
- Additional UNDP thematic evaluations (as ERC harvest expands)

**Evaluation Metrics:**
- Quantitative outcome extraction (participation rates, beneficiaries)
- Success factor identification
- Cost-effectiveness analysis where documented

**Expected Answer Coverage:**
- 250,000 women entrepreneurs supported
- Governance participation: 18% → 34% increase
- Cost per beneficiary: ~$250
- Partnership recommendations: women's organizations integration

**Difficulty Level:** Medium
**Document Count:** 1-3 (pilot phase)

---

## 3. Natural Resources & Biodiversity Theme

### Q3.1: Biodiversity and Green Infrastructure Outcomes
**Question:** What quantified biodiversity improvements are documented in UNDP evaluation of green infrastructure projects in Brazil? How do these connect to SDG15 targets?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023042` (Brazil green infrastructure outcome evaluation)
- Additional IKI biodiversity project evaluations (as corpus expands)

**Evaluation Metrics:**
- Quantitative outcome extraction (hectares restored, species indices)
- Job creation and livelihood benefits
- Progress toward SDG indicators

**Expected Answer Coverage:**
- 150,000 hectares of restored mangroves and forests
- Biodiversity index improvement: 18%
- 5,000 jobs created in conservation/restoration
- Co-benefits documentation
- Financial sustainability challenges

**Difficulty Level:** Medium
**Document Count:** 1-2 (pilot phase)

---

### Q3.2: Transboundary Water Governance and Climate Resilience
**Question:** As BGR reports on georesource governance become available, what lessons exist about transboundary groundwater management in the Niger Basin? How does this inform SDG6 monitoring?

**Referenced Doc_IDs:**
- `BGR-GR-2022-0087` (Georesource governance in Niger Basin - future)
- UN SDG and World Bank water governance reports (as corpus builds)

**Evaluation Metrics:**
- Cross-border governance mechanism documentation
- Climate vulnerability assessment integration
- Regional coordination recommendations

**Expected Answer Coverage:**
- Community access challenges across borders
- Climate vulnerability to hydrological changes
- Coordination mechanisms and their effectiveness
- Monitoring framework recommendations for SDG6

**Difficulty Level:** High (requires geospatial/transboundary understanding)
**Document Count:** 2+ (as corpus expands beyond pilot)

---

## 4. Human Development & Social Protection Theme

### Q4.1: Livelihood Support and Crisis Response Effectiveness
**Question:** Using UNDP joint evaluation data from Sahel countries, describe the evidence on community livelihood support during crises. What savings group models have been documented, and what is their reach?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2022198` (UNDP-GIZ Sahel resilience: crisis response evaluation)
- Additional UNDP evaluations from SDG1/SDG2 focused regions (as corpus grows)

**Evaluation Metrics:**
- Model replication and scale metrics
- Participatory outcomes (women membership percentages)
- Financial inclusion indicators

**Expected Answer Coverage:**
- Community savings groups: 850 established, 18,000 members
- Gender composition: 60% women
- 450,000 people reached with livelihood support
- Donor coordination: $12M leveraged
- Sustainability mechanisms

**Difficulty Level:** Low-Medium
**Document Count:** 1-2 (pilot phase)

---

## 5. Multi-Document Synthesis: Cross-Agency Comparison

### Q5.1: Comparative Effectiveness - UNDP vs. DEval on Evaluation Quality
**Question:** Comparing UNDP and DEval evaluation methodologies as documented in their sample evaluations, what differences exist in outcome measurement approaches? Which evaluation type produces more robust evidence for policy decisions?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2024001`, `UNDP-EVAL-2023087`, `UNDP-EVAL-2023156` (UNDP evaluations)
- `DEVAL-eval_report-*` series (16 DEval documents currently in corpus)

**Evaluation Metrics:**
- Methodology quality comparison
- Outcome indicator rigor
- Evidence attribution clarity
- Applicability to policy decisions

**Expected Answer Coverage:**
- Methodology approaches (randomized control, quasi-experimental, qualitative)
- Outcome measurement frameworks
- Scope of evaluations (project vs. thematic vs. outcome level)
- Recommendations quality and policy relevance

**Difficulty Level:** High (requires methodological literacy)
**Document Count:** 4+ (currently available)

---

## 6. Impact Quantification & Cost-Effectiveness

### Q6.1: Cost-Effectiveness Ratios Across Development Interventions
**Question:** Compiling available cost-effectiveness data from multiple UNDP, IKI, and DEval evaluations, what cost-per-beneficiary or cost-per-unit-impact metrics are documented? Which intervention types show best value?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023156` ($250 per beneficiary for gender/women empowerment)
- `UNDP-EVAL-2022198` ($12M donor funding, 450K people reached)
- `UNDP-EVAL-2023042` (green infrastructure cost structure)
- Expanding dataset from IKI, DEval as corpus grows

**Evaluation Metrics:**
- Numerator/denominator clarity in cost extraction
- Inflation adjustment and comparability
- Contextual factors affecting costs

**Expected Answer Coverage:**
- Gender empowerment: ~$250/beneficiary
- Sahel livelihood support: efficiency frontier from $12M reaching 450K
- Green infrastructure: cost per hectare restored
- Conservation: cost per job created
- Cross-sector comparison insights

**Difficulty Level:** High
**Document Count:** 3+ (pilot phase, expanding to 20+)

---

## 7. SDG Progress Monitoring

### Q7.1: SDG16 (Peace, Justice, Institutions) Progress in Multiple Countries
**Question:** Across Bangladesh, Sahel, and other regions, what progress indicators exist for SDG16 targets? How are community trust, institutional capacity, and anti-corruption measured?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023087` (Bangladesh: community trust in local government +22%)
- `UNDP-EVAL-2022198` (Sahel: governance institution building)
- DEval evaluations on governance (as corpus specifics expand)

**Evaluation Metrics:**
- Indicator harmonization across sources
- Baseline-endline progress tracking
- Attribution clarity

**Expected Answer Coverage:**
- Trust indices and measurement methods
- Institutional capacity metrics (officials trained, institutions established)
- Anti-corruption mechanisms and effectiveness
- Regional comparisons
- SDG16 sub-target alignment

**Difficulty Level:** Medium-High
**Document Count:** 2-3 (pilot), expanding to 10+

---

## 8. Multilingual Retrieval & Evidence Synthesis

### Q8.1: German and English Language Evidence Integration
**Question:** Once DEval German-language reports are processed, synthesize climate and gender findings across German (DEval/BMZ) and English (UNDP/World Bank) sources. What evidence gaps exist between German and global perspectives?

**Referenced Doc_IDs:**
- DEval policy briefs and evaluations (German language processing pipeline)
- UNDP climate evaluations (English)
- IKI climate assessments (German/English bilingual)
- BMZ policy briefs (German + translation)

**Evaluation Metrics:**
- Language processing accuracy
- Cross-lingual evidence linking
- Perspective/approach divergence identification

**Expected Answer Coverage:**
- German evidence on SDG13 and SDG16
- English evidence on same topics
- Methodological differences (German evaluative tradition vs. Anglo-American)
- Complementarity in thematic focus
- Evidence gaps needing further research

**Difficulty Level:** High (requires translation + synthesis)
**Document Count:** 4+ (as multilingual processing scales)

---

## 9. Real-World RAG Workflow: Policy Brief Generation

### Q9.1: Climate Finance & Adaptation Policy Brief
**Question:** Using UNDP Kenya climate evaluation and IKI climate initiative evaluations, generate a 2-page policy brief for development finance officers on effective climate adaptation financing mechanisms. What do the evaluations recommend?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2024001` (Kenya climate resilience)
- `IKI-EVAL-2025-001` (Grasslands climate initiatives)
- Additional IKI evaluations (as available)
- Emerging KfW green finance evaluations

**Evaluation Metrics:**
- Recommendation extraction accuracy
- Evidence citation fidelity
- Brief coherence and usability
- Policy actionability

**Expected Answer Coverage:**
- Financing models: climate-smart agriculture investment
- Community participation: smallholder farmer reach (15,000+ in Kenya)
- Co-benefits: food security, biodiversity, livelihoods
- Scaling recommendations
- Early warning systems and climate information services
- Implementation challenges

**Difficulty Level:** High
**Document Count:** 2-4 (pilot), 10+ (scaled)

---

## 10. Accountability & Lesson Learning

### Q10.1: Evaluation Findings on Implementation Barriers
**Question:** Synthesizing barriers and challenges across UNDP and DEval evaluations, what are the top implementation obstacles documented in governance, climate, and livelihood interventions? What workarounds or adaptations succeeded?

**Referenced Doc_IDs:**
- `UNDP-EVAL-2023087` (Bangladesh governance challenges)
- `UNDP-EVAL-2022198` (Sahel security/climate adaptation barriers)
- `UNDP-EVAL-2023042` (Green infrastructure sustainability challenges)
- DEval evaluation reports (challenge/lesson sections)

**Evaluation Metrics:**
- Challenge identification and categorization
- Mitigation strategy extraction
- Transferability assessment

**Expected Answer Coverage:**
- Governance: staffing, technical capacity, political will
- Climate adaptation: security constraints, climate unpredictability
- Livelihood: market access, asset vulnerability
- Finance: sustainability mechanisms, cost recovery
- Successful adaptations and workarounds
- Lessons for future programming

**Difficulty Level:** Medium
**Document Count:** 3-4 (pilot), 15+ (scaled)

---

## 11. Source Coverage Gaps & Future Benchmarks

### Q11.1: Quality Infrastructure (SDG9) Evidence Assessment
**Question:** Once PTB quality infrastructure cooperation documents are harvested, what evidence exists on metrology reforms improving SME competitiveness? What outcomes are documented in ECOWAS states?

**Referenced Doc_IDs:**
- PTB technical reports and evaluations (future ingestion, target: 500 docs)
- IKI technical cooperation evaluations (emerging)
- World Bank technical assistance reports (future, target: 250 docs)

**Evaluation Metrics:**
- Evidence synthesis across agencies
- SME outcome attribution
- Regional applicability

**Expected Answer Coverage:**
- Metrology standards adoption rates
- SME productivity/competitiveness improvements
- Cost-benefit analysis
- Institutional sustainability

**Difficulty Level:** Medium-High
**Document Count:** 0 (requires PTB harvest), target 5-10

---

### Q11.2: Global SDG Monitoring via UN VNRs and Synthesis Reports
**Question:** Once UN Voluntary National Review documents are integrated, compare SDG progress narratives across regions. Where is fastest progress on SDG16 (peace/justice)? What are the bottlenecks?

**Referenced Doc_IDs:**
- UN GSDR chapters and synthesis (future, target: 800 docs)
- UN VNRs from multiple countries (future, target: 700 docs)
- UNDP ERC evaluations by region (current: 5 pilot docs; target: 1500)

**Evaluation Metrics:**
- Cross-country progress comparison
- Bottleneck identification consistency
- Evidence attribution to source countries

**Expected Answer Coverage:**
- Regional SDG16 progress rates
- Institutional strengthening success stories
- Common barriers and solutions
- Donor engagement effectiveness
- Multi-stakeholder partnership effectiveness

**Difficulty Level:** High
**Document Count:** 0 (requires UN harvest), target 20+

---

## Benchmark Question Administration

### Running Individual Questions

```bash
# Example: Run Q1.1 with RAG system
python -m evidence_ai.rag_engine --query "Q1.1" --corpus-docs UNDP-EVAL-2024001,UNDP-EVAL-2022198

# Example: Run Q5.1 with full cross-agency context
python -m evidence_ai.rag_engine --query "Q5.1" --corpus-docs UNDP-EVAL-*,DEVAL-eval_report-* --metrics detailed
```

### Success Criteria

**Baseline (Pilot Phase - 37 documents):**
- ✓ Q1.1, Q2.1, Q2.2, Q3.1, Q4.1, Q5.1, Q6.1, Q7.1, Q9.1, Q10.1 must retrieve relevant docs (exact matches)
- ✓ Synthesis quality: extractable findings (50% of answers above require 2+ doc synthesis)
- ✓ Citation accuracy: ≥90% of referenced findings traceable to source doc_ids

**Scaled Phase (1,000+ documents):**
- ✓ Q1.2, Q3.2, Q11.1, Q11.2 become fully answerable with expanded corpus
- ✓ Cross-lingual Q8.1 operational with German processing pipeline
- ✓ Multi-year/multi-agency trends identifiable from 10+ document synthesis

**Failure Modes to Monitor:**
- Hallucinated citations (doc_ids that don't exist in corpus)
- Missing documents (relevant docs not retrieved despite corpus inclusion)
- Out-of-context synthesis (combining findings from unrelated interventions)
- Attribution errors (crediting findings to wrong source or country)

---

## Corpus Expansion & Question Re-validation

This benchmark suite should be re-validated quarterly as the corpus grows:

- **Q1 (Dec 2025):** Corpus 100 docs; retest Q1.1-Q1.2, evaluate Q3.2 readiness
- **Q2 (Mar 2026):** Corpus 500 docs; activate Q2.2 variants with DEval + BMZ German evidence
- **Q3 (Jun 2026):** Corpus 2,500 docs; full multi-source synthesis benchmarks (Q5.1, Q6.1, Q7.1)
- **Q4 (Sep 2026):** Corpus 5,000+ docs; Q11.1 (PTB), Q11.2 (UN VNRs) readiness assessment

---

## Related Documentation

- **Corpus Strategy:** See `dataset/dataset_strategy.md` for source coverage targets and SDG alignment
- **Metadata Schema:** See `data/raw/metadata_schema.yaml` for field standardization
- **Deduplication Report:** See `data/raw/shared/logs/dedup_report.json` for duplicate tracking
- **Benchmark Methodology:** See `research/benchmarks/BENCHMARK_METHODOLOGY_PROPOSAL.md` for evaluation framework
- **PII Review Queue:** See `data/raw/shared/pii_review.csv` for documents requiring redaction before public use
