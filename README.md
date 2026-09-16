# druks-ui-gallery

Every screen in this app is Python. It ships no JavaScript, no `dist/`, and no
Node project — the [Druks](https://github.com/czpython/druks) dashboard renders
what its `pages.py` declares.

The gallery is the visual and compatibility reference for Druks UI. It uses
only the public author surface, so anything it shows, your app can write.

## Install it

The app registers itself when you install it into a Druks environment:

```bash
uv pip install -e /path/to/druks-ui-gallery
```

Restart Druks. The gallery appears in the Apps sidebar.

## See the live gate

Open the gallery, then **examples → The live gate**, and press **Run the
example**:

1. A durable workflow starts.
2. It parks on a typed gate and waits for a person.
3. The region that follows the showcase reads the parked request and shows the
   controls.
4. You answer. The answer echoes the run's `parkedAt`, so it names the exact
   question.
5. The workflow resumes.
6. The region refreshes and the controls go away.

Nothing on that page is app JavaScript. The region follows the subject through
the read side every app already has, and the dashboard does the rest.

The parked run also waits on the Dashboard. Its **Review** opens this same page,
because the page declares itself the decision page for its subject:

```python
@ui.page("/examples/{example_id}", subject=Example)
```

The same page shows the other page shapes: a landing page with navigation, a
static child that renders as a tab, and a parameterized detail page with the
link back to the page it hangs under.

## See the whole catalog

**blocks** holds one of everything the contract carries, in five tabs:

| Tab | What it shows |
| --- | --- |
| Display and layout | Text, Markdown, sections, cards and a card's own link, every callout tone, dividers, empty states, links |
| Data | Metrics, Facts, three charts, a long table with a page filter and the same table empty, a list, and every value |
| Runs and artifacts | Timeline, all three shapes of Progress, images, a gallery, files, a link to the platform's own story |
| Layout | Stack and Columns, nested, and a sidebar |
| Forms and actions | Every field, forms that save as you edit, drag and drop, page and section controls, confirmation, refresh, navigation, and errors |

Every one of those pages ends with the Python that produced it. Every button
calls a real route, so the failure states are real failures.

A test fails when a block, value, or field in the contract has no example here.
The gallery is the reference, so an empty spot in it is a gap in the reference.

## Work on it

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

The tests need the Druks test database, the same one the platform's own suite
uses.

## Supported Druks

This gallery installs released Druks from PyPI: `druks>=0.6.0`.

- The contract this app consumes:
  [docs/druks-ui.md](https://github.com/czpython/druks/blob/main/docs/druks-ui.md)
- How to write an app of your own:
  [docs/writing-an-app.md](https://github.com/czpython/druks/blob/main/docs/writing-an-app.md)
