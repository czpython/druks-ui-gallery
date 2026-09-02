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
                        blocks=[ui.Text("A card holds blocks and offers links.")],
                        controls=[ui.Link("Its runs", page="runs")],
                    ),
                ],
            ),
            ui.Callout("Something worth knowing.", tone="info", title="Info"),
            ui.Callout("The sweep finished.", tone="success", title="Success"),
            ui.Callout("Two peers went stale.", tone="warning", title="Warning"),
            ui.Callout("The provider is unreachable.", tone="danger", title="Danger"),
            ui.EmptyState(
                "No peers yet",
                description="An empty state stands in for content there is none of.",
                controls=[ui.Link("Read the contract", url="https://docs.druks.ai")],
            ),
            ui.Link("A link to another page", page="data"),
            declaration(blocks),
        ],
    )


@blocks.child("/data")
async def data():
    """Values, and every block that shows them."""
    long_sweep = [
        ui.TableRow(
            [
                ui.TextValue(f"rack-{number}"),
                ui.NumberValue(number * 3, unit="ms"),
                DONE if number % 3 else WAITING,
                ui.TimeValue(STARTED + timedelta(minutes=number)),
            ]
        )
        for number in range(1, 26)
    ]
    return ui.Page(
        "Data",
        description="One value reads the same way wherever it sits.",
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
                    ui.Fact("Text", value=ui.TextValue("rack-1")),
                    ui.Fact("Status, plain", value=ui.StatusValue("idle")),
                    ui.Fact(
                        "Text with a link",
                        value=ui.TextValue("its runs", link=ui.Link("runs", page="runs")),
                    ),
                    ui.Fact("Number", value=ui.NumberValue(40.5, unit="ms")),
                    ui.Fact("Status", value=WAITING),
                    ui.Fact("Time", value=ui.TimeValue(STARTED)),
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
                title="Every field",
                description="Submit it: the route accepts anything and answers.",
                fields=[
                    ui.TextField(
                        name="peer",
                        label="Peer",
                        placeholder="rack-1",
                        help_text="One line of text.",
                    ),
                    ui.TextAreaField(name="note", label="Note", rows=3),
                    ui.NumberField(name="budget", label="Budget", minimum=0, maximum=100, step=5),
                    ui.SelectField(
                        name="severity", label="Severity", options=SEVERITY, value="low"
                    ),
                    ui.MultiSelectField(name="tags", label="Tags", options=SEVERITY),
                    ui.RadioField(name="decision", label="Decision", options=SEVERITY),
                    ui.CheckboxField(name="notify", label="Notify the owner"),
                    ui.UploadField(
                        name="evidence",
                        label="Evidence",
                        help_text="One file stored by the platform.",
                        accept="image/*,.pdf",
                    ),
                    ui.SecretField(
                        name="token",
                        label="Access token",
                        help_text="A secret has no value that a page can read back.",
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
            declaration(forms),
        ],
    )
