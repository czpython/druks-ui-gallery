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

Restart Druks. The gallery appears in the app switcher.

The V1 UI contract is not on PyPI yet, so the gallery takes Druks from `main`
until the release that carries it. Install it into an environment running that
Druks, not the published 0.4.0.

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

The same page shows the other page shapes: a landing page with navigation, a
static child that renders as a tab, and a parameterized detail page with the
link back to the page it hangs under.

## See the whole catalog

**blocks** holds one of everything the contract carries, in four tabs:

| Tab | What it shows |
| --- | --- |
| Display and layout | Text, Markdown, sections, cards, every callout tone, dividers, empty states, links |
| Data | Metrics, Facts, two charts, a long table and the same table empty, a list, and every value |
| Runs and artifacts | Timeline, all three shapes of Progress, images, a gallery, files, a link to the platform's own story |
| Layout | Stack and Columns, nested |
| Forms and actions | Every field, and buttons that confirm, refresh a region, navigate, fail, and fail validation |

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

This gallery tracks Druks `>=0.4.0` from `main`, until the release that carries
the V1 UI contract.

- The contract this app consumes:
  [docs/druks-ui.md](https://github.com/czpython/druks/blob/main/docs/druks-ui.md)
- How to write an app of your own:
  [docs/writing-an-app.md](https://github.com/czpython/druks/blob/main/docs/writing-an-app.md)
