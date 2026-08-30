from fastapi import APIRouter, HTTPException, status

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
