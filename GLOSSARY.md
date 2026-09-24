# Glossary

Governed definitions for the SIBurst working vocabulary.

These definitions reduce ambiguity inside this project. They do not describe
academic consensus. Where a term has several established meanings outside the
project, this glossary says so and states which meaning SIBurst uses. Canonical
definitions of **SI**, **Burst**, and **SIBurst** live in `NAME_ARCHITECTURE.md`
and are not repeated here.

---

### Capability

What a system can reliably do, under stated conditions.
Within the SIBurst framework, capability is always qualified by *reliability*
and *conditions*: a behavior observed occasionally, or only under narrow
conditions, is not yet counted as capability. Outside the project, the word is
used more loosely, including for demonstrated-once or best-case behavior.

### Capability accumulation

The incremental growth of capability through many small changes, during which
a quantitative description ("the same, but better") remains adequate.
Within the SIBurst framework, accumulation is the first stage of the thesis
structure and the precondition for any threshold.

### Threshold

A condition under which further accumulation stops producing proportionate,
same-kind effects.
Within the SIBurst framework, a threshold is identified by a change in which
description is adequate, not by a particular numerical value. The framework
does not claim that every capability trajectory contains a threshold.

### Discontinuity

The point at which a previous description of a system's situation fails and a
different one is required.
Within the SIBurst framework, discontinuity refers to a change of rules or
regime. It may appear as a step or be recognized only in retrospect across an
apparently smooth curve. In mathematics the word has a narrower technical
meaning; SIBurst does not use it in that strict sense.

### Operating regime

The set of conditions under which a system characteristically functions: what
it is trusted to do, what it acts upon, what it depends on, and what governs it.
Within the SIBurst framework, two systems with similar benchmark results may
occupy different operating regimes, and one system may change regime without a
dramatic change in any single measure.

### Phase change

In physics, a change of state of matter (for example, liquid to solid) in which
properties change qualitatively while an underlying variable such as
temperature changes smoothly.
Within the SIBurst framework, "phase change" is used as a **metaphor** and
organizing lens for a qualitative transition in intelligence. It is not asserted
as a law of AI development, and no claim is made that AI capability obeys the
physics of phase transitions.

### Superintelligence

Commonly used to mean intelligence that greatly exceeds human cognitive
performance across a broad range of domains. Usage varies: some writers reserve
the term for general superiority across virtually all domains of interest;
others apply it to narrower domains.
Within the SIBurst framework, superintelligence names the *direction* of the
transition the project is concerned with. Its use in the name is not a claim
that superintelligence exists, is near, or will occur.

### Frontier system

A system at or near the leading edge of capability at a given time.
Within the SIBurst framework, "frontier" is relative and moving: a frontier
system today may be ordinary later. Some policy contexts define frontier
systems by specific thresholds (for example, training compute); SIBurst does
not adopt any single such threshold.

### Agent

A system that pursues a goal by selecting and taking actions, observing their
results, and adjusting.
The word has a long history in computer science with broader and narrower
meanings; in current usage it often refers to systems built around a language
model that can call tools. Within the SIBurst framework, what matters is the
move from producing outputs to taking actions.

### Agentic system

A system, possibly composed of several models, tools, and agents, whose overall
behavior is goal-directed action rather than single-response output.
Within the SIBurst framework, "agentic" describes a degree, not a binary: systems
can be more or less agentic depending on how much they plan, act, and adapt
without step-by-step human direction.

### Autonomous system

A system that operates for extended periods, or across many decisions, without
human intervention at each step.
Autonomy is a matter of degree and scope, and is defined differently in
robotics, vehicles, software, and policy contexts. Within the SIBurst framework,
an increase in autonomy is one of the clearest candidate markers of a change in
operating regime.

### Inference

The process of running a trained model to produce outputs.
In statistics and logic, "inference" has different meanings (drawing
conclusions from data or premises). Within the SIBurst framework, the term is
used in its machine-learning sense unless otherwise stated.

### Compute layer

The hardware, and the systems that allocate it, on which models are trained
and run.
Within the SIBurst framework, the compute layer belongs to the BUILD function
(see `COMMERCIAL_TERRITORY.md`).

### Intelligence infrastructure

The combined layers — compute, training, inference, orchestration, tooling,
monitoring, and governance mechanisms — required to build, run, and oversee
capable AI systems.
This is a SIBurst working term rather than an established technical category.

### Capability evaluation

The structured assessment of what a system can do, under what conditions, and
how reliably.
Within the SIBurst framework, evaluation has two questions: *how well* a system
performs on known tasks, and *whether* it can now do things in kind that it
could not before. The second question is the one most specific to SIBurst.

### Observability

The ability to understand a system's internal state and behavior from what it
exposes: logs, traces, metrics, and other signals.
The term originates in control theory and is widely used in software operations.
Within the SIBurst framework, observability applies both to infrastructure and
to model or agent behavior.

### Transition monitoring

Ongoing observation aimed at detecting signs that a system is approaching,
crossing, or has crossed into a different operating regime.
This is a SIBurst working term. It describes a function, not a proven method:
the framework does not claim that transitions can always be detected in advance.
