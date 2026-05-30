# Presentation Script — SABD Project 1

**Daniel Garoz · 12 June 2026 · 15 minutes**

Read this as your study guide. Each section below corresponds to one slide.
The text in `>` blocks is what you actually say (in English).
The shorter notes underneath are reminders / what to emphasise.

---

## Slide 1 — Title

> Good morning. My name is Daniel Garoz, I am an Erasmus student in
> Computer Engineering. Today I will present Project 1 of SABD,
> which is a complete Big Data pipeline analyzing US airline delays
> using Apache Spark and HDFS.

**Tip:** smile, slow down, take a breath. ~30 seconds.

---

## Slide 2 — Outline

> In the next 15 minutes I will cover: the goal of the project,
> the dataset, the system architecture, how the two queries are
> implemented, the experimental evaluation, and the main lessons
> learned.

**Tip:** point at the screen as you go through each bullet. ~30 seconds.

---

## Slide 3 — Project Goal

> Important framing: the project is not really about airlines.
> It is about demonstrating that I can design and deploy a complete
> Big Data pipeline.
>
> The evaluation criteria are architecture, code organization,
> efficiency, and proper benchmarking. I will explain each of those
> in the next slides.

**Key idea to land:** the airline data is just the test bench. ~1 minute.

---

## Slide 4 — Dataset

> The dataset comes from the US Bureau of Transportation Statistics.
> The specification mentions four months, but the archive available
> through the course covered only the first three —
> January to March — with about 1.5 million flight records.
> I documented this constraint in the report.
>
> The original CSV has 27 columns, but I project only the 14 that
> Q1 and Q2 actually need. This is called *column pruning*, and I
> do it at load time to save I/O and memory.

**Key idea to land:** I am aware of the constraint and the methodology is unaffected. ~1 minute.

---

## Slide 5 — System Architecture

> The deployment is four Docker containers in a single private network:
> two for HDFS — namenode and datanode — and two for Spark —
> master and worker.
>
> Everything is described in a single docker-compose YAML, so the
> cluster can be reproduced from scratch with one command.
> I chose bde2020 images because they come pre-configured for
> HDFS and Spark to discover each other, which keeps the YAML compact.

**Anticipated question:** "Why replication 1?" → because there is a single datanode, more replicas would be impossible. ~1.5 minutes.

---

## Slide 6 — Code Organization

> The codebase is intentionally split into three layers:
> utilities I use everywhere, the Spark setup which is shared
> between both queries, and one script per concrete query.
>
> This separation paid off when moving from local CSV to HDFS:
> I only modified the preprocessing module — one line, to read
> the Spark master URL from an environment variable.
> The query files themselves did not change at all.

**Key idea to land:** the design is modular, not coincidentally so. ~1 minute.

---

## Slide 7 — Query 1 implementation

> Query 1 compares American Airlines and Delta on a monthly basis.
> For non-cancelled flights it computes the average, minimum and
> maximum departure delay. Separately, for ALL flights including
> cancelled ones, it computes the cancellation rate.
>
> Because the filtered DataFrame is used twice in two independent
> aggregations, I cache it explicitly. Without caching, Spark would
> re-execute the lineage from the CSV read on every action.
>
> The final coalesce(1) gives me a single CSV file, as the project
> expects.

**Anticipated question:** "Why .count() after .cache()?" → to force materialization before the first real action, so the loading timer reports cache-warm time consistently. ~1.5 minutes.

---

## Slide 8 — Query 1 results

> On the left, the monthly average departure delay. Both carriers
> behave similarly, around 8 to 15 minutes.
>
> On the right, the cancellation rate: Delta clearly outperforms
> American Airlines, especially in January where AA cancels
> almost 3.7% of flights against Delta's 2.8%.
>
> The January peak in cancellations matches what you would
> intuitively expect from winter storms in the United States.

**Tip:** physical pointer to the plots helps. ~1 minute.

---

## Slide 9 — Query 2 implementation

> Query 2 ranks every carrier by average arrival delay, keeping
> only the ones with at least 500 completed flights.
>
> The five delay-cause columns are often NULL because the BTS only
> fills them when the arrival delay exceeds 15 minutes.
> I treat NULL as zero, meaning "this cause did not contribute".
> The alternative of dropping NULLs would bias the average upwards
> because it would keep only the delayed flights. I justified this
> choice explicitly in the report.

**Anticipated question:** "Why this NULL policy?" → answer with the bias argument above. ~1.5 minutes.

---

## Slide 10 — Query 2 cause breakdown

> The stacked bar chart shows where the delay comes from for each
> of the top 10 carriers.
>
> The dominant cause for the worst performers — OH, F9 — is
> LATE_AIRCRAFT_DELAY, which is exactly the domino effect:
> if your morning flight is late, every subsequent flight using
> that aircraft will also be late.
>
> Weather and security are minor contributors across the board.

**Key idea to land:** the analysis reveals a real-world operational pattern. ~1 minute.

---

## Slide 11 — Four design decisions

> These are the four decisions I am most likely to be asked about.
>
> First: explicit schema, because inferSchema requires a second pass
> over the data just to infer types.
>
> Second: caching is not free, so I only cache when I actually
> reuse the DataFrame.
>
> Third: the default 200 shuffle partitions is way too many for our
> data size on a single machine. Eight matches the CPU count.
>
> Fourth: coalesce(1) is a deliberate trade-off. It costs about
> two seconds at output, but it gives the user a single result file,
> which is what the specification requires.

**Tip:** speak slower here, this slide is the "earning your grade" moment. ~1.5 minutes.

---

## Slide 12 — Benchmark methodology

> For each query and each configuration I run the benchmark six
> times. I discard the first run as warmup, and report mean and
> standard deviation across the remaining five.
>
> The warmup step is critical: a pilot Q1 run on HDFS without warmup
> measured 35 seconds, while the steady state is 19. The 16-second
> difference is JVM JIT compilation plus HDFS metadata caching
> warming up.
>
> Without discarding that first iteration, every measured average
> would be distorted.

**Anticipated question:** "Why only 5 measured runs?" → trade-off between statistical confidence and total benchmark time; n=5 is standard for course projects. ~1 minute.

---

## Slide 13 — Results table

> This is the headline table. Local times are around 4 to 6 seconds.
> HDFS times are around 17 to 19 seconds. The overhead is roughly
> 3 to 4 times.
>
> The breakdown shows that the overhead is concentrated in the
> loading and output stages, not in the computation itself.
> That makes sense: the computation is arithmetic that the CPU
> can do in milliseconds. What changes is the I/O path.

**Tip:** if asked, you can also mention preprocessing is essentially zero in both — that confirms it really is just Spark planning the DAG. ~1 minute.

---

## Slide 14 — Observations

> Four take-aways.
>
> First, loading is the dominant HDFS cost, because it triggers
> metadata round-trips to the namenode and network transfers
> from the datanode.
>
> Second, output costs are high because of the coalesce shuffle
> combined with HDFS replication writes.
>
> Third, the actual computation time is the same in both setups —
> the dataset is small relative to modern CPU capacity. The cluster
> does not bring a speed-up at this scale, only overhead.
>
> Fourth, warm-up is mandatory; without it the numbers are meaningless.

**Key idea to land:** HDFS overhead is real, predictable, and *not* a sign of bad implementation. ~1 minute.

---

## Slide 15 — Conclusions

> To wrap up: I delivered the containerized stack, the two queries
> with all their visualizations, the CSV results, and the benchmark
> suite.
>
> The main take-aways are that HDFS overhead is real and measurable,
> that most performance wins come from deliberate design decisions
> rather than from the framework itself, and that reproducibility
> is achievable with one docker-compose command and two shell scripts.

**Tip:** project confidence here, you are landing the plane. ~30 seconds.

---

## Slide 16 — Thank you / Questions

> Thank you for your attention. I am happy to take any questions.

**Tip:** keep silent for 2 seconds after this. Let them digest. Then wait for the first question.

---

# Likely questions from the professors

These come straight from the parts of the report and code that
professors typically probe. We will work on these in the
walkthrough sessions before the defense.

1. Explain `cache()` in detail. Why on `df`, why not on `non_cancelled`?
2. What is a *narrow* vs *wide* transformation? Which ones appear in Q1?
3. Why `coalesce(1)` and not `repartition(1)`?
4. What would change if you used Spark SQL instead of the DataFrame API?
5. Walk me through what happens when you submit `query1.py` to the cluster.
6. Why is loading on HDFS so much slower than locally?
7. Why did you treat NULL delay causes as 0? Defend the choice.
8. What is the role of the namenode vs the datanode?
9. What does `replication=1` mean and why do you set it?
10. What is JVM JIT compilation and how does it affect benchmarking?
11. Why do you discard the first run in the benchmark?
12. What is a SparkSession vs a SparkContext?
13. Explain the DAG of Query 1.
14. What is *column pruning* and where does it happen?
15. If the dataset were 1 TB instead of 178 MB, what would change?
16. What is `shuffle.partitions`? Why 8?
17. How would you scale this to a multi-node cluster?
18. What is the difference between client and cluster deploy mode?
19. Why bde2020 images? Could you have used apache/hadoop instead?
20. If you had to add Query 3 from the spec, where in the codebase would you start?

---

# Final tips for the day

- Print this script as backup, but **do not read from it during the talk**.
- Rehearse 3 times out loud, with a timer.
- If you run out of time, **drop slide 8** (Q1 plots) or **slide 10** (Q2 causes) — keep the architecture and decision slides.
- If a question stumps you, say *"That is a good question, let me think for a second"* and breathe.
