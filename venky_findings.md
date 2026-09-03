# Venky's Findings — Dashboard Review

**Author**: Venky
**Date**: 2026-09-02
**Scope**: Manual walkthrough of the running Zoiko Rooms admin/host dashboard. These are UX and functional gaps observed while clicking through the live app — not yet cross-checked line-by-line against the codebase.

---

## 1. Rooms Available page lacks detail
No proper detailed explanation shown on the Rooms Available page. Data should be pulled from a single "golden" source table so every live room shows the same complete, consistent set of details — no partial or inconsistent info between rooms.

## 2. Room type search/filter is broken
Clicking the room-type filter/container button doesn't fetch or return results. Search is not working on this page.

## 3. Duplicate functions across the dashboard
The same functionality appears to be implemented more than once — both in the main sidebar navigation and again inside individual pages. Needs consolidation so there's one source of truth per function instead of repeated logic.

## 4. Payments tab is too shallow
The Payments tab only fetches and displays a bare payment status. No real detail behind it (breakdown, history, context) — needs proper depth, not just a status flag.

## 5. Document verification isn't linked to the next step
There's no real connection between identity/document verification and what happens after. If a document is verified as true, the process should automatically move forward to the next step — this isn't implemented as an actual working flow yet, just disconnected pieces.

## 6. Can't view/download documents from the dashboard
Uploaded documents should be viewable and directly downloadable from within the dashboard. Currently not available.

## 7. Ratings are mock data
Ratings shown are hardcoded/mock, not real. Should be calculated from actual user reviews — an average across all customers who stayed in that specific room or villa.

## 8. Sublet tab needs more filters
The Sublet tab needs additional filters and requirement fields — current version is too bare to be useful.

## 9. Hosting flow doesn't auto-fetch location details
When a host creates a room listing tied to a real/true location, the system should automatically fetch and pre-fill relevant details for that location — reducing manual data entry and hesitation for the host, instead of making them type everything themselves.

## 10. Newly hosted rooms don't appear in Live Rooms
After a host creates a room, it doesn't show up in the Live Rooms tab. The room exists but isn't visible where it should be.

---

## Additional Gaps (found via code & docs review, not dashboard clicking)

These were found by actually reading the backend code, migrations, and the `docs/` spec files during setup — not from the UI. Included here since a few directly explain findings above.

## 11. Published listings don't reflect real occupancy
A room stays visible in search as "available" (`state = PUBLISHED`) even after a renter has actually moved in (`Occupancy.status = ACTIVE`). Nothing in the code automatically pauses or unpublishes a listing when it becomes occupied — only an admin manually pausing it would hide it. This is likely connected to finding #1 (no reliable "golden table" view of true room status) and possibly #10.
`backend/app/crud/listing.py`, `backend/app/models/occupancy.py`

## 12. New host-created rooms may be stuck pre-publish
Related to finding #10: a new listing starts at `DRAFT` and only becomes visible after passing `REVIEW → APPROVED → PUBLISHED`. If that approval step isn't surfaced anywhere in the host's UI, a host has no way to know their room is sitting unpublished, waiting on an admin action they can't see.
`backend/app/models/listing.py` (`LISTING_STATES`)

## 13. No renter/host account exists by default
`backend/seed.py` only creates an admin account and sample guest records — it never creates a real `UserAccount` (the renter/host login). Out of the box there's no way to test the renter/host side of the dashboard without registering a new account manually first.
`backend/seed.py`, `backend/app/models/user_account.py`

## 14. Branding endpoint returns 401 on public/login pages
`Logo.tsx` calls `/api/settings/branding` on every page load, including the login screens, before any authentication exists — so it 401s repeatedly in the browser console on pages that should be fully public. Cosmetically harmless (falls back to no logo) but is a real bug in how that endpoint is gated.
`src/components/ui/Logo.tsx`

## 15. Chatbot's audit log doesn't record what data it exposed
`tool_results_json` exists as a column on `ChatMessage` but is never populated anywhere in the code. The audit trail shows which tools the AI called, but not what data those tools actually returned — a real gap if this is ever reviewed for a compliance/data-leak investigation.
`backend/app/services/chat_service.py`, `backend/app/models/chat.py`

## 16. AI Assistant is far behind its own spec
The 14 design documents in `docs/` describe a full RAG-based AI assistant — vector search with citations, a knowledge base, jurisdiction-aware answers, a confirm-before-acting flow for anything beyond read-only lookups. What's actually built is a simpler tool-calling chatbot with no vector database, no citations, and no knowledge base at all. Roughly 9% of the documented spec exists in code today.

## 17. Code references compliance documents that don't exist
Docstrings/comments cite `ZR-COM-DATA-RIGHTS-001`, `ZR-INV-SEARCH-001`, and `ZR-API-INT-001` as if they're real governing documents, but none of the three exist anywhere in the repo — impossible to verify the code actually complies with them.




## Next steps
- [ ] Cross-check each finding against the actual code (routes/components) to confirm root cause before fixing
- [ ] Prioritize and assign
- [ ] Track fixes against this list
