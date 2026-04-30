# Professional Conduct

Load this when the user is dealing with deadlines, estimates, scope discussions, "should I add this" questions, or any situation where engineering judgment meets business pressure.

This file distills *The Clean Coder* (Robert C. Martin) into senior-engineer practical wisdom. The technical books teach you to write good code; this one teaches you to be a professional whose code can be trusted.

## Core stance: take responsibility

A professional owns their work. That means:

- **You are responsible for the code you ship.** Bugs are yours. "QA didn't catch it" is not a defense.
- **You are responsible for the estimates you give.** If you said two weeks and it took six, that's a missed estimate, not bad luck.
- **You are responsible for saying no when you should.** "But they made me commit to it" doesn't hold up.
- **You are responsible for your own learning.** Your employer is paying for output, not for your career development. That's on you.

Professionalism is the difference between an engineer and a software laborer. Laborers do what they're told. Professionals push back when "what they're told" will produce bad outcomes.

## How to say "no"

Saying yes to bad ideas is the most common professional failure. It feels collaborative; it's actually cowardly.

### When to say no

- The deadline is impossible without serious quality compromise
- The feature contradicts another part of the system
- The approach will create maintenance pain you'll later be blamed for
- The work is being requested without context you'd need to do it well
- The team has commitments that this would crowd out

### How to say no — the formula

The bad way:
> "No, that's a terrible idea."

The amateur way:
> "Sure, I'll try."  *(then misses the deadline / ships broken / silently resents)*

The professional way:
1. **Acknowledge what they're trying to achieve.** "I get that we need this for the demo on Friday."
2. **State the constraint honestly.** "Building this properly takes about 5 days of work."
3. **Offer real alternatives, with tradeoffs.** "We have three options: (a) push the demo a week, (b) ship a hardcoded mock that we replace next sprint — I'll need explicit agreement that we replace it, (c) cut the analytics piece, ship the rest, add analytics later."
4. **Let them decide. They own the priorities; you own the truth about the work.**

The professional answer is rarely a flat "no." It's usually "yes, but with the following honest tradeoffs." But it's never "yes" when "yes" requires lying about what's possible.

## Estimates: ranges, not promises

The most damaging thing a professional can do is treat estimates as promises.

### What an estimate actually is

An estimate is an educated guess about how long something will take, expressed as a probability distribution. "2 weeks" is shorthand for "I think there's a 50% chance it'll be done in 2 weeks, but it could be 1 week or 5 weeks depending on what I find."

When stakeholders hear "2 weeks," they hear a promise. When you say it, you mean a guess. The mismatch causes most missed deadlines.

### How to give better estimates

**Use ranges:**
> "Best case 3 days, expected 5 days, worst case 9 days."

**Use probability:**
> "I'm 50% confident in 5 days. I'm 90% confident in 9 days."

**Use the PERT formula** for a quick weighted average:
- O = optimistic estimate (everything goes well)
- M = most likely estimate
- P = pessimistic estimate (things go wrong but not catastrophically)
- **Estimate = (O + 4M + P) / 6**
- **Standard deviation = (P − O) / 6**

For 5 tasks averaged together, the standard deviation shrinks (because errors partially cancel), so a series of estimates is more reliable than a single one.

**Always include time for:**
- Tests (yes, even if they say "skip tests this time")
- Code review iteration
- Bug fixing as you go
- Integration with the rest of the system
- Deployment + verification
- The unknown unknowns (add a buffer; it's not padding, it's calibration)

If you're consistently late, your estimates are wrong — adjust them upward. Lying to yourself about how fast you are doesn't make you faster; it just makes you chronically late.

## Commitment vs. estimate — a critical distinction

- **An estimate** is a guess. It's allowed to be wrong.
- **A commitment** is a promise. It must be met.

Don't confuse the two. If a stakeholder asks "can you commit to Friday?", they're asking you to *guarantee* Friday. Only commit when you're nearly certain — say, 90%+ confidence. For everything else, give an estimate.

The professional language: *"I can't commit to Friday, but I estimate Friday with 60% confidence and Monday with 90% confidence. If you need a hard commitment, it's Monday."*

## The Boy Scout Rule, applied to careers

Leave every project a little better than you found it:
- The codebase: cleaner than before (the original Boy Scout Rule)
- The team: better-equipped than before (mentor, share knowledge)
- The processes: more efficient than before (automate the painful, document the missing)
- Yourself: more skilled than before (every project teaches something — extract the lesson)

Five years of "I did the job" is laborer's work. Five years of "I left every project measurably better" is a senior engineer's career.

## Practice: deliberate, outside work hours

Athletes don't get good by playing games. They get good by practicing skills that come up *during* games. Same for engineers.

What practice looks like:
- Read code outside your codebase (open-source projects, GitHub)
- Solve problems on platforms (LeetCode, Exercism, Advent of Code) — not for interviews, for skill maintenance
- Read books — the five we listed for this skill, plus your own additions
- Try a new language every year or two (forces you to question habits)
- Write — blogs, notes, internal docs. Writing crystallizes thinking.

Your employer pays you for output. Your *skill* is your responsibility. The 9-to-5 doesn't make you a senior engineer; the deliberate practice does.

## Working under pressure

When deadlines tighten and stress rises, amateurs cut corners and hope no one notices. Professionals do the *opposite*: under pressure, they *increase* their discipline.

Why: pressure is exactly when bugs are most likely. The way to ship faster is to make fewer mistakes — not skip the mistake-prevention practices.

Specifically:
- **Tests:** keep writing them. The bug you skip-test today becomes the production incident tomorrow.
- **Code review:** keep doing them. A 5-minute review prevents an hour of debugging.
- **Cleanup:** keep doing the small refactors. A 10-minute cleanup prevents 10 hours of tangled-code maintenance later.
- **Communication:** stay loud. When you're slipping, say so early. Hidden slippage compounds.

The pros stay calm and clean under pressure. That's what senior actually means.

## Avoid the "10x developer" trap

You'll hear "10x engineer" stories — the dev who works 80 hours a week and ships everything. Run from that culture. It's:

- **Unsustainable.** Burnout is real and recovery is slow.
- **Bad for the team.** The "hero" creates code only they understand, hoarding context.
- **Bad for the code.** Tired people produce buggy code. Sleep-deprived debugging is famous for shipping the worst bugs.
- **Bad for your career.** The market rewards consistent, predictable, sustainable output more than heroic crunches.

The senior engineer's pace is **steady**. 35–45 productive hours a week, year after year, without crunching.

## Continuous learning: the basics

What every senior should keep current on:

- **Language fundamentals** — the language you write in daily, deeply.
- **The major paradigms** — OO, functional, procedural. You don't have to be a master, but you should be conversant.
- **Data structures and algorithms** — at the level where you can recognize when one applies, even if you don't implement it from scratch.
- **System design** — how distributed systems work. Failure modes, latency, consistency.
- **Networking, OS, databases** — at the level of "I understand what's happening when I make this call."
- **Testing techniques** — the topic deserves more depth than most engineers give it.
- **Security fundamentals** — at minimum: OWASP Top 10, basic crypto, auth/authz, secret management.

You don't need to be expert in all of these. You need to be *aware* of all of them, deep in 1–2.

## Communication is part of the job

Senior engineers spend a surprising amount of time *not coding*. They:
- Write design docs
- Review others' code and designs
- Mentor juniors
- Communicate with stakeholders
- Document decisions

If you can't communicate clearly, you cap out at mid-level no matter how good your code is. Practice writing. Practice speaking. Both compound over a career.

## Scope discipline: the YAGNI of features

Stakeholders will constantly ask for "just one more thing." Each one is small. Together, they sink the ship.

The senior move:
- **Acknowledge:** "That's a good idea."
- **Defer:** "Let me capture it. We can discuss whether it goes in this release or next."
- **Track:** Write it down. In a backlog, ticket, doc — somewhere persistent.
- **Don't silently expand the work.** Saying "yes, I'll fit it in" without rescheduling is how good engineers become chronically late engineers.

Every "yes" to scope creep is a "no" to the deadline you committed to. Be honest about the trade.

## How to handle being wrong

You'll be wrong about technical decisions. Frequently. The question isn't whether — it's how you handle it.

Bad: defending the bad decision because admitting it makes you look weak.
Good: "I was wrong. Here's what I missed. Here's what I'd do now."

Engineers respect the second response, every time. The first creates the kind of "personality conflicts" that derail teams.

This applies to your past code too. Don't be ashamed of code you wrote 3 years ago. If your old code looks bad to current-you, that means current-you has grown. That's the goal.

## A note on the "humble brilliance" stance

The senior engineers worth working with have two qualities at once:

1. **Confidence** in what they know. They argue technical points clearly and don't hedge needlessly.
2. **Humility** about what they don't know. They ask questions, take feedback, change their minds.

The trap is sliding into either extreme — arrogance ("I'm always right") or false humility ("Who am I to say?"). Both are corrosive. Aim for: *strong opinions, weakly held*.

## Closing principle: be someone people want to work with

Technical skill gets you hired. Professionalism gets you trusted with bigger problems and better teammates. Over a 20-year career, professionalism compounds more than any specific technical skill.

The skills in this whole skill (clean code, refactoring, testing, etc.) are about the code. This file is about *being the engineer your team wants to keep*. Both matter. The technical skills can be built in 5 years; the professional reputation takes 15.
