---
name: accessibility-guardian
description: Generation-time accessibility rules for web UI. Apply when writing HTML, JSX/TSX, Vue/Svelte templates, forms, modals, custom widgets, or any user-facing component. Targets WCAG 2.2 Level AA — the standard most laws now require. Skip for headless code, server-only logic, or non-UI scripts.
---

# Accessibility Guardian

WCAG 2.2 AA is the target. The six errors below account for ~96% of all detected accessibility failures on the web (WebAIM Million, 2025/2026). Rules below are ordered by how often the failure shows up in real code.

First rule of ARIA: don't use ARIA. Pages using ARIA average 2× the errors of pages without — semantic HTML covers most cases, ARIA only patches what HTML can't express.

## 1. Names and labels

- **Every form control has a programmatic label.** `<label for="x">` paired with `id="x"`, or wrap the input. Placeholder is not a label. Use `aria-label` only when there's no visible text (icon-only inputs).
- **Every button has an accessible name.** Text content, or `aria-label` for icon-only. No empty `<button>`. SVG icons inside an interactive element get `aria-hidden="true"` so they don't fight the text for the name.
- **Every link has descriptive text.** No "click here," "read more," bare arrows. The link's text alone should make sense out of context.
- **Every meaningful image has `alt`.** Decorative images: `alt=""` (empty, not missing — missing means the screen reader reads the filename). Functional images (icons inside links/buttons): describe the action, not the picture.
- **Every page declares `lang` on `<html>`.** Add `lang` to inline content in a different language too.

## 2. Structure (semantic HTML first)

- **Use the right element.** `<button>` for actions, `<a href>` for navigation, `<input type="…">` for inputs, `<nav>`/`<main>`/`<header>`/`<footer>`/`<aside>` for landmarks. A `<div onClick>` is a bug — not focusable, not announced, not an action.
- **Heading hierarchy is sequential.** One `<h1>` per page. No skipping levels. Headings convey structure, not size — use CSS for size.
- **Lists are `<ul>`/`<ol>`/`<li>`. Tables are `<table>` with `<th scope>`.** Don't fake them with divs.
- **ARIA only where semantic HTML falls short.** When you must, follow the WAI-ARIA Authoring Practices for the specific pattern (combobox, tabs, menu, etc.) — partial implementations create worse experiences than no ARIA.

## 3. Keyboard and focus

- **Every interactive element is keyboard-operable.** Tab to focus, Enter/Space to activate. Custom widgets own their keyboard model (arrow keys in menus/listboxes, Esc to close dialogs).
- **Visible focus indicator on every focusable element.** Never `outline: none` without a replacement. The focused element must not be obscured by sticky headers, banners, or overlays (WCAG 2.2 SC 2.4.11).
- **Tab order matches visual order.** No positive `tabindex` values. `tabindex="0"` makes something focusable; `tabindex="-1"` makes it programmatically focusable but skipped by Tab.
- **Modals trap focus and restore it.** Focus moves in on open, can't Tab out, returns to the trigger on close. Esc closes.
- **Provide a skip link** to main content when there's substantial repeated navigation.

## 4. Visual and motion

- **Contrast: 4.5:1 for body text, 3:1 for large text** (≥18pt, or ≥14pt bold) **and UI components.** Don't convey state through color alone — pair with text, icon, or pattern.
- **Touch targets ≥24×24 CSS pixels** (WCAG 2.2 SC 2.5.8); 44×44 preferred. Smaller is acceptable only with sufficient surrounding space.
- **Respect `prefers-reduced-motion`.** Disable or reduce non-essential animation, parallax, and auto-play under that media query.
- **No drag-only or hover-only controls.** Every drag interaction needs a single-pointer alternative (WCAG 2.2 SC 2.5.7). Every hover-revealed control has a focus-revealed equivalent.
- **Layout reflows to 200% zoom** without horizontal scroll or clipped content. Avoid fixed pixel heights on text containers.

## 5. Forms and feedback

- **Errors are announced and fixable.** Set `aria-invalid="true"` on the field; link the message via `aria-describedby`. Describe what's wrong and how to fix it. Red border alone is not enough.
- **Required fields are marked in text** ("(required)") and with `aria-required="true"` — not just `*`.
- **Group related inputs** with `<fieldset>` + `<legend>` (especially radio/checkbox groups).
- **Live updates use `aria-live`.** `polite` for non-urgent (saved, results loaded), `assertive` only for critical alerts.
- **Don't force re-entry of data already provided in the same flow** (WCAG 2.2 SC 3.3.7). Prefill, autofill, or "same as above."

## Cross-cutting

- **Keyboard-only test before shipping.** If you can't complete a flow without a mouse, neither can your users.
- **Screen reader spot-check** at least once per major UI (VoiceOver: Cmd+F5; NVDA on Windows). Listen to one full task — what's announced, what's silent, what's wrong.
