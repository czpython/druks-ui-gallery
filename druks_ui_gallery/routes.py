from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, status

from druks_ui_gallery.workflows import EXAMPLES, Example, RunTheGate

# Every router here mounts under /api/druks_ui_gallery. An Action names one of
# these by its operation_id; the dashboard resolves it to a method and a URL.
router = APIRouter(prefix="/examples")


@router.post("/{example_id}/runs", status_code=status.HTTP_201_CREATED, operation_id="run_example")
async def run_example(example_id: str) -> dict[str, str]:
    """Start the example's durable run. The page that follows this showcase
    picks the run up on its next snapshot."""
    if example_id not in EXAMPLES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No example {example_id!r}.")
    return {"run": await RunTheGate.dispatch(example=Example(id=example_id))}


@router.post("/{example_id}/runs/cancelled", operation_id="stop_example")
async def stop_example(example_id: str) -> dict[str, str]:
    """Stop whatever is running, so the example can be run again from the top."""
    await RunTheGate.cancel(Example(id=example_id))
    return {"result": "stopped"}


# The catalog's own routes. Each one exists so a button on the forms page calls
# something real: an action that shows a failure has to have a failure to show.
demos = APIRouter(prefix="/demo")


@demos.post("/anything", operation_id="accept_anything")
async def accept_anything() -> dict[str, str]:
    """Takes whatever the form sends and answers. The page does the rest."""
    return {"result": "accepted"}


@demos.post("/peers", operation_id="needs_a_peer")
async def needs_a_peer(peer: Annotated[str, Body(embed=True, min_length=1)]) -> dict[str, str]:
    """Requires a peer, so an action that sends none shows a validation error on
    the field it belongs to."""
    return {"peer": peer}


@demos.post("/broken", operation_id="always_fails")
async def always_fails() -> dict[str, str]:
    """Refuses, so a page can show what a failure reads like."""
    raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "The peer registry is unreachable.")
