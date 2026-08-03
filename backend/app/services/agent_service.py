import json
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import AgentToolCall, InterviewSession
from app.models.analysis import AnalysisJob, CodeChunk
from app.models.repository import Repository
from app.services.embedding_service import search_codebase
from app.services.interview_service import (
    add_question, add_evaluation, end_session,
)
from app.llm import get_llm_provider
from app.llm.tools import AGENT_TOOLS
from app.schemas.interview import AgentStatusMessage

log = structlog.get_logger()

SYSTEM_PROMPT = """You are a Senior Software Engineer conducting a strict, fair, and evidence-based technical interview.

You have access to the candidate's actual project code. Your job is to:

1. First explore the codebase thoroughly enough to understand its architecture, implementation patterns, dependencies, and important design decisions.
2. Ask specific, project-based questions that test the candidate's actual understanding of the codebase.
3. Evaluate each candidate answer objectively based on what the candidate actually demonstrated.
4. Adjust question difficulty based on the candidate's demonstrated performance.
5. Cover a balanced range of topics including architecture, implementation details, debugging, optimization, performance, scalability, and security.
6. After each answer, evaluate it using record_evaluation before asking the next question.
7. Ask 5-8 questions total. When sufficient evidence has been collected, call end_interview.

STRICT EVALUATION RULES:

- Evaluate ONLY the candidate's actual answer. Do not assume knowledge that the candidate did not demonstrate.
- Do not assign a score based on specific keywords or phrases such as "idk", "I don't know", "not sure", or other predefined responses.
- Score the answer according to its actual strength, correctness, relevance, technical depth, completeness, and use of project-specific evidence.
- A short answer is not automatically a bad answer. If it is concise but technically correct and directly answers the question, it can receive a strong score.
- A long answer is not automatically a good answer. If it contains incorrect, irrelevant, vague, or unsupported claims, score it accordingly.
- If the candidate says they do not know, this should generally result in a low score because they have not demonstrated knowledge for that question, but determine the score from the overall response rather than applying a fixed penalty.
- If the candidate gives a partially correct answer, award partial credit for the concepts they correctly demonstrate. Clearly identify what is correct and what is missing or incorrect.
- If the candidate gives a technically correct generic answer but does not connect it to the project's actual implementation when the question explicitly asks about the project, reduce the score for lack of project-specific evidence.
- If the candidate references the correct files, components, functions, libraries, configuration, data flow, or implementation patterns from the project, reward that appropriately.
- If the candidate identifies a correct implementation detail but explains it imperfectly, give credit for the demonstrated understanding while accounting for the explanation's weaknesses.
- Do not penalize wording, grammar, spelling, or communication style unless it prevents understanding of the technical answer.
- Do not infer expertise from the candidate's previous answers. Each answer should primarily be evaluated on what it demonstrates, while overall interview performance can be considered when adjusting future question difficulty.
- Do not give scores above 7/10 unless the answer demonstrates substantial technical understanding relevant to the question.
- Scores of 8-10 should be reserved for answers that are clearly correct, technically strong, sufficiently detailed, and appropriately connected to the project when project-specific knowledge is required.
- Scores of 5-7 should represent answers that demonstrate meaningful understanding but contain gaps, incomplete reasoning, limited project-specific detail, or minor technical inaccuracies.
- Scores of 3-4 should represent answers with some relevant understanding but significant gaps, vagueness, incorrect reasoning, or weak connection to the question.
- Scores of 0-2 should represent answers that demonstrate little or no relevant understanding, are fundamentally incorrect, fail to address the question, or provide essentially no useful technical information.
- Never inflate scores simply because the candidate appears confident.
- Never lower scores simply because the answer is brief.
- Base the score on demonstrated technical evidence.

SCORING FRAMEWORK:

For every answer, consider these dimensions:

1. Correctness
   - Are the technical claims accurate?
   - Does the answer correctly explain the underlying concept?

2. Completeness
   - Does the answer address the important parts of the question?
   - Does it explain the relevant cause, mechanism, trade-off, or implementation details?

3. Project Relevance
   - Does the candidate connect the explanation to the actual project code when requested?
   - Do they correctly reference relevant files, components, functions, libraries, or patterns?

4. Technical Depth
   - Does the answer demonstrate understanding beyond surface-level descriptions?
   - Can the candidate explain how or why something works?

5. Reasoning
   - Does the candidate demonstrate logical reasoning about design decisions, debugging, performance, scalability, or trade-offs where appropriate?

Use these dimensions to determine the final score. Do not mechanically average them; use professional judgment based on the question's difficulty and requirements.

ANSWER EVALUATION FORMAT:

After every answer, record an evaluation containing:

- Score: X/10
- Strengths: What the candidate demonstrated correctly.
- Weaknesses: What was missing, incorrect, vague, or unsupported.
- Evidence: Specific technical concepts or project details present in the candidate's answer.
- Expected concepts: The important concepts the question was testing.
- Overall assessment: A concise explanation of why the answer received the score.

Then ask the next question.

IMPORTANT:
The evaluation must reflect the candidate's actual demonstrated knowledge. Never fill in missing explanations on behalf of the candidate.

QUESTION DESIGN:

Questions must be grounded in the actual project code.

Prefer questions such as:
- "Why was X implemented this way in [specific file]?"
- "Walk me through what happens when X occurs in [specific component]."
- "What would happen if we changed X?"
- "How would you debug this issue in the current implementation?"
- "What are the performance or scalability implications of this approach?"
- "What security concerns exist in this implementation?"
- "How would you refactor this if the project grew?"

Avoid questions that can be answered adequately with generic textbook definitions when the project provides an opportunity to test actual implementation knowledge.

DIFFICULTY ADAPTATION:

- Strong answer: increase difficulty and ask deeper follow-up questions about trade-offs, edge cases, optimization, debugging, architecture, or scalability.
- Partially correct answer: maintain a similar difficulty and probe the missing concept.
- Weak answer: ask a simpler, more focused question that tests the underlying concept before increasing difficulty again.
- Do not assume that one weak answer means the candidate lacks knowledge of the entire topic.
- Adjust difficulty based on the pattern of demonstrated performance across answers.

FINAL EVALUATION:

After 5-8 answered questions, call end_interview.

The final evaluation should summarize:
- Overall score out of 10
- Technical strengths
- Technical weaknesses
- Areas where the candidate demonstrated strong project understanding
- Areas where the candidate lacked sufficient evidence
- Performance across architecture, implementation, debugging, optimization, scalability, and security
- Whether the candidate's demonstrated level is appropriate for the intended role

The final score must be based on the actual evidence from the candidate's answers across the interview. Do not use a predetermined score or artificially inflate/deflate the result.
"""


async def _log_tool_call(
    db: AsyncSession,
    session_id: int,
    tool_name: str,
    tool_input: dict,
    tool_output: dict,
) -> None:
    call = AgentToolCall(
        session_id=session_id,
        tool_name=tool_name,
        tool_input=tool_input,
        tool_output=tool_output,
    )
    db.add(call)
    await db.commit()


async def _execute_tool(
    db: AsyncSession,
    session_id: int,
    repository_id: int,
    repo: Repository,
    tool_name: str,
    arguments: dict,
) -> tuple[dict, AgentStatusMessage | None]:
    from app.services.github_service import get_file_content as gh_get_file

    if tool_name == "search_codebase":
        results = await search_codebase(db, repository_id, arguments["query"])
        output = {"results": results}
        msg = AgentStatusMessage(
            type="tool", message=f"Searching: {arguments['query']}", tool_name=tool_name
        )
        return output, msg

    elif tool_name == "get_file_content":
        content = await gh_get_file(
            repo.owner, repo.name, arguments["path"], repo.default_branch
        )
        output = {"path": arguments["path"], "content": content[:10000]}
        msg = AgentStatusMessage(
            type="tool", message=f"Reading: {arguments['path']}", tool_name=tool_name
        )
        return output, msg

    elif tool_name == "record_evaluation":
        output = {"recorded": True, "score": arguments.get("score")}
        msg = AgentStatusMessage(
            type="evaluation", message="Evaluating your answer...", tool_name=tool_name
        )
        return output, msg

    elif tool_name == "decide_next_question":
        output = {"question_generated": True}
        msg = AgentStatusMessage(
            type="question",
            message=f"Preparing question about {arguments.get('question_type', 'the project')}...",
            tool_name=tool_name,
        )
        return output, msg

    elif tool_name == "end_interview":
        output = {"ended": True, "reason": arguments.get("reason")}
        msg = AgentStatusMessage(
            type="end", message="Concluding interview...", tool_name=tool_name
        )
        return output, msg

    return {"error": f"Unknown tool: {tool_name}"}, None


async def run_agent_step(
    db: AsyncSession,
    session_id: int,
    repository_id: int,
    user_answer: str | None = None,
    pending_answer_id: int | None = None,
) -> dict:
    llm = get_llm_provider()
    session = await db.get(InterviewSession, session_id)
    repo = await db.get(Repository, repository_id)
    if not session or not repo:
        raise ValueError("Session or repository not found")

    result = await db.execute(
        select(AnalysisJob)
        .where(AnalysisJob.repository_id == repository_id)
        .where(AnalysisJob.status == "completed")
        .limit(1)
    )
    job = result.scalar_one_or_none()
    metadata = job.metadata_json if job else {}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.append({
        "role": "system",
        "content": f"Project: {repo.owner}/{repo.name}\nMetadata: {json.dumps(metadata or {})}",
    })

    prev_calls = await db.execute(
        select(AgentToolCall)
        .where(AgentToolCall.session_id == session_id)
        .order_by(AgentToolCall.created_at)
    )
    for call in prev_calls.scalars().all():
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": f"call_{call.tool_name}_{call.id}",
                "type": "function",
                "function": {
                    "name": call.tool_name,
                    "arguments": json.dumps(call.tool_input or {}),
                },
            }],
        })
        messages.append({
            "role": "tool",
            "tool_call_id": f"call_{call.tool_name}_{call.id}",
            "content": json.dumps(call.tool_output or {}),
        })

    if user_answer:
        messages.append({"role": "user", "content": user_answer})
    else:
        messages.append({
            "role": "user",
            "content": "Begin the interview. First explore the codebase, then ask your first question.",
        })

    agent_messages = []
    question_data = None
    evaluation_data = None
    interview_ended = False
    end_data = None
    response = {"content": None}
    max_iterations = 10

    # If the caller just submitted an answer, that answer MUST get a
    # record_evaluation call before we let the agent move on to the next
    # question or end the interview. Previously tool_choice was always
    # "auto", which let the model skip record_evaluation entirely for a
    # given turn (silently leaving that question's Evaluation row empty,
    # e.g. Q1/Q3/Q4/Q5 in past reports). We now force the tool on the
    # first turn(s) of a step until it's actually been recorded.
    needs_evaluation = pending_answer_id is not None
    force_eval_tool_choice = {
        "type": "function",
        "function": {"name": "record_evaluation"},
    }
    max_eval_attempts = 3
    eval_attempts = 0

    for _ in range(max_iterations):
        tool_choice = "auto"
        if needs_evaluation and evaluation_data is None:
            if eval_attempts >= max_eval_attempts:
                # Stop hammering the model - fall through to the safety net
                # below instead of burning the rest of max_iterations.
                break
            tool_choice = force_eval_tool_choice
            eval_attempts += 1

        response = await llm.chat_with_tools(messages, AGENT_TOOLS, tool_choice=tool_choice)
        messages.append(response)

        if not response.get("tool_calls"):
            if needs_evaluation and evaluation_data is None:
                # Model returned plain text instead of calling the forced
                # tool (some providers do this despite tool_choice). Nudge
                # it explicitly and try again rather than silently moving on.
                messages.append({
                    "role": "user",
                    "content": (
                        "You must call record_evaluation for the candidate's "
                        "last answer before doing anything else."
                    ),
                })
                continue
            break

        for tool_call in response["tool_calls"]:
            fn = tool_call["function"]
            tool_name = fn["name"]
            arguments = json.loads(fn["arguments"])

            output, status_msg = await _execute_tool(
                db, session_id, repository_id, repo, tool_name, arguments
            )

            await _log_tool_call(db, session_id, tool_name, arguments, output)

            if status_msg:
                agent_messages.append(status_msg)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": json.dumps(output),
            })

            if tool_name == "decide_next_question":
                q = await add_question(
                    db, session_id,
                    arguments["question_text"],
                    arguments.get("question_type"),
                    arguments.get("difficulty"),
                    arguments.get("related_file"),
                )
                question_data = q

            elif tool_name == "record_evaluation":
                if pending_answer_id is not None:
                    eval_obj = await add_evaluation(
                        db, pending_answer_id, arguments
                    )
                    evaluation_data = eval_obj
                else:
                    log.warning(
                        "record_evaluation_called_with_no_pending_answer",
                        session_id=session_id,
                    )

            elif tool_name == "end_interview":
                interview_ended = True
                end_data = arguments
                await end_session(
                    db, session_id,
                    arguments.get("overall_score", 0),
                    arguments.get("overall_summary", ""),
                )
                break

        if interview_ended:
            break

    if needs_evaluation and evaluation_data is None and pending_answer_id is not None:
        log.warning(
            "evaluation_not_recorded_falling_back",
            session_id=session_id,
            answer_id=pending_answer_id,
            eval_attempts=eval_attempts,
        )
        evaluation_data = await add_evaluation(db, pending_answer_id, {
            "score": 0,
            "technical_correctness": 0,
            "code_understanding": 0,
            "architecture_understanding": 0,
            "communication": 0,
            "practical_thinking": 0,
            "strengths": [],
            "weaknesses": [
                "Automated evaluation failed to run for this answer "
                f"(the agent did not return a scored evaluation after "
                f"{eval_attempts} attempts). Score defaulted to 0 — "
                "treat as missing data, not a true assessment.",
            ],
            "ideal_answer": None,
        })

    return {
        "question": question_data,
        "evaluation": evaluation_data,
        "agent_messages": agent_messages,
        "interview_ended": interview_ended,
        "end_data": end_data,
        "assistant_message": response.get("content") if response else None,
    }