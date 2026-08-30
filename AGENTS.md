# AGENTS.md

`druks-ui-gallery` is a Druks app. It exists to show what Druks UI can render
and to prove the contract from outside the platform's own repository.

## Read map

- The contract this app consumes:
  https://github.com/czpython/druks/blob/main/docs/druks-ui.md.
- How an app is put together:
  https://github.com/czpython/druks/blob/main/docs/writing-an-app.md.

## Contracts

- Screens are Python. This app writes no JavaScript, ships no `dist/`, and has
  no Node project. A change that adds any of those is wrong here.
- Use only the public author surface: `druks.ui`, `druks.apps`,
  `druks.workflows`, and the other concern namespaces the author guide lists.
  Never `druks.durable` or another internal module.
- A page function is a pure read. Druks reruns it on load, on an event, on a
  reconnect, and on a retry, so it must never write, start work, publish an
  event, answer a gate, or depend on process state. An operator starts work
  through an `Action`.
- Every example runs for real. This app shows no mock-up of a block it cannot
  actually produce.

## Verify

```bash
uv sync
uv run ruff check .
uv run pytest
```
