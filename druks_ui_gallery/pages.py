from druks import ui

from druks_ui_gallery.workflows import EXAMPLES, Example

# A run that has not reached the gate yet, and what the page says while it has
# not. A start enqueues, so a run is scheduled before it is running.
WORKING = {
    "scheduled": "The run is queued. It starts in a moment.",
    "running": "The run is working. It stops at the gate in a moment.",
}

# How a run's state reads on this gallery's pages.
TONES = {
    "scheduled": "neutral",
    "running": "active",
    "parked": "warning",
    "finished": "success",
    "failed": "danger",
    "cancelled": "neutral",
}


@ui.page("/")
async def overview():
    return ui.Page(
        title="Druks UI",
        description="Every screen here is Python. This app ships no JavaScript.",
        blocks=[
            ui.Markdown(
                markdown=(
                    "An app declares typed `Page` objects in `pages.py`. The shared "
                    "dashboard renders them, resolves navigation and actions, and "
                    "refreshes the regions that follow a subject."
                )
            ),
            ui.Divider(),
            ui.Card(
                title="The live gate",
                description="A durable run stops for a person, and the page shows it.",
                blocks=[
                    ui.Text(
                        text=(
                            "Start the run, watch it park, answer it, and watch the "
                            "controls go away on their own."
                        )
                    )
                ],
                actions=[
                    ui.Link(
                        label="Open the example", page="example", arguments={"example_id": "gate"}
                    )
                ],
            ),
        ],
    )


@overview.child("/about")
async def about():
    """A static child page, which the shell shows as a tab on its parent."""
    return ui.Page(
        title="About this gallery",
        blocks=[
            ui.Markdown(
                markdown=(
                    "This app is the compatibility consumer for Druks UI. It uses only "
                    "the public author surface, and every page it shows is one an app "
                    "could write."
                )
            ),
            ui.Facts(
                title="What to look at",
                facts=[
                    ui.Fact(label="Tabs", value=ui.TextValue(text="This page is one.")),
                    ui.Fact(
                        label="Detail pages",
                        value=ui.TextValue(
                            text="The gate example",
                            link=ui.Link(
                                label="The gate example",
                                page="example",
                                arguments={"example_id": "gate"},
                            ),
                        ),
                    ),
                    ui.Fact(
                        label="Live regions",
                        value=ui.TextValue(text="The decision on the gate example."),
                    ),
                ],
            ),
        ],
    )


@ui.page("/examples")
async def examples():
    return ui.Page(
        title="Examples",
        description="Each one runs for real.",
        blocks=[
            ui.List(
                items=[
                    ui.TextValue(
                        text=label,
                        link=ui.Link(
                            label=label, page="example", arguments={"example_id": example}
                        ),
                    )
                    for example, label in EXAMPLES.items()
                ]
            )
        ],
    )


@ui.page("/examples/{example_id}")
async def example(example_id: str):
    """A parameterized detail page. The shell gives it a link back to the page
    whose path it extends."""
    found = await Example.get_for_subject_id(example_id)
    if not found:
        return ui.Page(
            title="No such example", blocks=[ui.Text(text=f"Nothing is named {example_id!r}.")]
        )
    status = await found.get_status()

    # What the followed region holds right now: the gate while a run waits on
    # it, and the way to start one otherwise.
    decision: list = [
        ui.Text(text="Nothing is waiting on you. Start a run and it will stop here."),
        ui.Action(
            label="Run the example",
            operation="run_example",
            arguments={"example_id": example_id},
            tone="primary",
            refresh="region",
        ),
    ]
    if status.gate and status.run:
        decision = [ui.GateControls(run=status.run)]
    elif status.state in WORKING:
        decision = [
            ui.Text(text=WORKING[status.state]),
            ui.Action(
                label="Stop it",
                operation="stop_example",
                arguments={"example_id": example_id},
                tone="danger",
                confirm="Stop this run?",
                refresh="region",
            ),
        ]

    return ui.Page(
        title=EXAMPLES[example_id],
        description="A durable run that stops for a person.",
        blocks=[
            ui.Section(
                title="Your decision",
                name="decision",
                # The whole trick: this region watches the showcase, so every
                # change to its run rereads the page and replaces the region.
                follows=found,
                blocks=decision,
            ),
            ui.Divider(),
            ui.Timeline(
                title="Runs",
                items=[
                    ui.TimelineItem(
                        at=run.created_at,
                        title=run.label,
                        description=run.failure or "",
                        status=ui.StatusValue(
                            label=run.state, tone=TONES.get(run.state, "neutral")
                        ),
                    )
                    for run in await found.get_timeline()
                ],
            ),
        ],
    )
