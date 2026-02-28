# PCOS Blueprint Context

This document defines the long-term architectural direction,
design principles, and operational rules for this system.

---

## 1. Mission

Build a production-grade, automated macro-intelligence feed infrastructure
that consolidates high-quality global media sources into a unified system.

The system must be:
- Stable
- Transparent
- Extensible
- Long-term maintainable

---

## 2. Core Philosophy

1. Infrastructure first, features second.
2. Deterministic behavior over fragile cleverness.
3. Standards-compliant implementation.
4. Automation > manual intervention.
5. Long-term evolution mindset.

---

## 3. Current Architecture

Media Sources  
↓  
Python Aggregator  
↓  
Deduplication + Sorting  
↓  
RSS Generation  
↓  
Git Commit  
↓  
GitHub Actions  
↓  
GitHub Pages Deployment  

Status: Production-ready RSS core completed.

---

## 4. Technical Rules

- RSS must follow 2.0 spec.
- Atom self-link required.
- pubDate must be RFC 822 compliant.
- Sorting must use parsed datetime.
- All changes must not break backward compatibility.

---

## 5. Evolution Roadmap

Phase 1 – Infrastructure stabilization ✅  
Phase 2 – Metadata enrichment  
Phase 3 – Classification system  
Phase 4 – Analytical intelligence layer  
Phase 5 – Research-grade automation

---

## 6. Working Protocol With AI

When resuming discussions:

State:
"Use CONTEXT.md as architectural baseline."

Paste relevant section if needed.

AI must:
- Respect system philosophy
- Preserve long-term structure
- Avoid ad-hoc unstable changes

---

Last Updated: 2026-02-28
