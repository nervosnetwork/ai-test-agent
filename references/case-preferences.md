# Project Case preferences

Which Cases are worth designing is the project's decision, not this skill's. The project states it in
root `AGENTS.md` under `## Case preferences` (用例偏好): for example the test layer, how a Case must be
set up and observed, what not to generate, and cost limits. Read that section before any design and
treat it as binding, ahead of this skill's defaults and of whatever the diff suggests.

## Apply the preferences as an admission gate

- A leaf becomes a Case only if it satisfies every stated preference. Check before writing the row,
  not after: effort spent on Cases the project will not keep is wasted.
- A leaf that fails is not a Case. Keep it visible once: one line under 导读 “测不到的” and a tree
  leaf `[not_applicable] — 不符合用例偏好：<reason>`. Do not redesign it in a form the preferences
  exclude, such as another layer, a test-only hook or a patched build.
- Say in 导读 what the preferences let you reach: which changed behavior is testable under them, by
  which route, and which is not. A diff shows what changed, not what this project tests.
- Preferences decide which Cases enter the table. They do not limit how deeply the change is
  analysed, and they never relax expectations, provenance or the two gates.

## When the project states none

Do not invent a preference. Design from observable behavior as before, state the layer you assumed
in 导读, and ask under 需要你决定 whether to record it in `AGENTS.md`. When a human corrects the kind of
Case you produced (“not this layer”, “no unit-level points”), propose the wording for
`## Case preferences` so the same correction is not needed twice.
