Project purpose:
DecisionCanvs is an AI-powered business analytics copilot that converts uploaded business data into analysis, visual dashboards, and executive recommendations.

Development priorities:
1. Stability
2. Clear business value
3. Polished UX
4. Reliable chart generation
5. Strong README and demo flow

Rules:
- Use schema-validated JSON between backend and frontend
- Keep chart generation constrained to approved templates
- Prefer deterministic analysis over opaque AI reasoning
- Never fabricate metrics or causal claims
- Mark assumptions and uncertainty clearly
- Keep components modular and strongly typed
- Optimize for a 3-minute live demo

UI standard:
- B2B SaaS quality
- minimal, clean, professional
- no clutter, no gimmicks

Testing:
- Validate response schemas
- Validate chart specs
- Validate at least one upload-to-dashboard flow