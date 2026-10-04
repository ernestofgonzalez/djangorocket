# Button

Triggers an action. Three variants set the hierarchy — one primary per view,
secondary for the alternatives, ghost for low-weight inline actions.

Labels sit flush left: a button wider than its label never centers it.

```bash
$ djangorocket add button
```

The template lands at `<templates_dir>/button/button.html`.

## Usage

```django
{% include "components/ui/button/button.html" with label="Create project" %}
```

Every other include on the page passes `omit_assets=True`, so the shared
`<style>`, icon sprite and `<script>` are written once:

```django
{% include "components/ui/button/button.html" with label="Create project" %}
{% include "components/ui/button/button.html" with label="Cancel" variant="secondary" omit_assets=True %}
```

`{% include %}` inherits the page's context, so a view that already has a
`title` or `href` in scope would leak it into the button. Add `only` to seal
it off:

```django
{% include "components/ui/button/button.html" with label="Cancel" variant="secondary" omit_assets=True only %}
```

## Props

| Prop | Default | What it does |
| --- | --- | --- |
| `label` | — | Required. The button text. Verbs, sentence case, one line — it never truncates; the button grows. With `icon_only` it becomes the accessible name and the tooltip. |
| `variant` | `"primary"` | `"primary"`, `"secondary"` or `"ghost"`. |
| `size` | `"md"` | `"sm"` (32px), `"md"` (36px) or `"lg"` (48px). |
| `href` | — | Renders an `<a>` instead of a `<button>`. |
| `type` | `"button"` | `"button"`, `"submit"` or `"reset"`. Ignored when `href` is set. |
| `icon` | — | Leading glyph. See the set below. |
| `trailing_icon` | — | Trailing glyph, same set. |
| `icon_svg` | — | Custom leading markup, used instead of `icon`. Mark it safe. |
| `trailing_svg` | — | Custom trailing markup, used instead of `trailing_icon`. Mark it safe. |
| `icon_only` | `False` | Drops the label from view and squares the button off to `size` × `size`. |
| `block` | `False` | Full width, with the label — and any trailing icon — flush against the left padding edge. |
| `disabled` | `False` | Dims to 45% and takes it out of the tab order. |
| `loading` | `False` | Swaps a spinner in ahead of the label, hides the icons, sets `aria-busy` and ignores repeat clicks. |
| `loading_label` | `label` | The label while loading. |
| `name`, `value` | — | Submitted with the form. |
| `title` | — | Tooltip. Defaults to `label` when `icon_only`. |
| `button_id` | — | DOM id, so a script can find this button. |
| `extra_classes` | — | Appended to the class list, as a JS or layout hook. |
| `omit_assets` | `False` | Skips the `<style>`/`<svg>`/`<script>` block. Pass it on every include after the first on a page. |

### Icons

`icon` and `trailing_icon` take one of `plus`, `download`, `edit`, `arrow`,
`chevron` or `check` — the glyphs the design draws, in a sprite the asset block
carries. Anything else goes through `icon_svg` / `trailing_svg`:

```django
{% include "components/ui/button/button.html" with label="Sign in with GitHub" icon_svg=github_mark omit_assets=True %}
```

## Choosing a variant

- **Primary** — one per view, the action that moves the task forward. Order in
  a row: primary first, flush left. Never two primaries side by side.
- **Secondary** — the alternatives, and cancel.
- **Ghost** — inline with text, or in dense toolbars. It trims its inline
  padding so the label lines up with the copy around it.

Use a `<button>` for actions and an `<a href>` for navigation, even when the two
look the same — that is what decides whether the keyboard activates it with
Space or Enter, and whether it can be opened in a new tab.

## Loading

Rendered server-side, `loading=True` is the whole state: the spinner leads, the
icons stand down, `aria-busy="true"` is set, the cursor turns to `progress` and
the bundled script swallows repeat clicks — from the pointer and from
Enter/Space alike.

To drive it from the page's own script, `drButton.setLoading` pins the width the
button already had before the spinner swaps in, so a row of controls does not
reflow around it:

```django
{% include "components/ui/button/button.html" with label="Submit order" type="submit" button_id="place-order" %}
```

```js
form.addEventListener("submit", function () {
    var button = document.getElementById("place-order");
    drButton.setLoading(button, true);
    button.querySelector(".dr-btn__label").textContent = "Submitting order…";
});
```

The pinned width is a floor, so a shorter loading label never shrinks the
button. Keep the loading label no longer than the idle one — or use `block` —
and it does not move at all.

Prefer an explained error over a disabled button. If a button is disabled, say
why next to it.

## Behaviour

- **Hierarchy.** Variants carry the weight; sizes carry the density. A view has
  one primary.
- **Hover & press.** Hover is a pointer affordance, suppressed on touch. Primary
  steps down the accent ramp; secondary and ghost tint their ground by 7% then
  14–18%.
- **Keyboard.** Enter and Space activate. Focus shows a 2px accent ring at a 2px
  offset, drawn outside the edge so it reads on a solid fill too.
- **Icon-only.** Named by `aria-label` and explained by a `title` tooltip, both
  taken from `label`.
- **Touch.** Small is under the 44px minimum, so on a coarse pointer it carries
  the rest of the target as padding drawn outside its box. The button does not
  change size; only the area that answers a tap does.
- **Reduced motion.** The spinner keeps turning for readers who ask for less
  motion, but in eight steps rather than a smooth sweep — a frozen spinner reads
  as a hung button.

## Theming

Colors, type and spacing come from the design-system custom properties, each
with a fallback baked in, so the component looks right on a page that defines
none of them and follows the theme on a page that does:

| Property | Falls back to |
| --- | --- |
| `--color-text` | `#201e1d` — the secondary label, the hover and press tints |
| `--color-bg` | `#f3f2f2` — the primary label |
| `--color-accent` | `#ec3013` — the primary fill, the ghost label, the focus ring |
| `--color-accent-600` | `#dd2b0f` — primary hover |
| `--color-accent-700` | `#ae1800` — primary pressed |
| `--color-divider` | `rgba(32, 30, 29, .4)` — the secondary edge |
| `--font-heading` | `"Archivo", system-ui, sans-serif` — labels |
| `--font-heading-weight` | `800` |
| `--radius-md` | `0` — the corner |
| `--space-1…3` | the 4px scale — padding |

Set them on `:root` (or on any ancestor) to retheme the component. The design it
was built from sets Archivo; load it, or point `--font-heading` at your own face.

## Measurements

| Property | Small | Medium | Large |
| --- | --- | --- | --- |
| Height | 32px | 36px | 48px |
| Padding (x) | 12px | 14.4px | 20px |
| Padding (y) | 6px | 8px | 12px |
| Ghost padding (x) | 4px | 4px | 8px |
| Label | 13 / 800 | 14 / 800 | 16 / 800 |
| Icon | 16px | 16px | 20px |
| Icon gap | 6px | 6px | 8px |
| Icon only | 32 × 32 | 36 × 36 | 48 × 48 |
| Edge · radius | 1px · 0 | 1px · 0 | 1px · 0 |
| Touch target | 44px | 36px | 48px |

The edge is drawn on every variant, transparent where the variant has none, so
all three measure the same box at a given size.
