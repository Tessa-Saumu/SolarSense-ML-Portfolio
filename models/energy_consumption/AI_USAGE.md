## AI Usage – Model 1 (Energy Consumption Estimation)

This document records how AI tools were used in the implementation of **Model 1 – Energy Consumption Estimation**.

---

### Tools Used

- **Cursor** (GPT-based coding assistant)
- **OpenAI GPT models** via Cursor for:
  - Designing the formula-based estimation logic
  - Implementing validation and error handling
  - Generating documentation and example payloads

---

### Key Prompts That Drove Implementation

- High-level design and alignment with requirements:
  - “Model 1 Energy Consumption Investigation & Alignment – refrigeration-heavy SMEs, African climate adjustment, `/api/v1/estimate-consumption` endpoint…”
- Implementation details:
  - “Generate Flask API with equipment-based calculation, breakdown, and confidence score.”
  - “Add validation for business_type, equipment list with refrigeration requirement, and climate adjustment.”
- Documentation:
  - “Create README with request/response schemas, curl examples, and integration notes.”

---

### Estimated Time Saved

These numbers are indicative and not rigorously measured:

- **Design + implementation** of the formula-based estimator and Flask API:
  - Manual baseline: ~6–8 hours
  - With AI assistance: ~2–3 hours
- **Documentation** (README, integration guide, AI usage notes):
  - Manual baseline: ~2–3 hours
  - With AI assistance: ~0.5–1 hour

Overall estimated time saved: **~5–7 hours** for this MVP.

---

### Human Review Expectations

- A DSE lead should:
  - Sanity-check equipment power ratings and climate factors.
  - Validate that the refrigeration share heuristics (50–70%) match domain expectations.
  - Adjust documentation language and time-saved estimates to match internal standards if needed.





