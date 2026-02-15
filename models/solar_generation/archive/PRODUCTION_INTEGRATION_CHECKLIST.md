✅ Model 2 – Production Integration Checklist
1️⃣ Contract Stability

 Endpoint paths finalized (/api/v1/...)

 No planned renaming of fields

 No planned nesting changes

 Error format standardized:

{"status": "error", "message": "..."}


 Success format standardized:

{"status": "success", ...}


If all true → backend integration is safe.

2️⃣ Deterministic Behavior

 Same input always returns same structure

 month omitted → always returns full 12 months

 include_lifetime=false → lifetime block consistently omitted

 Out-of-bounds coordinates always return 400

 Missing API key always returns 401

Consistency > cleverness.

3️⃣ Failure Safety

 Model artifacts missing → 500 returned

 Corrupted metadata → 500 returned

 No raw tracebacks exposed in response

 No internal file paths leaked in errors

You never want stack traces reaching frontend.

4️⃣ Performance & Stability

 Average response time < 500ms

 No memory growth across repeated calls

 No file loading on every request (model loaded once at startup)

 No blocking external API calls during inference

If the model is loaded at app startup and reused → excellent.

5️⃣ Security & Guardrails

 API key required for all /api/v1/*

 Rate limit active (100/min per IP)

 Input validation on:

latitude

longitude

month range

 Coordinates bounded to SSA region

6️⃣ Versioning Protection

 Routes are under /api/v1/

 You are ready to create /api/v2/ later without breaking v1

This is critical for future upgrades.

7️⃣ Deployment Awareness

Right now you are using ngrok.

That is fine for integration testing, but confirm:

 Backend understands URL may change

 They know only base URL changes, not routes

 They are not hardcoding full URL including tunnel ID in permanent configs