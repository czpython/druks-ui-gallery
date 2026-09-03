from datetime import UTC, datetime
from importlib.metadata import entry_points
from typing import Literal, get_args, get_origin

import pytest
from druks.testing import seed_run
from druks.ui import Block, Field, Page, Value
from pydantic import BaseModel

from druks_ui_gallery.catalog.pages import data, forms
from druks_ui_gallery.catalog.source import HEADING
from druks_ui_gallery.pages import example
from druks_ui_gallery.workflows import Example, RunTheGate

# What the contract carries. A block, value, or field that Druks adds without an
# example here fails this suite: the gallery is the reference, so an empty spot
# in it is a gap in the reference.
BLOCKS = {member.model_fields["block"].default for member in Block.__args__[0].__args__}
VALUES = {member.model_fields["value"].default for member in Value.__args__[0].__args__}
FIELDS = {member.model_fields["field"].default for member in Field.__args__[0].__args__}


# The attributes the gallery cannot show, and why. One that leaves this list
# needs an example; one that joins it needs a reason. Anything else failing is
# a hole in the reference.
WITHOUT_AN_EXAMPLE = [
    # Files reads records this gallery never makes, so the block renders with
    # nothing in it and no FileSummary is ever built. The page says so, and
    # links to the platform's own story where real files are.
    "FileSummary.contentType",
    "FileSummary.id",
    "FileSummary.name",
    "FileSummary.size",
    "Files.files",
    # The showcase follows its subject on a Section, not on the Page: the point
    # of it is that one region is replaced while the rest of the page stays
    # put. A page-level follow here would say the opposite.
    "Page.follows",
]


# Every enumeration the contract offers, found rather than listed: a Literal on
# any public model reachable from a block, a value, or a field. A variant with
# no example is a hole in the reference just as much as a block with none.
def public_models() -> list[type[BaseModel]]:
    found: list[type[BaseModel]] = []
    queue = [Page]
    queue += [member for union in (Block, Value, Field) for member in union.__args__[0].__args__]
    while queue:
        model = queue.pop()
        if model in found:
            continue
        found.append(model)
        for info in model.model_fields.values():
            queue += [one for one in nested(info.annotation) if one not in found]
    return found


def nested(annotation) -> list[type[BaseModel]]:
    """Every model an annotation can hold, however it is wrapped."""
    if isinstance(annotation, type) and issubclass_safe(annotation, BaseModel):
        return [annotation]
    return [one for argument in get_args(annotation) for one in nested(argument)]


def issubclass_safe(annotation, of) -> bool:
    try:
        return issubclass(annotation, of)
    except TypeError:
        return False


def literals(annotation) -> set:
    """What a Literal allows, however deep it sits in the annotation."""
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    return set().union(set(), *(literals(one) for one in get_args(annotation)))


def variants() -> list[tuple[type[BaseModel], str, set]]:
    """Each public model, its Literal field, and what that field allows. The
    discriminators are left out: their own test covers those."""
    found = []
    for model in public_models():
        discriminator_field, _ = discriminator_of(model)
        for name, info in model.model_fields.items():
            if name == discriminator_field:
                continue
            options = literals(info.annotation)
            if options:
                found.append((model, name, options))
    return found


def wire_keys(model: type[BaseModel]) -> set[str]:
    return {info.alias or name for name, info in model.model_fields.items()}


def discriminator_of(model: type[BaseModel]) -> tuple[str, str]:
    """The key that names this model on the wire, and what it holds. A model can
    carry a field called ``value`` that holds a datum rather than a name — a
    Metric, a Fact, an Option — so the Literal is what settles it."""
    for key in ("block", "value", "field"):
        info = model.model_fields.get(key)
        if info is not None and get_origin(info.annotation) is Literal:
            return key, info.default
    return "", ""


def nodes_of(pages: list[dict], model: type[BaseModel]) -> list[dict]:
    """Every node the gallery rendered for one model. A node counts only when it
    carries that model's own keys, and its discriminator too."""
    discriminator_field, discriminator = discriminator_of(model)
    keys = wire_keys(model)
    found = []
    for page in pages:
        for node in every(page):
            if set(node) != keys:
                continue
            if discriminator and node.get(discriminator_field) != discriminator:
                continue
            found.append(node)
    return found


def chosen(pages: list[dict], model: type[BaseModel], field: str) -> set:
    """What the gallery actually rendered for one model's field."""
    return {node[field] for node in nodes_of(pages, model)}


def default_for(model: type[BaseModel], field: str) -> object:
    """What the wire carries when the app leaves a field alone. A field that
    renders its default everywhere has no example, however it serializes —
    ``minimum=0`` is set, and an empty string is not."""
    (info,) = [one for name, one in model.model_fields.items() if (one.alias or name) == field]
    return info.get_default(call_default_factory=True)


def settable(model: type[BaseModel]) -> list[str]:
    """Every wire key an app writes on a model. The discriminator is left out:
    it is the model's name on the wire, not something an app sets."""
    discriminator_field, _ = discriminator_of(model)
    return [
        info.alias or name
        for name, info in model.model_fields.items()
        if name != discriminator_field
    ]


def every(node) -> list[dict]:
    """Every object in a serialized page — a block, a value, a field, a row."""
    if isinstance(node, dict):
        return [node, *(one for value in node.values() for one in every(value))]
    if isinstance(node, list):
        return [one for value in node for one in every(value)]
    return []


def installed():
    (entry,) = entry_points(group="druks.apps", name="druks_ui_gallery")
    return entry.load()


def named(node, key: str) -> set[str]:
    """Every discriminator of one kind anywhere in a serialized page."""
    if isinstance(node, dict):
        found = {node[key]} if isinstance(node.get(key), str) else set()
        for value in node.values():
            found |= named(value, key)
        return found
    if isinstance(node, list):
        return set().union(*(named(one, key) for one in node)) if node else set()
    return set()


async def rendered(druks_db) -> list[dict]:
    """Every page this gallery declares, as the wire carries it."""
    pages = []
    for declared in installed().pages():
        arguments = {"example_id": "gate"} if declared.name == "example" else {}
        page = await declared.function(**arguments)
        pages.append(page.model_dump(by_alias=True, mode="json"))
    return pages


@pytest.fixture
async def parked(druks_db):
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


async def test_every_block_has_an_example(druks_db, parked):
    shown = set().union(*(named(page, "block") for page in await rendered(druks_db)))

    assert BLOCKS - shown == set(), "these blocks have no gallery example"


async def test_every_value_has_an_example(druks_db, parked):
    shown = set().union(*(named(page, "value") for page in await rendered(druks_db)))

    assert VALUES - shown == set(), "these values have no gallery example"


async def test_every_field_has_an_example(druks_db, parked):
    shown = set().union(*(named(page, "field") for page in await rendered(druks_db)))

    assert FIELDS - shown == set(), "these fields have no gallery example"


async def test_every_attribute_has_an_example(druks_db, parked):
    """Every attribute a model carries, not just every model. The tests above
    catch a whole new block, value, or field; this catches a new attribute on
    one that is already here, which is how most of the contract grows —
    ``Action.fields`` and ``Page.controls`` both arrived that way."""
    pages = await rendered(druks_db)

    missing = sorted(
        f"{model.__name__}.{field}"
        for model in public_models()
        for field in settable(model)
        if not any(node[field] != default_for(model, field) for node in nodes_of(pages, model))
    )

    assert missing == WITHOUT_AN_EXAMPLE, "these attributes have no gallery example"


@pytest.mark.parametrize(
    "model, field, options", variants(), ids=lambda one: getattr(one, "__name__", str(one))
)
async def test_every_variant_has_an_example(druks_db, parked, model, field, options):
    pages = await rendered(druks_db)

    missing = options - chosen(pages, model, field)

    assert missing == set(), f"{model.__name__}.{field} variants with no example"


async def test_every_action_names_an_operation_the_app_declares(druks_db, parked):
    operations = installed().operations()

    for page in await rendered(druks_db):
        for action in actions_in(page):
            assert action["operation"] in operations, action


def actions_in(node) -> list[dict]:
    if isinstance(node, dict):
        found = [node] if node.get("block") == "action" else []
        for value in node.values():
            found += actions_in(value)
        return found
    if isinstance(node, list):
        return [one for value in node for one in actions_in(value)]
    return []


async def test_every_catalog_page_shows_its_own_declaration(druks_db):
    for declared in installed().pages():
        if not declared.module.endswith("catalog.pages"):
            continue
        page = await declared.function()
        (last,) = [block for block in page.blocks if block.block == "markdown"][-1:]
        assert HEADING in last.text
        assert f"async def {declared.name}(" in last.text


async def test_an_action_can_be_confirmed_refreshed_and_navigated(druks_db):
    page = await forms.function()

    shown = actions_in(page.model_dump(by_alias=True, mode="json"))
    assert any(action["confirm"] for action in shown), "no action asks first"
    assert any(action["tone"] == "danger" for action in shown), "no destructive action"
    assert any(action["refresh"] == "region" for action in shown), "no region refresh"
    assert any(action["link"] for action in shown), "no action navigates"
    assert any(action["operation"] == "always_fails" for action in shown), "no failure to see"
    # The validation error has to reach a field, so the action collects the
    # field that the route names back.
    (validating,) = [one for one in shown if one["operation"] == "needs_a_peer"]
    assert [field["name"] for field in validating["fields"]] == ["peer"]


async def test_a_table_shows_both_its_states(druks_db):
    page = (await data.function()).model_dump(by_alias=True, mode="json")

    tables = [one for one in every(page) if one.get("block") == "table"]
    assert [bool(table["rows"]) for table in tables] == [True, False]
    assert len(tables[0]["rows"]) > 20, "no long-content example"


async def test_the_parked_example_shows_the_gate(druks_db, parked):
    page = await example.function("gate")

    assert [block.block for block in page.blocks[0].blocks] == ["gate_controls"]
