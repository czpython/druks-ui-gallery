from datetime import UTC, datetime, timedelta

from druks import ui

from druks_ui_gallery.catalog.source import declaration

# One made-up sweep, so every page reads as the same agent app rather than as
# unrelated samples.
STARTED = datetime(2026, 8, 29, 9, 14, 2, tzinfo=UTC)
PEERS = ["rack-1", "rack-2", "rack-3"]
SEVERITY = [ui.Option("Low", value="low"), ui.Option("High", value="high")]

DONE = ui.StatusValue("done", tone="success")
WAITING = ui.StatusValue("waiting", tone="warning")
FAILED = ui.StatusValue("failed", tone="danger")
RUNNING = ui.StatusValue("running", tone="active")


@ui.page("/blocks", label="blocks")
async def blocks():
    """Display and layout: the blocks a page is written out of."""
    return ui.Page(
        "Display and layout",
        description="Text, sections, cards, callouts, dividers, empty states, and links.",
        blocks=[
            ui.Text("A paragraph the app wrote."),
            ui.Quote("Words from a person or an external system stay exactly as written."),
            ui.Markdown(
                "Markdown carries **emphasis**, `code`, and lists:\n\n"
                "- the shell renders it\n"
                "- raw HTML is stripped\n"
            ),
            ui.Divider(),
            ui.Section(
                title="A section",
                name="display",
                blocks=[
                    ui.Text("A section groups blocks and can be a live region."),
                    ui.Card(
                        title="rack-1",
                        description="Last answered 4 minutes ago.",
                        blocks=[
                            ui.Text(
                                "A card holds blocks and offers links. Its own link sits on "
                                "its title here, because it has controls too."
                            )
                        ],
                        controls=[ui.Link("Its runs", page="runs")],
                        link=ui.Link("rack-1", page="data"),
                    ),
                ],
            ),
            ui.Callout("Something worth knowing.", tone="info", title="Info"),
            ui.Callout("The sweep finished.", tone="success", title="Success"),
            # A callout's controls are the next step it points at: a link to
            # read more, or an action to try again. This retry really fails.
            ui.Callout(
                "Two peers went stale.",
                tone="warning",
                title="Warning",
                controls=[ui.Link("See the sweep", page="data")],
            ),
            ui.Callout(
                "The provider is unreachable.",
                tone="danger",
                title="Danger",
                controls=[ui.Action(label="Try again", operation="always_fails")],
            ),
            ui.EmptyState(
                "No peers yet",
                description="An empty state stands in for content there is none of.",
                controls=[ui.Link("Read the contract", url="https://docs.druks.ai")],
            ),
            ui.Cards(
                title="The same set, with nothing in it",
                cards=[],
                empty=ui.EmptyState(
                    "No peers yet",
                    description="A set of cards says this itself when it holds none.",
                    controls=[ui.Link("Add a peer", page="forms")],
                ),
            ),
            ui.Link("A link to another page", page="data"),
            declaration(blocks),
        ],
    )


@blocks.child("/data")
async def data(state: str = ""):
    """Values, and every block that shows them. ``state`` has a default, so it
    is a filter: the shell keeps it in the query string and reads the page again
    when it changes."""
    sweep = [(number, DONE if number % 3 else WAITING) for number in range(1, 26)]
    long_sweep = [
        ui.TableRow(
            [
                ui.TextValue(f"rack-{number}"),
                ui.NumberValue(number * 3, unit="ms"),
                status,
                ui.TimeValue(STARTED + timedelta(minutes=number)),
            ],
            # The one thing a row folds away. The rows that answered say all
            # they have to say in their cells, so only the waiting ones carry
            # a sentence.
            detail="" if status is DONE else "No answer inside the 2s window. The sweep moved on.",
        )
        for number, status in sweep
        # An empty filter means any.
        if not state or status.label == state
    ]
    return ui.Page(
        "Data",
        description="One value reads the same way wherever it sits.",
        filters=[
            ui.SelectField(
                name="state",
                label="State",
                options=[
                    ui.Option("Any", value=""),
                    ui.Option("Done", value=DONE.label),
                    ui.Option("Waiting", value=WAITING.label),
                ],
                value=state,
            )
        ],
        blocks=[
            ui.Metrics(
                [
                    ui.Metric("Peers", value=ui.NumberValue(25)),
                    ui.Metric(
                        "Answered",
                        value=ui.NumberValue(17),
                        description="Peers that replied to this sweep.",
                    ),
                    ui.Metric("State", value=RUNNING),
                ],
                title="Operational summary",
            ),
            ui.Metrics(
                [
                    ui.Metric("Neutral", value=ui.NumberValue(8)),
                    ui.Metric("Active", value=ui.NumberValue(4, tone="active")),
                    ui.Metric("Success", value=ui.NumberValue(17, tone="success")),
                    ui.Metric("Warning", value=ui.NumberValue(2, tone="warning")),
                    ui.Metric("Danger", value=ui.NumberValue(1, tone="danger")),
                ],
                title="Number tones",
            ),
            ui.Facts(
                [
                    ui.Fact(
                        "Text",
                        value=ui.TextValue("rack-1", description="The first peer to answer."),
                    ),
                    ui.Fact("Status, plain", value=ui.StatusValue("idle")),
                    ui.Fact(
                        "Text with a link",
                        value=ui.TextValue("its runs", link=ui.Link("runs", page="runs")),
                    ),
                    ui.Fact("Number", value=ui.NumberValue(40.5, unit="ms")),
                    ui.Fact("Status", value=WAITING),
                    ui.Fact(
                        "Status with a link",
                        value=ui.StatusValue(
                            "parked",
                            tone="warning",
                            link=ui.Link(
                                "The live gate", page="example", arguments={"example_id": "gate"}
                            ),
                        ),
                    ),
                    ui.Fact("Time", value=ui.TimeValue(STARTED)),
                    ui.Fact(
                        "Controls",
                        value=ui.ControlsValue([ui.Link("Its runs", page="runs")]),
                    ),
                ],
                title="Every value",
            ),
            ui.Chart(
                kind="bar",
                title="Answers per day",
                categories=["Mon", "Tue", "Wed", "Thu"],
                series=[
                    ui.ChartSeries(label="rack-1", points=[3, 5, 4, 6]),
                    ui.ChartSeries(label="rack-2", points=[1, 2, 2, 3]),
                ],
                category_label="Day",
                value_label="Answers",
            ),
            ui.Chart(
                kind="area",
                title="Peers answering",
                categories=["Mon", "Tue", "Wed", "Thu"],
                series=[ui.ChartSeries(label="answered", points=[12, 17, 15, 21])],
                category_label="Day",
                value_label="Peers",
            ),
            ui.Chart(
                kind="line",
                title="Latency drift",
                categories=["Mon", "Tue", "Wed", "Thu"],
                series=[ui.ChartSeries(label="drift", points=[2, -1, 3, -4])],
                category_label="Day",
                value_label="Milliseconds from the mean",
            ),
            ui.Section(
                title="A table with rows",
                name="table_rows",
                blocks=[
                    ui.Table(
                        title="This sweep",
                        columns=[
                            ui.TableColumn("Peer"),
                            ui.TableColumn("Latency", align="end"),
                            ui.TableColumn("State"),
                            ui.TableColumn("Answered"),
                        ],
                        rows=long_sweep,
                        empty_text="No peers yet.",
                    )
                ],
            ),
            ui.Section(
                title="The same table, empty",
                name="table_empty",
                blocks=[
                    ui.Table(
                        columns=[ui.TableColumn("Peer"), ui.TableColumn("Latency")],
                        rows=[],
                        empty_text="No peers answered this sweep.",
                    )
                ],
            ),
            ui.List([ui.TextValue(peer) for peer in PEERS], title="A list of values"),
            declaration(data),
        ],
    )


@blocks.child("/runs")
async def runs():
    """The blocks that make durable work readable."""
    return ui.Page(
        "Runs and artifacts",
        description="What a durable run looks like on a page.",
        blocks=[
            ui.Timeline(
                [
                    ui.TimelineItem(when=STARTED, title="Run started", status=RUNNING),
                    ui.TimelineItem(
                        when=STARTED + timedelta(minutes=2),
                        title="Swept 25 peers",
                        description="Three did not answer.",
                        status=DONE,
                    ),
                    ui.TimelineItem(
                        when=STARTED + timedelta(minutes=4),
                        title="Waiting on you",
                        status=WAITING,
                    ),
                    ui.TimelineItem(
                        when=STARTED + timedelta(minutes=9),
                        title="Provider refused the retry",
                        description="503 from the peer registry.",
                        status=FAILED,
                    ),
                ],
                title="This sweep",
            ),
            ui.Progress("Sweeping peers", completed=17, total=25),
            ui.Progress("Waiting for the provider"),
            ui.Progress(
                "Stages",
                steps=[
                    ui.ProgressStep(label="read the roster", status=DONE),
                    ui.ProgressStep(label="sweep", status=RUNNING),
                    ui.ProgressStep(label="report", status=WAITING),
                ],
            ),
            ui.Image(
                url="https://docs.druks.ai/assets/logo/web/DruksLogo_White.svg",
                alternative_text="The Druks wordmark.",
                caption="An image says what it shows, or the page shows those words instead.",
            ),
            ui.ImageGallery(
                [
                    ui.Image(
                        url="https://docs.druks.ai/assets/logo/web/DruksLogo_White.svg",
                        alternative_text="The Druks wordmark, again.",
                    ),
                    ui.Image(
                        url="https://example.invalid/missing.png",
                        alternative_text="An image that will not load, so you read this instead.",
                    ),
                ],
                title="A gallery",
            ),
            ui.Text(
                "Files reads from records this gallery does not make, so what you "
                "see is the block with nothing to show. The platform's own story "
                "lives on the subject page the link below opens."
            ),
            ui.Files(title="Files a run produced"),
            ui.Link(
                "Everything druks did about the gate example",
                subject={"subject_type": "example", "subject_id": "gate"},
            ),
            declaration(runs),
        ],
    )


@blocks.child("/layout")
async def layout():
    """Stack and Columns, which hold every other block."""
    return ui.Page(
        "Layout",
        description="Down the page, and across it.",
        blocks=[
            ui.Stack([ui.Text("A medium gap, the one a stack takes by default.")], gap="medium"),
            ui.Stack(
                [
                    ui.Columns(
                        [
                            ui.Card(title="One", blocks=[ui.Text("Each child is a column.")]),
                            ui.Card(title="Two", blocks=[ui.Text("They share the width.")]),
                            ui.Card(title="Three", blocks=[ui.Text("They stack when narrow.")]),
                        ]
                    ),
                    ui.Columns(
                        [
                            ui.Facts(
                                [ui.Fact("Columns", value=ui.TextValue("hold anything"))],
                                title="Nested",
                            ),
                            ui.Stack(
                                [ui.Text("Including"), ui.Text("another stack.")], gap="small"
                            ),
                        ]
                    ),
                    ui.Columns(
                        [
                            ui.Card(
                                title="Main", blocks=[ui.Text("It takes what the rail leaves.")]
                            ),
                            ui.Card(
                                title="Rail",
                                blocks=[ui.Text("A sidebar keeps the last column narrow.")],
                            ),
                        ],
                        layout="sidebar",
                    ),
                ],
                gap="large",
            ),
            declaration(layout),
        ],
    )


@blocks.child("/forms")
async def forms():
    """Every field, and what an action does next."""
    return ui.Page(
        "Forms and actions",
        description="Each button here calls a real route.",
        controls=[
            ui.Action(
                label="Try the validation error",
                operation="needs_a_peer",
                refresh="none",
                fields=[
                    ui.TextField(
                        name="peer",
                        label="Peer",
                        help_text="Leave it empty and the error lands here.",
                    )
                ],
            )
        ],
        blocks=[
            ui.Form(
                action=ui.Action(label="Submit", operation="accept_anything", tone="primary"),
                # A second button that sends the same fields somewhere else.
                extra_actions=[
                    ui.Action(label="Send to the broken route", operation="always_fails")
                ],
                title="Every field",
                description=(
                    "Submit it: the route accepts anything and answers. The second "
                    "button sends the same fields to a route that refuses."
                ),
                fields=[
                    ui.TextField(
                        name="peer",
                        label="Peer",
                        placeholder="rack-1",
                        help_text="One line of text.",
                    ),
                    ui.TextAreaField(
                        name="note",
                        label="Note",
                        rows=3,
                        placeholder="What the sweep found.",
                        help_text="Several lines of text.",
                    ),
                    ui.NumberField(
                        name="budget",
                        label="Budget",
                        minimum=0,
                        maximum=100,
                        step=5,
                        help_text="A number inside a range.",
                    ),
                    ui.SelectField(
                        name="severity",
                        label="Severity",
                        options=SEVERITY,
                        value="low",
                        help_text="One option out of a set.",
                    ),
                    ui.MultiSelectField(
                        name="tags",
                        label="Tags",
                        options=SEVERITY,
                        help_text="Any number of options.",
                    ),
                    ui.RadioField(
                        name="decision",
                        label="Decision",
                        options=SEVERITY,
                        help_text="One option, all of them in view.",
                    ),
                    ui.CheckboxField(
                        name="notify",
                        label="Notify the owner",
                        help_text="One box, on or off.",
                    ),
                    ui.UploadField(
                        name="evidence",
                        label="Evidence",
                        help_text="One file stored by the platform.",
                        accept="image/*,.pdf",
                    ),
                    ui.MultiUploadField(
                        name="photos",
                        label="Photos",
                        help_text="Several files from one dialog, each stored by the platform.",
                        accept="image/*",
                    ),
                    ui.SecretField(
                        name="token",
                        label="Access token",
                        help_text="A secret has no value that a page can read back.",
                    ),
                ],
            ),
            ui.Form(
                action=ui.Action(label="Save", operation="accept_anything", tone="primary"),
                title="A form that starts filled in",
                description=(
                    "Every field here is required. The ones that can carry a starting "
                    "value do, which is how an app offers something to edit rather "
                    "than something to write."
                ),
                fields=[
                    ui.TextField(name="peer", label="Peer", value="rack-1", is_required=True),
                    ui.TextAreaField(
                        name="note",
                        label="Note",
                        rows=3,
                        value="Latency doubled after the replica moved.",
                        is_required=True,
                    ),
                    ui.NumberField(
                        name="budget", label="Budget", value=25, minimum=0, is_required=True
                    ),
                    ui.SelectField(
                        name="severity",
                        label="Severity",
                        options=SEVERITY,
                        value="high",
                        is_required=True,
                    ),
                    ui.MultiSelectField(
                        name="tags",
                        label="Tags",
                        options=SEVERITY,
                        value=["low", "high"],
                        is_required=True,
                    ),
                    ui.RadioField(
                        name="decision",
                        label="Decision",
                        options=SEVERITY,
                        value="low",
                        is_required=True,
                    ),
                    ui.CheckboxField(
                        name="notify", label="Notify the owner", value=True, is_required=True
                    ),
                    # None of these three can start with a value: nothing the
                    # server sends puts a file back into a file input, and a
                    # secret is not readable once it is stored.
                    ui.UploadField(
                        name="evidence", label="Evidence", accept=".csv", is_required=True
                    ),
                    ui.MultiUploadField(name="photos", label="Photos", is_required=True),
                    ui.SecretField(name="token", label="Access token", is_required=True),
                ],
            ),
            ui.Section(
                title="Forms that save as you edit",
                blocks=[
                    ui.Text(
                        "Neither form has a button. A select sends when it changes, and text "
                        "sends when it loses focus."
                    ),
                    # Nothing is stored, so neither refreshes: a reread would put
                    # back what you just changed.
                    ui.Columns(
                        [
                            ui.Form(
                                action=ui.Action(
                                    label="Save the note",
                                    operation="accept_anything",
                                    refresh="none",
                                ),
                                submit="change",
                                layout="prose",
                                fields=[
                                    ui.TextField(
                                        name="title", label="Title", value="Three peers went stale"
                                    ),
                                    ui.TextAreaField(
                                        name="body",
                                        label="Body",
                                        rows=6,
                                        value=(
                                            "Latency **doubled** after the replica moved.\n\n"
                                            "- rack-3\n- rack-7\n- rack-12\n"
                                        ),
                                        # Formatted in place, and sent back as markdown.
                                        markdown=True,
                                    ),
                                ],
                            ),
                            ui.Form(
                                action=ui.Action(
                                    label="Save the peer",
                                    operation="accept_anything",
                                    refresh="none",
                                ),
                                submit="change",
                                layout="row",
                                fields=[
                                    ui.SelectField(
                                        name="peer",
                                        label="Peer",
                                        options=[
                                            ui.Option("rack-1", value="rack-1", group="Frankfurt"),
                                            ui.Option("rack-2", value="rack-2", group="Frankfurt"),
                                            ui.Option("rack-3", value="rack-3", group="Dublin"),
                                        ],
                                        value="rack-1",
                                    )
                                ],
                            ),
                        ],
                        layout="sidebar",
                    ),
                ],
            ),
            ui.Divider(),
            ui.Section(
                title="What an action does next",
                name="results",
                controls=[
                    ui.Action(
                        label="Refresh this section",
                        operation="accept_anything",
                        refresh="region",
                    )
                ],
                blocks=[
                    ui.Text("Every button below calls a route and shows you the answer."),
                    ui.Card(
                        title="Confirmation and a destructive tone",
                        blocks=[ui.Text("It asks before it sends anything.")],
                        controls=[
                            ui.Action(
                                label="Delete the sweep",
                                operation="accept_anything",
                                # What the action already knows. The shell sends
                                # these whether or not it asks for anything else.
                                arguments={"sweep_id": 7},
                                tone="danger",
                                confirm="Delete this sweep? Nothing is really deleted here.",
                                refresh="region",
                            )
                        ],
                    ),
                    ui.Card(
                        title="A failure",
                        blocks=[ui.Text("The route refuses, and the page says so.")],
                        controls=[
                            ui.Action(label="Call the broken route", operation="always_fails")
                        ],
                    ),
                    ui.Card(
                        title="Refresh, and navigation",
                        blocks=[ui.Text("One rereads this region; the other leaves the page.")],
                        controls=[
                            ui.Action(
                                label="Go to the overview",
                                operation="accept_anything",
                                refresh="none",
                                link=ui.Link("Overview", page="overview"),
                            ),
                            ui.Action(
                                label="Refresh the whole page",
                                operation="accept_anything",
                                refresh="page",
                            ),
                            ui.Link("A link, which calls nothing", page="overview"),
                        ],
                    ),
                ],
            ),
            ui.Section(
                title="Acting on rows",
                name="stale_peers",
                blocks=[
                    ui.Text(
                        "Tick rows and retire them together, or retire one from its own row. "
                        "The route answers with the peers it got. Nothing is stored, so the "
                        "rows stay."
                    ),
                    ui.Table(
                        title="Stale peers",
                        columns=[
                            ui.TableColumn("Peer"),
                            ui.TableColumn("State"),
                            ui.TableColumn("Actions"),
                        ],
                        rows=[
                            ui.TableRow(
                                [
                                    ui.TextValue(peer),
                                    WAITING,
                                    ui.ControlsValue(
                                        [
                                            ui.Action(
                                                label="Retire",
                                                operation="retire_peers",
                                                arguments={"peers": [peer]},
                                                refresh="region",
                                            )
                                        ]
                                    ),
                                ],
                                # What the shell sends for this row when it is ticked.
                                key=peer,
                            )
                            for peer in PEERS
                        ],
                        # The ticked keys arrive as one list under this name.
                        select="peers",
                        actions=[
                            ui.Action(
                                label="Retire the selected",
                                operation="retire_peers",
                                tone="danger",
                                confirm="Retire these peers? Nothing is really retired here.",
                                refresh="region",
                            )
                        ],
                    ),
                ],
            ),
            ui.Section(
                title="Drag and drop",
                name="board",
                blocks=[
                    ui.Text(
                        "Drag a card onto the other list. The drop sends the card's peer and "
                        "the list's state to a route. Nothing is stored, so the card goes back."
                    ),
                    ui.Columns(
                        [
                            ui.Cards(
                                title="Waiting",
                                layout="stack",
                                cards=[ui.Card(title="rack-3", drag={"peer": "rack-3"})],
                                # The drop is the submit, so it collects nothing
                                # and asks nothing first.
                                drop=ui.Action(
                                    label="Move to waiting",
                                    operation="move_peer",
                                    arguments={"state": "waiting"},
                                    refresh="region",
                                ),
                            ),
                            ui.Cards(
                                title="Done",
                                layout="stack",
                                cards=[
                                    ui.Card(title="rack-1", drag={"peer": "rack-1"}),
                                    ui.Card(title="rack-2", drag={"peer": "rack-2"}),
                                ],
                                drop=ui.Action(
                                    label="Move to done",
                                    operation="move_peer",
                                    arguments={"state": "done"},
                                    refresh="region",
                                ),
                            ),
                        ]
                    ),
                ],
            ),
            declaration(forms),
        ],
    )
