# Extensions (optional)

The core kit is four stages + four gates. These extensions are **opt-in**; add one only when you
hit the problem it solves. Don't start here.

| Extension | Add it when… | What it gives you |
|-----------|--------------|-------------------|
| [`dual-track-governance.md`](./dual-track-governance.md) | more than a couple of people edit the kit itself | separates "change the product" from "change the kit" so they stop polluting each other |
| [`pipeline-driver/`](./pipeline-driver/SKILL.md) | you want one command to drive ①→④ end-to-end with the red lines enforced | a thin orchestrator that *calls* the four skills, never reimplements them |

Both follow invariant #4 (composition over duplication): they wire existing pieces together, they
do not add a second copy of any logic.
