# StageOS Theme — Test Report & Roadmap

> **System under test:** the "StageOS" theme (WHMCS *Six* client-area template,
> currently at `7.10.0-release.1`) in `digital-expand/templates-six`.
> **Date:** 2026-05-29 · **Method:** static analysis (no live WHMCS/PHP backend
> available in this environment, so dynamic/end-to-end testing was out of scope).

---

## 1. What was tested

These are Smarty (`.tpl`) templates plus bundled CSS/JS/font assets. The
following static checks were run across all **147** templates and assets:

| # | Check | Result |
|---|-------|--------|
| 1 | Smarty block-tag balance (`{if}/{foreach}/{section}/…` open vs close) | ✅ Pass — 0 unbalanced blocks |
| 2 | `{include file=…}` target resolution | ✅ Pass (1 intentional fallback) |
| 3 | Local asset (`css/js/img`) reference existence | ✅ Pass |
| 4 | Empty/blank template audit | ⚠️ 2 deprecated blank files (intentional) |
| 5 | Bundled JS/CSS library versions & known CVEs | ❌ Findings (H1, H2) |
| 6 | `target="_blank"` reverse-tabnabbing | ❌ Findings (H3) |
| 7 | Mixed-content / insecure `http://` links | ⚠️ Findings (M3) |
| 8 | CSRF token presence in POST forms | ⚠️ Needs verification (M5) |
| 9 | Accessibility — `<img>` `alt` text | ⚠️ Findings (M2) |
| 10 | Deprecated HTML & inline styles | ⚠️ Findings (L1, L2) |
| 11 | External / dead CDN dependencies | ⚠️ Findings (M1, M4) |

**Good news:** the templates are structurally sound — every Smarty control
block is balanced, includes resolve, and referenced local assets exist. The
issues below are about **dependency age, security hardening, and front-end
modernization**, not broken markup.

---

## 2. Issues found

### 🔴 High severity (security)

**H1 — Bundled jQuery is `1.12.4` (end-of-life, multiple XSS CVEs).**
`js/scripts.js` bundles *jQuery JavaScript Library v1.12.4* (2016). jQuery
< 3.5 is affected by **CVE-2020-11022 / CVE-2020-11023** (cross-site scripting
via `.html()/.append()` on untrusted markup) and **CVE-2019-11358** (prototype
pollution). Any place the theme passes untrusted content through jQuery DOM
methods is potentially exploitable.

**H2 — Bootstrap `3.4.1` (end-of-life framework).**
`css/all.css` / `js/scripts.js` are built on Bootstrap 3, which reached EOL and
receives no security or compatibility fixes. It also drags in the old jQuery
dependency above.

**H3 — `target="_blank"` without `rel="noopener noreferrer"` (reverse tabnabbing).**
~12 templates open links in a new tab without `rel="noopener"`, letting the
opened page access `window.opener`. Affected files include:
`clientareaproductdetails.tpl`, `clientareaproducts.tpl`, `clientareadomains.tpl`,
`clientareadomaindetails.tpl`, `domainchecker-results.tpl`, `viewquote.tpl`,
`serverstatus.tpl`, `supportticketsubmit-kbsuggestions.tpl`, `clientregister.tpl`,
`twitterfeed.tpl`, `store/sitelock/index.tpl`, `store/marketgoo/index.tpl`.
(Modern browsers default `target="_blank"` to `noopener`, which mitigates but
does not excuse this — older clients remain exposed.)

### 🟠 Medium severity

**M1 — Dead/legacy IE8 shims from `oss.maxcdn.com`.**
`includes/head.tpl` and `oauth/layout.tpl` load `html5shiv` and `respond.js`
from `oss.maxcdn.com` inside `<!--[if lt IE 9]>` blocks. MaxCDN was retired;
these resources are effectively dead and the IE8 support they provide is
obsolete. `store/codeguard/index.tpl` uses a similar cdnjs shim.

**M2 — 120 `<img>` tags missing `alt` attributes (WCAG 1.1.1).**
Accessibility gap across the theme (product SSL status images, TLD logos,
spinners, CCV help images, etc.). Decorative images need `alt=""`; meaningful
ones need descriptive text.

**M3 — Insecure `http://` links to customer domains (5 templates).**
`clientareadomains.tpl`, `clientareaproducts.tpl`, `clientareaproductdetails.tpl`,
`clientareadomaindetails.tpl`, `domainchecker-results.tpl` link to
`http://{$domain}`. Should be protocol-relative (`//`) or `https://`.

**M4 — External Google Fonts dependency (`//fonts.googleapis.com`).**
`includes/head.tpl` loads Open Sans / Raleway from Google. This is a
render-blocking third-party request and a **GDPR/privacy** concern in the EU
(a German court has ruled embedded Google Fonts unlawful without consent).
Consider self-hosting the fonts (the `fonts/`+`webfonts/` dirs already exist).

**M5 — POST forms without a visible CSRF token — verify global protection.**
Most state-changing POST forms (e.g. `clientareadetails.tpl`,
`clientareachangepw.tpl`, `clientareaaddcontact.tpl`) contain no explicit
`{$token}` field. WHMCS injects CSRF tokens globally via JS
(`csrfToken` is set in `head.tpl`), so this is likely covered — but it should
be **confirmed against the running WHMCS install**, especially for any custom
forms, since it relies entirely on JS.

### 🟡 Low severity / tech debt

- **L1 —** 17 templates use deprecated HTML attributes (`align="…"`, etc.);
  heaviest in `invoicepdf.tpl` (19), `quotepdf.tpl` (13), `bulkdomainmanagement.tpl`.
- **L2 —** 33 inline `style="…"` usages — should move to stylesheets.
- **L3 —** 2 zero-byte dead templates: `pwreset.tpl`, `clientareacreditcard.tpl`
  (superseded by the `password-reset-*` flow and payment-methods pages).
- **L4 —** No front-end tooling in the repo: no `package.json`, linter,
  formatter, or CI. `all.css`/`scripts.js` are committed pre-built with no
  visible source/build pipeline, making upgrades risky.

---

## 3. Roadmap

A phased plan ordered by risk-reduction-per-effort. Phase 0/1 are safe,
low-risk changes shippable now; later phases are larger modernization efforts.

### Phase 0 — Quick wins (low risk, ship this week)
- [ ] **H3:** add `rel="noopener noreferrer"` to every `target="_blank"` link.
- [ ] **M3:** switch customer-domain links from `http://` to protocol-relative `//`.
- [ ] **M1:** remove dead `oss.maxcdn.com` IE8 shims (drop IE8 support outright).
- [ ] **L3:** delete the two zero-byte dead templates.

### Phase 1 — Accessibility & hardening (1–2 weeks)
- [ ] **M2:** add `alt` text to all 120 `<img>` tags (empty `alt=""` for decorative).
- [ ] **M4:** self-host Open Sans / Raleway and drop the Google Fonts request.
- [ ] **M5:** confirm CSRF coverage on every POST form against a live WHMCS
      instance; add explicit `{$token}` fields where not auto-protected.
- [ ] **L1/L2:** replace deprecated HTML attributes and inline styles with CSS classes.

### Phase 2 — Establish a build/test pipeline (2–4 weeks)
- [ ] Add `package.json` + a SCSS/asset build so `all.css`/`scripts.js` are
      generated, not hand-committed.
- [ ] Add linting/formatting (e.g. `stylelint`, `prettier`, an HTML/Smarty linter)
      and wire a **CI workflow** running the static checks from §1 on every PR.
- [ ] Add a SessionStart hook (`/session-start-hook`) so these checks run in
      Claude Code web sessions too.

### Phase 3 — Dependency modernization (the big one, 1–2 months)
- [ ] **H1/H2:** upgrade jQuery `1.12.4 → 3.7+` and migrate Bootstrap 3 → 5
      (or follow the upstream WHMCS theme path / the newer "Twenty-One" theme).
      This is breaking and must be done with full regression testing of every
      client-area page, order flow, and store add-on.
- [ ] Re-run the full §1 test matrix and a live click-through of all flows.

### Phase 4 — Continuous upkeep
- [ ] Track upstream WHMCS theme releases and merge security patches promptly.
- [ ] Add automated dependency-vulnerability scanning to CI.

---

## 4. How to reproduce these tests

The static checks above are scriptable (Smarty balance check, include/asset
resolution, `target=_blank`/`http://`/`alt`/deprecated-attribute greps). They
should be folded into the Phase 2 CI workflow so regressions are caught
automatically. None require a running WHMCS instance; the items marked
"verify against live install" (M5) do.
