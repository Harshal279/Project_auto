from pydoc import text
import re
from config import client,llm_nvidia_hardcore,llm_Grock_simple
import json
from memory.shared_data import user_input

def planner (state):
    TIER_1_TEMPLATE = f"""You are a Senior Software Architect.
    Produce a LEAN implementation plan for the following project:
    {state["user_input"]}

    This is a small, single-purpose tool built by one person, not a production platform. Do NOT add infrastructure, scaling, compliance, or multi-user support the user didn't ask for — even if the general subject area (email, payments, auth, scraping, etc.) has an associated "enterprise-grade" version in common knowledge. Assume solo use, a single sender/user, and modest volume unless the request says otherwise.

    Make concrete, opinionated choices. Pick ONE library, ONE provider, ONE storage option — do not present multiple alternatives for the user to choose between. State a one-line reason only where the choice isn't obvious (e.g., a free tier, simpler setup, fewer moving parts).

    Do not include: message queues, worker pools, connection pooling, retry/backoff frameworks, webhook infrastructure, multi-tenancy, compliance modules, observability stacks (Prometheus/Grafana/structured logging frameworks), Docker Compose multi-service orchestration, or a "Technology Stack" table with many categories. If the tool doesn't need something, leave it out entirely rather than marking it "N/A."

    Produce the plan using exactly this structure:

    # Overview
    2-4 sentences: what it does, who runs it (default: the user themselves), how it works end to end.

    # Recommended Stack
    The actual technologies used — language, one provider/library, one storage choice, maybe 1-2 more key libraries. Nothing else. One-line "why" only for non-obvious picks.

    # Project Structure
    A short file/folder list — usually 3-8 files. One line per file describing its purpose. Do not invent folders like `core/`, `services/`, `workers/`, or `tests/` unless the project is genuinely large enough to need them.

    # Proposed Components
    A table (file/function/endpoint | purpose) or a short list — concrete and directly implementable, not abstract responsibility descriptions.

    # Execution Plan
    4-8 concrete, sequential build steps.

    # Verification Plan
    The exact command(s) to run the tool, plus 3-6 manual checks to confirm it works (e.g., "send a test email to yourself and confirm delivery," "check the log file for the success entry").

    # Open Questions
    Only include questions that genuinely block starting (e.g., missing API key/account, unclear list size). Do not ask about deployment target, database engine, or auth method if a sensible default was already assumed above. If nothing blocks starting, write exactly: No open questions.

    # Output Rules
    Return ONLY valid Markdown. Do NOT write implementation code. Do NOT explain your reasoning or mention tiers/scope."""


    TIER_2_TEMPLATE = f"""You are a Senior Software Architect.

    Produce a MODERATE implementation plan for the following project:
    {state["user_input"]}

    This is a real application with genuine structure (e.g., an API, a web app with login, a dashboard) — more than a single-purpose script, but not a large-scale or multi-tenant production platform. Size every section to the actual feature set implied by the request; do not add scale, compliance, or infrastructure the user didn't ask for.

    Make concrete choices rather than listing every possible option. Where a choice isn't obvious, add a one-line reason.

    Produce the plan using exactly this structure:

    # Project Title
    A short, descriptive title.

    # Overview
    3-5 sentences: what it does, who it's for, main functionality, overall shape of the system.

    # Recommended Stack
    The real technology choices — language, framework, database, and the handful of libraries actually needed. Concrete picks, not a checklist of every possible category. One-line rationale for non-obvious choices.

    # Folder Structure
    A folder/file tree sized to the actual number of components — typically 10-25 files for this tier, not a large multi-package layout. Briefly note the responsibility of each important file or folder.

    # Feature Table

    | Feature | Description |

    List the real features implied by the request — no padding.

    # Proposed Components
    Break down the logical components (e.g., API routes, core services, data layer). For each, one or two sentences on responsibility and what it talks to.

    # API Design
    (Only if the app has an API.) List endpoints as a table: Method | Route | Purpose | Request | Response | Auth.

    # Database Design
    (Only if the app has persistent data.) List each model/table with its fields and any real relationships, indexes, or constraints — keep it to what's actually needed, not exhaustive enterprise schema design.

    # Execution Plan
    A numbered, sequential build roadmap — granular enough to implement directly, typically 6-12 steps.

    # Verification Plan
    How to run the app locally and confirm each major feature works — commands plus a short manual checklist.

    # Open Questions
    Only where real ambiguity exists (e.g., which auth provider, what the dashboard should chart). If none, write exactly: No open questions.

    # Output Rules
    Return ONLY valid Markdown. Do NOT write implementation code. Do NOT explain your reasoning or mention tiers/scope. Omit any section above that doesn't apply (e.g., no API Design section for an app with no API) rather than writing "N/A.\""""


    TIER_3_TEMPLATE = f"""You are a Senior Software Architect and Technical Planning Agent.

    Your task is to produce a production-grade implementation plan for the following project.
    {state["user_input"]}

    Design the project as if it were going to be built by a professional software engineering team.

    The document must be detailed enough that another AI coding agent can implement the entire project without additional planning.

    Do NOT write any implementation code.

    Instead, produce a complete software architecture and execution plan.

    # Project Title

    Give the project an appropriate title.

    ---

    # Project Summary

    Explain in 3-6 sentences:

    - What the project does
    - Who it is for
    - Main functionality
    - Overall architecture

    ---

    # Architecture Overview

    Provide a complete folder structure using a tree.

    Example:

    project_name/
    ├── api/
    ├── core/
    ├── ui/
    ├── database/
    ├── utils/
    ├── tests/
    └── main.py

    For every important file or folder, briefly explain its responsibility.

    ---

    # Feature Set

    Create a table with two columns.

    | Feature | Description |

    Include every major feature required for the project.

    ---

    # Proposed Components

    Break the project into logical components.

    For each component include a short description of its responsibility and how it interacts with other components.

    ---

    # API Design (if applicable)

    List endpoints.

    Method

    Route

    Purpose

    Request

    Response

    Authentication requirement

    Example:

    POST /users/login

    GET /tasks

    PUT /tasks/{{id}}

    DELETE /tasks/{{id}}

    ---

    # Database Design (if applicable)

    List tables/models.

    For each model include

    Fields

    Relationships

    Indexes

    Constraints

    ---

    # Technology Stack

    Include

    Programming language

    Backend

    Frontend

    Database

    ORM

    Libraries

    Third-party APIs

    Authentication

    Deployment

    Testing Framework

    Logging

    Configuration

    ---

    # Execution Plan

    Provide a numbered implementation roadmap.

    The steps should be granular.

    Example

    1. Create project structure

    2. Configure environment

    3. Build database models

    4. Implement authentication

    5. Build backend APIs

    6. Implement frontend

    7. Integrate components

    8. Testing

    9. Deployment

    ---

    # User Review Required

    List all assumptions that require confirmation before implementation.

    Example

    - Default country code?
    - Authentication method?
    - Deployment target?
    - Database choice?

    ---

    # Open Questions

    If information is missing, ask concise questions.

    If none, write:

    No open questions.

    ---

    # Output Rules

    Return ONLY valid Markdown.

    Do NOT generate any code.

    Do NOT explain your reasoning.

    Produce a professional implementation specification similar to what a senior software architect would write.

    The document should be detailed enough that another AI agent can immediately begin implementation."""
    print("choosing a template...")
    prompt = f"""You classify a software project request into a planning-document scope tier.
            Output ONLY the TIER_1_TEMPLATE or TIER_2_TEMPLATE or TIER_3_TEMPLATE. No explanation.
    
            TIER 1 — Simple/single-purpose tool. Short request, one core function, no mention of
            scale, multiple users, tenants, or compliance — even if the domain (email, payments,
            scraping, auth) has a "serious" production-grade version in general knowledge.
            The domain does NOT determine the tier. Scope stated by the user does.
    
            TIER 2 — A real app with structure: login, dashboard, API-backed frontend, moderate
            feature set — but no scale/compliance/multi-tenant signals.
    
            TIER 3 — User explicitly said production-grade, scalable, multi-tenant, compliant,
            enterprise, or gave a long, already-detailed spec themselves.
    
            Examples:
            "I want to make a bulk emailer" → 1
            "I want to build a tool to send bulk emails to my newsletter list" → 1
            "build me a CLI that scrapes a site and emails me changes" → 1
            "a web app where users can sign up and track their expenses" → 2
            "an API for a todo app with login" → 2
            "a production-grade multi-tenant bulk email platform with bounce/complaint handling
            and deliverability monitoring for sending millions of emails/month" → 3
            "build a payment system" → 1  (no scale/compliance mentioned — do not assume Stripe-grade infra)
            "build a PCI-compliant multi-merchant payment processing platform" → 3
    
            Request: {user_input}
            output format JSON: {{"tier": 1 or 2 or 3}}"""
    
    response = llm_Grock_simple.invoke(prompt)

    content = response.content

    # Remove model reasoning
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    # Extract the JSON object
    match = re.search(r'\{.*?\}', content, re.DOTALL)

    if not match:
        raise ValueError(f"Could not find tier JSON in response:\n{response.content}")

    tier_data = json.loads(match.group(0))
    tier = tier_data["tier"]

    print("planning...")

    template = None
    if tier == 1:
        template = TIER_1_TEMPLATE
    elif tier == 2:
        template = TIER_2_TEMPLATE
    elif tier == 3:
        template = TIER_3_TEMPLATE
    else:
        raise ValueError("Invalid tier")
    print(f"Using template {tier}")
    
        
    result = llm_nvidia_hardcore.invoke(template)
    text = result.content

    with open("plan.md", "w", encoding="utf-8") as f:
        f.write(text)

    print("Markdown file created!")
    state["plan"] = text
    return state

