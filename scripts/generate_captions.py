#!/usr/bin/env python3
"""
Generate a batch of short and/or long social-media captions for the
"Study + Paid Internship in Singapore" program.

Usage:
    python3 generate_captions.py --config <config.json> --short 5 --long 3 --out captions.md

The factual program details (duration, industries, phone, discount, etc.)
come from the config file. The wording/voice comes from phrase banks below,
tuned to Josh's own writing samples, so re-running with a higher --short/--long
count produces new combinations instead of the same caption every time.
"""
import argparse
import json
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Phrase banks (voice/style only -- no facts live here, facts come from config)
# ---------------------------------------------------------------------------

SHORT_HOOKS = [
    "Anybody wants to come to {country}?",
    "Who wants to come to {country}?",
    "Dreaming of studying and working overseas?",
    "Want to earn a salary while you study?",
    "{country} calling!",
    "Ready for a fresh start in {country}?",
    "Looking for a real opportunity abroad?",
    "Want to study AND get paid at the same time?",
]

SHORT_PROGRAM_LINES = [
    "Study + Internship with SALARY.",
    "Study & work with on-the-job training.",
    "Get paid while you train.",
    "Exciting job opportunities with on-the-job training and a salary!",
    "Study now, work and earn later.",
    "Paid internship + study program now open.",
]

SHORT_VISA_FEE_LINES = [
    "NO AGENCY FEE.",
    "No agency fees, no hidden costs.",
    "{visa_note}, no agency fee.",
    "Zero agent fees, straightforward process.",
]

SHORT_CTAS = [
    "PM me for the visa process.",
    "DM me for more info.",
    "Interested can DM me.",
    "Interested? Message me directly.",
    "PM ME FOR VISA PROCESS.",
    "WhatsApp me at {phone}.",
]

# Static hashtag pool (lowercase, casual style) -- combined with the
# country hashtag for every short caption. 2-3 of these are picked at
# random and shuffled together with the country tag so the hashtag line
# reads naturally (not always the same tags in the same order).
SHORT_HASHTAG_POOL = [
    "#student",
    "#studentlife",
    "#studyabroad",
    "#workabroad",
    "#livingabroad",
    "#paidinternship",
    "#internship",
    "#studyandwork",
    "#abroadlife",
    "#globalcareer",
    "#studentraveler",
    "#careerabroad",
]


def _hashtag_line(cfg, rng):
    """Every short caption ends with a small hashtag set: the country tag
    plus 2-3 random picks from the static pool, shuffled together."""
    country_tag = "#" + cfg["country"].lower().replace(" ", "")
    picks = rng.sample(SHORT_HASHTAG_POOL, k=rng.choice([2, 3]))
    tags = picks + [country_tag]
    rng.shuffle(tags)
    return " ".join(tags)

# Each headline is a standalone opening line -- either an ALL-CAPS statement
# or an emoji + question. Some reference the country, some don't; {flag}/
# {country}/{COUNTRY} are filled in if present.
LONG_HEADLINES = [
    # eye-catching mixed-case hooks (preferred style -- an emoji/flag lead-in
    # plus a punchy statement or direct question, not a shouted ALL-CAPS line).
    # Punchier, higher-energy set: curiosity gaps, direct address ("you"),
    # urgency, and stronger verbs read as more scroll-stopping than a flat
    # statement of fact.
    "\U0001F6A8 Stop Scrolling — This Could Change Your Life {flag}",
    "\U0001F4A5 The Opportunity You've Been Waiting For Is in {country}",
    "\U0001F525 Imagine Studying AND Earning in {country} {flag}",
    "{flag} This Is Your Sign to Study + Work in {country}",
    "\u2708\uFE0F Pack Your Bags — {country} Is Calling!",
    "\U0001F4BC Get Paid to Build Your Future in {country}",
    "\U0001F30F Your International Career Starts Right Here in {country}",
    "\U0001F3AF Study. Intern. Earn. All in {country}.",
    "\U0001F680 From Classroom to Career — Your {country} Journey Starts Now",
    "\u2728 Turn Your Study Abroad Dream Into Reality in {country}",
    "\U0001F525 Applications Are Open — Don't Miss Your Shot at {country}!",
    "\U0001F4AB Study Smart, Earn Sooner — Welcome to {country}",
    "\U0001F31F Your Passport to a Paid Career Starts in {country}",
    "\U0001F4E2 Big News: Study + Paid Internship Slots Just Opened in {country}!",
    "{flag} Ready to Level Up? {country} Is Where It Begins",
    "\U0001F525 Want to Study in {country} and Get a Paid Internship?",
    "\u2728 Your {country} Study + Internship Journey Starts Here {flag}",
    "\U0001F6A8 {country} Study & Paid Internship — Applications Open! {flag}",
    "\U0001F31F Study, Train, and Earn in {country}",
    "\U0001F4BC Get Paid While You Study in {country} {flag}",
    "\U0001F393 Study in {country} — Now With a Paid Internship! {flag}",
    "\U0001F680 Your Ticket to Study + Work in {country}",
    "\u2728 Study Abroad, Earn Abroad — {country} Edition {flag}",
    "\U0001F4A5 {country} Awaits — Study, Train, and Earn!",
    "\U0001F3AF Your Shot at Studying + Working in {country}",
    # longer, more elaborate hooks -- a full sentence (or two clauses joined
    # with an em dash) rather than a short phrase, for when the post should
    # open with something more descriptive and attention-grabbing than a
    # quick tagline
    "\U0001F4BC Get Paid While You Study — Your Dream Career in {country} Starts Today! {flag}",
    "\U0001F525 Why Choose Between Studying and Earning? In {country}, You Get Both! {flag}",
    "\u2728 Your Ticket to a World-Class Education AND a Paid Career — Right Here in {country}!",
    "\U0001F393 Study Hard, Earn Real Money, and Build a Career You're Proud Of — In {country}! {flag}",
    "\U0001F30F From the Classroom to a Real Paycheck — Your {country} Story Starts Right Now! {flag}",
    "\U0001F680 One Program, Two Wins — Get a Real Education AND a Real Salary in {country}!",
    "\U0001F4A5 Stop Dreaming About It — Go Study, Get Paid, and Build Your Future in {country}! {flag}",
    "\U0001F31F Imagine Graduating With Both a Diploma AND Real Work Experience — That's {country} for You! {flag}",
    # a couple of the bolder ALL-CAPS banner lines kept for variety
    "{flag} STUDY + PAID INTERNSHIP IN {COUNTRY}",
    "{flag} ONE YEAR OPPORTUNITY IN {COUNTRY}",
]

# The subtext/hook line right under the headline.
LONG_HOOKS = [
    "Looking for an opportunity to gain international experience?",
    "Want to study abroad and earn a salary at the same time?",
    "Ready to build your future overseas?",
    "Looking for a real pathway to study and work abroad?",
    "Applications are now open for our Study & Paid Internship Program!",
    "Study. Learn. Gain Experience.",
    "Study and intern in {country} with our 1-Year Program.",
    "Make your dream a reality!",
]

# Optional extra line that sometimes appears just before the CTA block.
LONG_CLOSERS = [
    "\U0001F30F Build your future while gaining international work experience.",
    "\U0001F4A1 No experience needed — just bring your drive to learn and grow.",
    "\U0001F91D We support you through every step, from application to your first paycheck.",
    "\U0001F4C8 Join hundreds of students who've already started their journey with us.",
    None,
]

LONG_URGENCY_LINES = [
    "\u26A0\uFE0F Limited seats available for this intake — apply early to secure your spot.",
    "\u23F3 Intake closes soon, so don't wait to start your application.",
    "\U0001F4CC Slots are filling up fast for this batch.",
    None,
    None,
]

LONG_CTA_BLOCKS = [
    "\U0001F4E9 PM for more details.\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 Message me for more details.\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 DM to find out if you qualify.\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 Message us today!\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 PM us now!\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 Reserve your slot today!\n\U0001F4F1 WhatsApp: {phone}",
    "\U0001F4E9 Contact us for complete details.\n\U0001F4F1 WhatsApp: {phone}",
]

CHECK = "✔️"
DOT = "\U0001F539"


def build_short_caption(cfg, rng, used):
    """Mimic Josh's own short-caption voice: 2-3 punchy fragments plus a CTA,
    not a fully-punctuated four-sentence paragraph. Which fragments appear,
    and in what order, is randomized so repeated runs don't feel templated."""
    for _ in range(40):
        include_hook = rng.random() < 0.9
        include_program = rng.random() < 0.95
        include_fee = rng.random() < 0.95
        hook = rng.choice(SHORT_HOOKS) if include_hook else None
        program = rng.choice(SHORT_PROGRAM_LINES) if include_program else None
        fee = rng.choice(SHORT_VISA_FEE_LINES) if include_fee else None
        cta = rng.choice(SHORT_CTAS)
        tag = _hashtag_line(cfg, rng)

        # keep a fixed hook-first / cta-last shape (matches all 3 samples)
        # but let program/fee swap order between them for variety
        middle = [x for x in [program, fee] if x]
        rng.shuffle(middle)
        if not middle and not hook:
            hook = rng.choice(SHORT_HOOKS)

        key = (hook, tuple(middle), cta, tag)
        if key in used:
            continue
        used.add(key)

        parts = []
        if hook:
            parts.append(hook.format(country=cfg["country"]))
        for m in middle:
            parts.append(m.format(
                visa_note=cfg.get("visa_note", "Visa assistance provided"),
            ))
        parts.append(cta.format(phone=cfg["phone"]))
        text = " ".join(parts)
        text += " " + tag
        return text.strip()
    return None


def _benefit_groups(cfg):
    """Each "fact" (study duration, fee, payment plan, ...) can have several
    interchangeable phrasings, e.g. "No Agent Fee" / "No Agent Fees" /
    "No Agency Fee". `benefit_groups` in the config is a list of lists; a
    plain flat `benefits` list still works and is treated as one phrasing
    per fact."""
    if "benefit_groups" in cfg:
        return cfg["benefit_groups"]
    return [[b] for b in cfg.get("benefits", [])]


def build_long_caption(cfg, rng, used):
    groups = _benefit_groups(cfg)
    industries = cfg.get("industries", [])

    for _ in range(40):
        headline = rng.choice(LONG_HEADLINES)
        hook = rng.choice(LONG_HOOKS)
        closer = rng.choice(LONG_CLOSERS)
        urgency = rng.choice(LONG_URGENCY_LINES)
        cta = rng.choice(LONG_CTA_BLOCKS)

        # pick a subset of benefit facts -- most posts now show 5-7 (up from
        # 4-5) so the checklist itself carries more of the post's length
        n = min(len(groups), rng.randint(5, 7)) if len(groups) > 5 else len(groups)
        # Not sorted: when n == len(groups) (true whenever there are <=5
        # fact groups, the common case for a flat `benefits` list), a sorted
        # sample always comes back as 0..len-1 in order, so every caption
        # would list the same facts in the same order. Sampling without
        # sorting keeps the checklist order varying between captions too.
        idxs = rng.sample(range(len(groups)), n) if groups else []
        benefits = [rng.choice(groups[i]) for i in idxs]

        # industries list now shows most of the time rather than about half,
        # since it's one of the easiest ways to add real, relevant length
        include_industries = bool(industries) and rng.random() < 0.85

        key = (headline, hook, closer, urgency, cta, tuple(benefits), include_industries)
        if key in used:
            continue
        used.add(key)

        headline_text = headline.format(
            flag=cfg.get("flag_emoji", "\U0001F1F8\U0001F1EC"),
            country=cfg["country"],
            COUNTRY=cfg["country"].upper(),
        )
        hook_text = hook.format(country=cfg["country"])

        lines = [headline_text, "", hook_text]
        if benefits:
            lines += [f"{CHECK} {b}" for b in benefits]
        if include_industries:
            lines.append("")
            lines.append(cfg.get("industries_label", "Available industries:"))
            lines += [f"{DOT} {i}" for i in industries]
        lines.append("")
        if closer:
            lines.append(closer)
        if urgency:
            lines.append(urgency)
        lines.append(cta.format(phone=cfg["phone"]))
        return "\n".join(lines)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--short", type=int, default=5)
    ap.add_argument("--long", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    try:
        cfg = json.loads(Path(args.config).read_text())
    except FileNotFoundError:
        raise SystemExit(f"Config file not found: {args.config}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Config file '{args.config}' is not valid JSON: {e}")
    missing = [k for k in ("country", "phone") if k not in cfg]
    if missing:
        raise SystemExit(f"Config is missing required field(s): {', '.join(missing)}")
    rng = random.Random(args.seed)

    short_used, long_used = set(), set()
    shorts, longs = [], []
    for _ in range(args.short):
        c = build_short_caption(cfg, rng, short_used)
        if c:
            shorts.append(c)
    for _ in range(args.long):
        c = build_long_caption(cfg, rng, long_used)
        if c:
            longs.append(c)

    if len(shorts) < args.short:
        print(f"Warning: only generated {len(shorts)} of {args.short} requested short captions "
              "(ran out of unique phrasing combinations).", file=sys.stderr)
    if len(longs) < args.long:
        print(f"Warning: only generated {len(longs)} of {args.long} requested long captions "
              "(ran out of unique phrasing combinations).", file=sys.stderr)

    out_lines = ["# Captions\n"]
    out_lines.append("## Short captions\n")
    for i, c in enumerate(shorts, 1):
        out_lines.append(f"**{i}.**\n{c}\n")
    out_lines.append("## Long captions\n")
    for i, c in enumerate(longs, 1):
        out_lines.append(f"**{i}.**\n```\n{c}\n```\n")

    Path(args.out).write_text("\n".join(out_lines))
    print(f"Wrote {len(shorts)} short + {len(longs)} long captions -> {args.out}")


if __name__ == "__main__":
    main()
