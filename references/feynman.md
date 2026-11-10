# Feynman mode (费曼模式)

Trigger: the user says `费曼模式：<PR or topic>` or "Feynman mode", or asks to understand a PR before
testing it. The user explains and you find the gaps. This is a conversation, not a deliverable: write
no review document, Case or file, call no B reviewer, open no gate, and approve nothing.

1. Read the PR description, linked issue, the author's tests and the diff. Do not explain yet.
2. List the 3–5 concepts needed to test this PR in dependency order, names only. Choose them for the
   project's Case preferences (`case-preferences.md`): what its tests can set up and observe, not
   internals it will never exercise.
3. Take one concept at a time and ask one question. The user answers in their own words, as if
   briefing a colleague new to the project.
4. Say what was right, wrong, vague or skipped. Do not give the full answer first: use one follow-up
   question or a concrete scenario so the user closes the gap. After two failed attempts, explain in
   at most three sentences and ask the user to restate it.
5. When the concepts are done, ask for three sentences: what was wrong before, what the PR changes,
   and what an outside observer now sees. Correct only what is wrong.
6. Close with a short list: explained well, still unclear, and for each unclear item the document or
   code location to read next.

Keep every turn short and in the user's language: one question per turn, plain words, no lecture.
Mark what you infer from code rather than from a stated requirement, and say when nothing was run.
A doubt about the PR that surfaces here is a question for its developers, not a Case. When the user
later asks for test design, follow the normal route; their confirmed three sentences are a draft for
导读, still subject to both gates.
