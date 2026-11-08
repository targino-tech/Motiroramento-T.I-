# Palette's Journal - Critical Learnings Only

## 2026-03-31 - Accessible and Interactive HTML Overview Cards in Grafana Dashboards
**Learning:** Grafana text panels rendering raw HTML topology cards often rely purely on visual emoji indicators without accessibility roles or semantic labels, preventing screen readers from conveying infrastructure status. Moreover, displaying status cards without navigation links creates dead ends for NOC operators who expect to click on a summary metric to inspect its dedicated dashboard.
**Action:** When designing or updating HTML summary panels in Grafana, wrap high-level system cards in semantic anchor links (`<a>`) pointing to sub-dashboards with `aria-label` describing current operational status, and assign `role="img"` with descriptive labels to status icons.
