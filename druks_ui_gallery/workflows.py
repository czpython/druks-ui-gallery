from druks.workflows import Subject, SubjectSummary, Workflow, step
from pydantic import BaseModel


class ExampleOption(BaseModel):
    """One answer the gate offers. It is the ask's own contract, not a stored
    shape, so it lives beside the workflow that asks."""

    id: str
    label: str
    recommended: bool = False


class ExampleQuestion(BaseModel):
    id: str
    prompt: str
    options: list[ExampleOption]


# Every example this gallery runs. The id is the whole record: a showcase keeps
# no row, so the subject is identity alone.
EXAMPLES = {
    "gate": "The live gate",
}


class Example(Subject):
    """What a gallery run is about. Identity only — Druks needs nothing more,
    and a reference app should not need a table to prove a page renders."""

    @classmethod
    async def get_for_subject_id(cls, subject_id: str) -> "Example | None":
        if subject_id in EXAMPLES:
            return cls(id=subject_id)
        return

    def get_summary(self) -> SubjectSummary:
        return SubjectSummary(id=self.id, label=EXAMPLES[self.id])

    @classmethod
    async def list_summaries(cls, account_id: str | None) -> list[SubjectSummary]:
        return [cls(id=example).get_summary() for example in EXAMPLES]


class RunTheGate(Workflow):
    """The example the gallery exists to show: a durable run that stops and
    waits for a person, then carries their answer forward."""

    subject = Example

    async def run_multistep(self) -> None:
        await self.look()
        reply = await self.review(
            questions=[
                ExampleQuestion(
                    id="scope",
                    prompt="The sweep found three stale peers. Retire them?",
                    options=[
                        ExampleOption(id="all", label="Retire all three", recommended=True),
                        ExampleOption(id="oldest", label="Retire the oldest only"),
                    ],
                )
            ],
            context="This gate is the whole point of the gallery: the run below is "
            "parked, and it stays parked until you answer — through a restart, or "
            "for a week.",
        )
        # Body-level, not a step: an announcement is its own checkpoint.
        await self.announce("answered", action=reply.action, note=reply.note)

    @step
    async def look(self) -> None:
        """A durable checkpoint before the gate, so the run has history to show."""

    @classmethod
    async def dispatch(cls, *, example: Example) -> str:
        return await cls.start(subject=example)
