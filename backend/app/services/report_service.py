import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.interview import InterviewSession, Question, Answer, Evaluation
from app.models.report import PerformanceReport
from app.models.repository import Repository
from app.services.storage_service import upload_pdf


async def generate_report(db: AsyncSession, session_id: int) -> PerformanceReport:
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(
            selectinload(InterviewSession.questions)
            .selectinload(Question.answer)
            .selectinload(Answer.evaluation),
            selectinload(InterviewSession.repository),
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise ValueError("Interview session not found")

    pdf_bytes = _build_pdf(session)
    object_key = f"reports/{session.user_id}/{session_id}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    backend = await upload_pdf(pdf_bytes, object_key)

    report = PerformanceReport(
        session_id=session_id,
        storage_key=object_key,
        storage_backend=backend,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


def _build_pdf(session: InterviewSession) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        textColor=HexColor("#1a1a2e"), fontSize=22, spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        textColor=HexColor("#16213e"), fontSize=14, spaceAfter=10, spaceBefore=15,
    )
    body_style = styles["BodyText"]

    elements = []
    elements.append(Paragraph("Interview Mirror", title_style))
    elements.append(Paragraph("Performance Report", styles["Heading3"]))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", color=HexColor("#e0e0e0")))
    elements.append(Spacer(1, 12))

    repo = session.repository
    if repo:
        elements.append(Paragraph(f"Repository: {repo.owner}/{repo.name}", body_style))
    elements.append(Paragraph(f"Date: {session.started_at.strftime('%Y-%m-%d %H:%M UTC')}", body_style))
    score_text = f"{session.overall_score:.1f}/10" if session.overall_score else "N/A"
    elements.append(Paragraph(f"Overall Score: {score_text}", heading_style))
    elements.append(Spacer(1, 8))

    if session.summary:
        elements.append(Paragraph("Summary", heading_style))
        elements.append(Paragraph(session.summary, body_style))
        elements.append(Spacer(1, 12))

    scores = []
    for q in session.questions:
        if not q.answer or not q.answer.evaluation:
            continue
        ev = q.answer.evaluation
        scores.append([
            ev.technical_correctness,
            ev.code_understanding,
            ev.architecture_understanding,
            ev.communication,
            ev.practical_thinking,
        ])

    if scores:
        elements.append(Paragraph("Category Averages", heading_style))
        labels = [
            "Technical Correctness", "Code Understanding",
            "Architecture", "Communication", "Practical Thinking",
        ]
        avgs = []
        for i in range(5):
            vals = [s[i] for s in scores if s[i] is not None]
            avg = sum(vals) / len(vals) if vals else 0
            avgs.append(f"{avg:.1f}")
        table_data = [labels, avgs]
        table = Table(table_data, colWidths=[1.3 * inch] * 5)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), HexColor("#16213e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#cccccc")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 16))

    elements.append(Paragraph("Questions &amp; Evaluations", heading_style))
    elements.append(HRFlowable(width="100%", color=HexColor("#e0e0e0")))

    for q in session.questions:
        elements.append(Spacer(1, 10))
        diff = f" [{q.difficulty}]" if q.difficulty else ""
        elements.append(Paragraph(
            f"Q{q.order_index + 1}{diff}: {q.question_text}", heading_style
        ))
        if q.answer:
            elements.append(Paragraph(f"Answer: {q.answer.answer_text}", body_style))
            if q.answer.evaluation:
                ev = q.answer.evaluation
                elements.append(Paragraph(f"Score: {ev.score:.1f}/10", body_style))
                if ev.strengths:
                    elements.append(Paragraph(
                        "Strengths: " + ", ".join(ev.strengths), body_style
                    ))
                if ev.weaknesses:
                    elements.append(Paragraph(
                        "Areas to improve: " + ", ".join(ev.weaknesses), body_style
                    ))
                if ev.ideal_answer:
                    elements.append(Paragraph(
                        f"Ideal answer: {ev.ideal_answer}", body_style
                    ))

    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", color=HexColor("#e0e0e0")))
    elements.append(Paragraph(
        "Generated by Interview Mirror", styles["Italic"]
    ))

    doc.build(elements)
    return buffer.getvalue()