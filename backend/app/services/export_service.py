"""
Export service for book formats
Exports completed books to DOCX, EPUB, PDF, and Markdown
"""

from typing import List
from sqlalchemy.orm import Session
import logging
from pathlib import Path
from datetime import datetime

from docx import Document
from docx.shared import Pt, Inches
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from ebooklib import epub

from app.config import settings
from app.models.project import Project
from app.models.chapter import Chapter

logger = logging.getLogger(__name__)


async def export_to_format(db: Session, project_id: int, format: str) -> str:
    """
    Export project to specified format
    
    Args:
        db: Database session
        project_id: Project ID
        format: Output format (docx, epub, pdf, markdown)
    
    Returns:
        Path to exported file
    """
    # Get project and chapters
    project = db.query(Project).filter(Project.id == project_id).first()
    chapters = db.query(Chapter).filter(
        Chapter.project_id == project_id
    ).order_by(Chapter.number).all()
    
    if not project or not chapters:
        raise ValueError("Project or chapters not found")
    
    # Create output directory
    output_dir = Path(settings.OUTPUT_DIR) / str(project_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    safe_name = "".join(c for c in project.name if c.isalnum() or c in (' ', '-', '_')).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export based on format
    if format == "docx":
        file_path = output_dir / f"{safe_name}_{timestamp}.docx"
        _export_docx(project, chapters, file_path)
    elif format == "epub":
        file_path = output_dir / f"{safe_name}_{timestamp}.epub"
        _export_epub(project, chapters, file_path)
    elif format == "pdf":
        file_path = output_dir / f"{safe_name}_{timestamp}.pdf"
        _export_pdf(project, chapters, file_path)
    elif format == "markdown":
        file_path = output_dir / f"{safe_name}_{timestamp}.md"
        _export_markdown(project, chapters, file_path)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    logger.info(f"Exported project {project_id} to {format}: {file_path}")
    
    return str(file_path)


def _export_docx(project: Project, chapters: List[Chapter], file_path: Path):
    """Export to Microsoft Word DOCX"""
    doc = Document()
    
    # Title page
    title = doc.add_heading(project.name, level=0)
    title.alignment = 1  # Center
    
    doc.add_paragraph()
    doc.add_paragraph(f"Gatunek: {project.genre.value.title()}")
    doc.add_paragraph(f"Wygenerowano: {datetime.now().strftime('%d.%m.%Y')}")
    doc.add_paragraph()
    doc.add_paragraph("Stworzone przez NarraForge")
    doc.add_page_break()
    
    # Chapters
    for chapter in chapters:
        if chapter.content:
            # Chapter title
            doc.add_heading(f"Rozdział {chapter.number}", level=1)
            if chapter.title:
                doc.add_heading(chapter.title, level=2)
            
            # Chapter content
            for paragraph in chapter.content.split('\n\n'):
                if paragraph.strip():
                    doc.add_paragraph(paragraph.strip())
            
            doc.add_page_break()
    
    # Save
    doc.save(file_path)
    logger.info(f"DOCX exported: {file_path}")


def _export_epub(project: Project, chapters: List[Chapter], file_path: Path):
    """Export to EPUB e-book format"""
    book = epub.EpubBook()
    
    # Metadata
    book.set_identifier(f"narraforge_{project.id}")
    book.set_title(project.name)
    book.set_language('pl')
    book.add_author('NarraForge AI')
    
    # Add chapters
    epub_chapters = []
    for chapter in chapters:
        if chapter.content:
            c = epub.EpubHtml(
                title=f"Rozdział {chapter.number}",
                file_name=f"chap_{chapter.number:03d}.xhtml",
                lang='pl'
            )
            
            content = f"<h1>Rozdział {chapter.number}</h1>"
            if chapter.title:
                content += f"<h2>{chapter.title}</h2>"
            
            for paragraph in chapter.content.split('\n\n'):
                if paragraph.strip():
                    content += f"<p>{paragraph.strip()}</p>"
            
            c.content = content
            book.add_item(c)
            epub_chapters.append(c)
    
    # Define TOC
    book.toc = tuple(epub_chapters)
    
    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Spine
    book.spine = ['nav'] + epub_chapters
    
    # Write
    epub.write_epub(file_path, book)
    logger.info(f"EPUB exported: {file_path}")


def _export_pdf(project: Project, chapters: List[Chapter], file_path: Path):
    """Export to PDF"""
    doc = SimpleDocTemplate(str(file_path), pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    chapter_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        alignment=TA_JUSTIFY,
        fontSize=12,
        leading=16
    )
    
    # Build content
    content = []
    
    # Title page
    content.append(Paragraph(project.name, title_style))
    content.append(Spacer(1, 0.2*Inches))
    content.append(Paragraph(f"Gatunek: {project.genre.value.title()}", styles['Normal']))
    content.append(Spacer(1, 0.5*Inches))
    content.append(Paragraph("Stworzone przez NarraForge", styles['Normal']))
    content.append(PageBreak())
    
    # Chapters
    for chapter in chapters:
        if chapter.content:
            content.append(Paragraph(f"Rozdział {chapter.number}", chapter_style))
            if chapter.title:
                content.append(Paragraph(chapter.title, styles['Heading3']))
            
            content.append(Spacer(1, 0.2*Inches))
            
            for paragraph in chapter.content.split('\n\n'):
                if paragraph.strip():
                    content.append(Paragraph(paragraph.strip(), body_style))
                    content.append(Spacer(1, 0.1*Inches))
            
            content.append(PageBreak())
    
    # Build PDF
    doc.build(content)
    logger.info(f"PDF exported: {file_path}")


def _export_markdown(project: Project, chapters: List[Chapter], file_path: Path):
    """Export to Markdown"""
    with open(file_path, 'w', encoding='utf-8') as f:
        # Title
        f.write(f"# {project.name}\n\n")
        f.write(f"**Gatunek:** {project.genre.value.title()}  \n")
        f.write(f"**Wygenerowano:** {datetime.now().strftime('%d.%m.%Y')}  \n")
        f.write(f"**Platforma:** NarraForge\n\n")
        f.write("---\n\n")
        
        # Chapters
        for chapter in chapters:
            if chapter.content:
                f.write(f"## Rozdział {chapter.number}\n\n")
                if chapter.title:
                    f.write(f"### {chapter.title}\n\n")
                
                f.write(chapter.content)
                f.write("\n\n---\n\n")
    
    logger.info(f"Markdown exported: {file_path}")
