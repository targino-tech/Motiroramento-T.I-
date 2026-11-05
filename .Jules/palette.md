# Palette's Journal - Critical UX & Accessibility Learnings

## 2026-10-27 - Accessible 3D Dashboards & Reduced-Motion Topology
**Learning:** HTML-based 3D perspective dashboard panels that rely on CSS transforms (`rotateX`, `rotateY`, `perspective`) and emoji-based status icons create accessibility barriers for users with vestibular sensitivities and screen reader users when semantic labels, focus states, and motion preferences are omitted.
**Action:** Always provide `@media (prefers-reduced-motion: reduce)` resets to flatten 3D card transforms, include descriptive `aria-label` / `title` attributes on telemetry cards, and make interactive visual cards keyboard-focusable with visible focus rings (`:focus-visible`).
