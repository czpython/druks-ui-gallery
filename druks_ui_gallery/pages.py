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
        "Druks UI",
        description="Every screen here is Python. This app ships no JavaScript.",
        blocks=[
            ui.Markdown(
                "An app declares typed `Page` objects in `pages.py`. The shared "
                "dashboard renders them, resolves navigation and actions, and "
                "refreshes the regions that follow a subject."
            ),
            ui.Divider(),
            ui.Card(
                title="The live gate",
                description="A durable run stops for a person, and the page shows it.",
                blocks=[
                    ui.Text(
                        "Start the run, watch it park, answer it, and watch the "
                        "controls go away on their own."
                    )
                ],
                actions=[
                    ui.Link("Open the example", page="example", arguments={"example_id": "gate"})
                ],
            ),
            ui.Card(
                title="The whole catalog",
                description="Every block, value, and field the contract carries.",
                blocks=[ui.Text("Each page ends with the Python that produced it.")],
                actions=[ui.Link("Open the catalog", page="blocks")],
            ),
        ],
    )


@overview.child("/about")
async def about():
    """A static child page, which the shell shows as a tab on its parent."""
    return ui.Page(
        "About this gallery",
        blocks=[
            ui.Markdown(
                "This app is the compatibility consumer for Druks UI. It uses only "
                "the public author surface, and every page it shows is one an app "
                "could write."
            ),
            ui.Facts(
                [
                    ui.Fact("Tabs", value=ui.TextValue("This page is one.")),
                    ui.Fact(
                        "Detail pages",
                        value=ui.TextValue(
                            "The gate example",
                            link=ui.Link(
                                "The gate example", page="example", arguments={"example_id": "gate"}
                            ),
                        ),
                    ),
                    ui.Fact(
                        "Live regions", value=ui.TextValue("The decision on the gate example.")
                    ),
                ],
                title="What to look at",
            ),
            ui.Markdown(
                "### What to try on the catalog pages\n\n"
                "The shell owns theme, spacing, and accessibility, so these are "
                "things to look at rather than things this app does:\n\n"
                "- **Narrow the window.** The table keeps its headers and scrolls "
                "sideways; columns become rows; the tab strip scrolls.\n"
                "- **Switch your system to light or dark.** Every block follows it; "
                "no page carries a colour of its own.\n"
                "- **Press Tab.** Every link, button, and field takes focus in the "
                "order it is read, and shows where it is.\n"
                "- **Turn a screen reader on.** A chart reads as a table of the same "
                "numbers, progress reads as words, and each image reads as what it "
                "shows.\n"
            ),
        ],
    )


@ui.page("/examples")
async def examples():
    return ui.Page(
        "Examples",
        description="Each one runs for real.",
        blocks=[
            ui.List(
                [
                    ui.TextValue(
                        label,
                        link=ui.Link(label, page="example", arguments={"example_id": example}),
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
        return ui.Page("No such example", blocks=[ui.Text(f"Nothing is named {example_id!r}.")])
    status = await found.get_status()

    if status.gate:
        decision = [ui.GateControls(status.run)]
    elif status.run and status.state in WORKING:
        decision = [
            ui.Text(WORKING[status.state]),
            ui.Action(
                label="Stop it",
                operation="stop_example",
                arguments={"example_id": example_id},
                tone="danger",
                confirm="Stop this run?",
                refresh="region",
            ),
        ]
    else:
        decision = [
            ui.Text("Nothing is waiting on you. Start a run and it will stop here."),
            ui.Action(
                label="Run the example",
                operation="run_example",
                arguments={"example_id": example_id},
                tone="primary",
                refresh="region",
            ),
        ]

    return ui.Page(
        EXAMPLES[example_id],
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
                [
                    ui.TimelineItem(
                        when=run.created_at,
                        title=run.label,
                        description=run.failure or "",
                        status=ui.StatusValue(run.state, tone=TONES.get(run.state, "neutral")),
                    )
                    for run in await found.get_timeline()
                ],
                title="Runs",
            ),
        ],
    )
