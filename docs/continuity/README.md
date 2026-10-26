# Session continuity

This folder carries Yaparo's current working context between Codex chats, models, and people.

## Source of truth

- `STATE.md` is the compact, current handoff snapshot. Replace outdated snapshot details; do not turn it into a transcript.
- `PROJECT.md`, `ROADMAP.md`, and accepted ADRs remain the canonical project record. Update those when a decision or durable project status changes.
- The current user request and the repository's `AGENTS.md` instructions take precedence over this handoff note. Verify facts that may have changed, especially Git/PR state, provider quotas, and environment status.

## At the start of a session

1. Read `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, this file, and `STATE.md`.
2. Check the current branch, working-tree changes, latest commit, and linked pull request before editing.
3. Confirm the next action still matches the user's current request and the Phase 0 gates.

## At a milestone or handoff

Update `STATE.md` with only verified current facts: objective, completed work, branch/PR, checks actually run, remaining decisions/blockers, and one recommended next action. Update canonical docs when appropriate. Mark unverified information as unverified and include the date/time and timezone.

Never record API keys, passwords, access tokens, secret values, or private customer data here. If relevant, record only that a credential is stored in an approved secret store and whether it needs rotation. Do not copy credentials into another chat or model.

## Handoff preference — updated 23 October 2026

The owner disabled usage-limit checks and threshold-triggered stops. Do not query
usage or reactivate a usage monitor unless requested again. Existing monitors stay
paused. Normal milestone and end-of-session handoffs still apply: verify Git/PR/CI,
record unfinished work, update only changed facts and identify one next action.

## Copyable handoff prompt

> `C:\Users\ugrkb\OneDrive\Masaüstü\yaparo` deposundaki Yaparo (eski adı GrowthTwin) projesini kaldığı yerden sürdür. Önce `AGENTS.md`, `PROJECT.md`, `ROADMAP.md`, `docs/continuity/README.md` ve `docs/continuity/STATE.md` dosyalarını bu sırayla oku; sonra dalı, çalışma ağacını, son commit'i, açık PR'ları ve CI durumunu yeniden doğrula. Teknik koordinatör olarak işi küçük adımlarla ilerlet; terminal işlerini kullanıcıya yaptırma. Ürün Türkiye'de reklam vermek isteyen farklı kişi ve işletmelere hitap eder; diş klinikleri yalnızca olası müşteri örneğidir. Omneky, marka ve brief alımından çok formatlı reklam üretimi, bağlı kanallarda kampanya yayını, birleşik raporlama ve sınırlar içindeki iyileştirme için uzun vadeli yetenek ölçütüdür; tüm özellik ve kanallar ilk sürüme girmez. Sentetik veriyle yerel ürün geliştirmesi Phase 0 yayın hazırlığı tamamlanmadan da sürebilir; gerçek veri, canlı reklam hesabı, yayın, medya harcaması ve üretim AI kullanımı ayrı readiness kapıları geçilene kadar kapalıdır. Her gerçek kanal/harcama için reklamverenin açık izni, bağlı hesabı ve uygulanabilir sert limitleri gerekir; belirsizlikte dur. Gizli bilgileri hiçbir yere yazma ve ücretli altyapı ekleme. `STATE.md` içindeki tek Next action adımından devam et, uygun dokümanları güncel tut ve ilerlemeyi anlaşılır Türkçe özetle.

If the next model cannot access the repository, provide it the current `STATE.md` text and the user's new request. The repository remains the durable source of truth; never include secrets in the pasted context.


Current rename/runtime/compatibility evidence: [RENAMING.md](RENAMING.md).
Do not migrate secrets or reset durable IDs merely to match the new brand.

Current product priority (23 October 2026): [owned-core/open-source plan](../product/yaparo-open-source-master-plan.md)
and [Y01–Y32 delivery sequence](../product/yaparo-delivery-plan.md), accepted in
ADR-0040. Begin with the synthetic brand/material/editor/export slice; protected
Google candidate recovery is a separate integration workstream. No package or
provider choice is production-approved merely because it appears in research.

Owner priority correction (26 October 2026, ADR0070): download/export availability
is undecided. Existing PNG/ZIP prototypes are not a customer feature commitment;
no package work is next. Continue in-site brand→content→editing→campaign use.
