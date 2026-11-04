# Palette's Journal - Critical Learnings Only

## 2026-11-04 - High-Contrast Focus Rings and Motion Accessibility in Web Dashboards
**Learning:** Dense monitoring dashboards (such as Zabbix and NOC panels) often feature dark themes and subtle borders that obscure standard browser focus rings, making keyboard navigation difficult. Furthermore, dynamic dashboards benefit from subtle transitions, but users with vestibular disorders require immediate respect for `prefers-reduced-motion`.
**Action:** When customizing dashboard styles, always pair keyboard `:focus-visible` outlines with high-contrast semi-transparent outer rings (`outline-offset` and `box-shadow`), and include a global `@media (prefers-reduced-motion: reduce)` block to instantly zero out durations for sensitive users.
