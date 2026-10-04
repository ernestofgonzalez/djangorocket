# Accordion

A vertically stacked set of headers that each reveal one section of content.
Use it to shorten long pages of secondary detail — FAQs, settings groups,
specs — where readers scan titles and open only what they need.

No motion: sections open and close instantly.

```bash
$ djangorocket add accordion
```

The template lands at `<templates_dir>/accordion/accordion.html`.

## Usage

```django
{% include "components/ui/accordion/accordion.html" with title="Questions" items=faq_items %}
```

`items` is whatever iterable of mappings (or objects) your view hands the
template:

```python
faq_items = [
    {
        "title": "What does the plan include?",
        "body": "Every plan includes unlimited projects, version history for "
                "90 days and email support.",
    },
    {
        "title": "How is billing calculated?",
        "body": "You are billed per active seat at the start of each cycle.",
        "id": "billing",
    },
    {
        "title": "Single sign-on (SAML)",
        "meta": "Business plan only",
        "body": "",
        "disabled": True,
    },
]
```

## Props

| Prop | Default | What it does |
| --- | --- | --- |
| `items` | — | Required. The sections. See the item keys below. |
| `title` | — | Section heading, beside the list on desktop and above it below that. |
| `description` | — | A line under the heading. Hidden on mobile. |
| `allow_multiple` | `False` | `True` lets several sections stay open at once. The default is single: opening one closes the other. |
| `show_index` | `False` | `True` numbers the headers `01`, `02`, … The index is dropped on mobile. |
| `icon_style` | `"chevron"` | `"chevron"` or `"plus"`. |
| `open_index` | `0` | The section open on first render. `-1` starts with every section closed. |
| `heading_level` | `3` | The heading tag the triggers sit in, so the accordion slots into the page outline. |
| `component_id` | `"accordion"` | Prefix for generated DOM ids. Set it when a page has more than one accordion and the items carry no explicit ids. |
| `omit_assets` | `False` | `True` skips the `<style>`/`<script>` block. Pass it on every include after the first on a page. |

### Item keys

| Key | What it does |
| --- | --- |
| `title` | The header label. Wraps; never truncated. |
| `body` | The panel content. Plain text — mark it safe to pass HTML. |
| `meta` | Optional qualifier under the title on tablet and desktop. Use it to say why a disabled item is unavailable. |
| `open` | `True` renders this section open regardless of `open_index`. |
| `disabled` | `True` dims the header to 45% and takes it out of the tab order and the arrow-key ring. |
| `id` | Becomes the panel's DOM id, so a URL fragment (`#billing`) opens that section on load. |

## More than one on a page

The first include carries the shared `<style>` and `<script>`; later ones pass
`omit_assets=True` and a distinct `component_id`:

```django
{% include "components/ui/accordion/accordion.html" with title="Questions" items=faq_items component_id="faq" %}
{% include "components/ui/accordion/accordion.html" with title="Specifications" items=spec_items component_id="specs" omit_assets=True %}
```

Each accordion keeps its own open state; single mode never reaches across.

## Behaviour

- **Expand & collapse.** Clicking anywhere on the header toggles its panel — the
  whole row is the target, not just the icon. Every section may be closed; none
  is forced open.
- **No motion.** Panels appear and disappear instantly, and the glyph swaps in
  the same frame. Nothing transitions.
- **Keyboard.** Tab moves between headers and into open panel content. Enter or
  Space toggles the focused header. ↓/↑ move focus to the next/previous header
  and wrap; Home and End jump to first and last. Disabled headers are skipped.
- **Semantics.** Each header is a `<button>` inside a heading, carrying
  `aria-expanded` and `aria-controls`; the panel is `role="region"` with
  `aria-labelledby` pointing back.
- **Find-in-page.** Closed panels stay in the DOM as `hidden="until-found"`, so
  the browser's find can open them, and the header's state follows.
- **Deep links.** A URL fragment naming a panel (`#billing`) opens that section
  on load and moves focus to its header.

## Theming

Colors, type and spacing come from the design-system custom properties, each
with a fallback baked in, so the component looks right on a page that defines
none of them and follows the theme on a page that does:

| Property | Falls back to |
| --- | --- |
| `--color-text` | `#201e1d` — headers, body, the outer rules |
| `--color-accent` | `#ec3013` — the expanded icon and index, the focus ring |
| `--color-divider` | `rgba(32, 30, 29, .4)` — the rule between items |
| `--font-heading` | `"Archivo", system-ui, sans-serif` — headers |
| `--font-body` | `"Archivo", system-ui, sans-serif` — panel copy |
| `--space-1…8` | the 4 px scale — gaps and the index gutter |

Set them on `:root` (or on any ancestor) to retheme the component. The design it
was built from sets Archivo; load it, or point `--font-heading` / `--font-body`
at your own faces.

## Measurements

| Property | Desktop ≥ 1024px | Tablet 640–1023px | Mobile < 640px |
| --- | --- | --- | --- |
| Header min-height | 64px | 56px | 48px |
| Header padding (y) | 20px | 16px | 12px |
| Title | 20 / 600 | 18 / 600 | 16 / 600 |
| Icon / hit area | 20px in 40px | 20px in 40px | 20px in 44px |
| Panel inset (left) | 0 | 0 | 0 |
| Panel bottom padding | 24px | 20px | 16px |
| Body | 15 / 1.6, max 68ch | 15 / 1.6, max 68ch | 15 / 1.6 |
| Rules | 2px ink outer · 2px divider inner | Same | Same |

Desktop sits in a 3-of-4 column span with the section title in column 1. Tablet
stacks the title above. Mobile drops the index, the meta and the description,
and grows the hit area to 44px.
