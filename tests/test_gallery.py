from datetime import UTC, datetime
from importlib.metadata import entry_points

import pytest
from druks.testing import seed_run

from druks_ui_gallery.app import DruksUiGallery
from druks_ui_gallery.catalog.pages import forms
from druks_ui_gallery.pages import example, overview
from druks_ui_gallery.workflows import EXAMPLES, Example, RunTheGate

# Druks ships its fixtures as a pytest plugin, so installing it is the whole
# wiring: druks_db for a rolled-back session and druks_client for the API.


def installed():
    """This app as Druks itself resolves it — through the entry point, which is
    the whole registration. Nothing here reaches into a Druks internal: this
    gallery consumes only what an app author can."""
    (entry,) = entry_points(group="druks.apps", name="druks_ui_gallery")
    return entry.load()


def test_the_app_loads_from_its_entry_point():
    app = installed()

    assert app is DruksUiGallery
    assert app.frontend_dist() is None, "the gallery ships no JavaScript"
    assert [subject.__name__ for subject in app.subjects()] == ["Example"]


def test_the_pages_make_a_route_table():
    app = installed()

    assert {page.name for page in app.pages()} >= {"overview", "about", "examples", "example"}
    assert [page.label for page in app.navigation_pages()] == ["overview", "examples", "blocks"]
    # A static child is a tab; a parameterized one is a detail page.
    pages = {page.name: page for page in app.pages()}
    assert pages["about"].parent is pages["overview"]
    assert pages["about"].is_static
    assert not pages["example"].is_static


def test_every_action_names_an_operation_the_app_declares():
    app = installed()

    operations = app.operations()

    assert set(operations) >= {"run_example", "stop_example"}
    assert operations["run_example"].method == "POST"


async def test_the_landing_page_links_to_the_example(druks_db):
    page = await overview.function()

    (destinations,) = [block for block in page.blocks if block.block == "cards"]
    (opening,) = [
        control
        for card in destinations.cards
        for control in card.controls
        if control.page == "example"
    ]
    assert opening.arguments == {"example_id": "gate"}


async def test_the_forms_catalog_shows_inline_and_action_field_collection():
    page = await forms.function()

    empty, filled = [block for block in page.blocks if block.block == "form"]
    (results,) = [
        block for block in page.blocks if block.block == "section" and block.name == "results"
    ]
    (field_action,) = page.controls

    assert empty.title == "Every field"
    # The other half of what a field can do: a page that offers something to
    # edit sends the current value back with it.
    assert filled.title == "A form that starts filled in"
    assert all(field.is_required for field in filled.fields)
    assert field_action
    assert field_action.label == "Try the validation error"
    assert [field.name for field in field_action.fields] == ["peer"]
    (result_action,) = results.controls
    assert result_action.refresh == "region"


async def test_the_example_page_offers_a_run_when_nothing_waits(druks_db):
    page = await example.function("gate")

    region = page.blocks[0]
    assert region.name == "decision"
    assert region.follows.subject_type == "example"
    assert region.follows.subject_id == "gate"
    assert [control.operation for control in region.controls] == ["run_example"]


async def test_a_queued_run_reads_as_queued_and_can_be_stopped(druks_db):
    await seed_run(druks_db, kind=RunTheGate.kind, subject=Example(id="gate"), state="scheduled")

    page = await example.function("gate")

    region = page.blocks[0]
    assert "queued" in region.blocks[0].text
    assert [control.operation for control in region.controls] == ["stop_example"]


async def test_a_parked_run_puts_the_gate_in_the_followed_region(druks_db, parked_run):
    page = await example.function("gate")

    region = page.blocks[0]
    assert [block.block for block in region.blocks] == ["gate_controls"]
    assert region.blocks[0].run == parked_run.id


async def test_an_unknown_example_says_so(druks_db):
    page = await example.function("nowhere")

    assert page.title == "No such example"


async def test_the_showcase_is_identity_alone():
    assert await Example.get_for_subject_id("nowhere") is None
    assert [summary.id for summary in await Example.list_summaries(None)] == list(EXAMPLES)


@pytest.fixture
async def parked_run(druks_db):
    run = await seed_run(
        druks_db,
        kind=RunTheGate.kind,
        subject=Example(id="gate"),
        state="parked",
        input_gate="review",
        input_request={"presentation": "in_app", "controls": ["approve"], "questions": []},
    )
    run.input_requested_at = datetime.now(UTC)
    await druks_db.flush()
    return run
