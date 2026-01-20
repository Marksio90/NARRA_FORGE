"""
Export service - exports books to various formats.
"""
from pathlib import Path
from typing import Literal
import logging

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

logger = logging.getLogger(__name__)

ExportFormat = Literal['docx', 'pdf', 'epub', 'txt', 'md']


class ExportService:
    """
    Exports books to various formats: DOCX, PDF, EPUB, TXT, Markdown.
    """

    def __init__(self, output_dir: str = "/app/outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def export(self, book, format: ExportFormat) -> str:
        """
        Export book to specified format.

        Args:
            book: Book model
            format: Output format

        Returns:
            Path to exported file
        """
        logger.info(f"Exporting book {book.id} to {format}")

        exporters = {
            'docx': self._export_docx,
            'pdf': self._export_pdf,
            'epub': self._export_epub,
            'txt': self._export_txt,
            'md': self._export_md,
        }

        exporter = exporters.get(format)
        if not exporter:
            raise ValueError(f"Unknown format: {format}")

        return await exporter(book)

    async def _export_docx(self, book) -> str:
        """Export to DOCX."""
        doc = Document()

        # Title
        title = doc.add_heading(book.title or "Bez tytułu", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Subtitle
        if book.subtitle:
            subtitle = doc.add_paragraph(book.subtitle)
            subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Separator
        doc.add_paragraph()
        doc.add_paragraph("─" * 50)
        doc.add_paragraph()

        # Chapters
        for chapter in book.chapters:
            # Chapter heading
            chapter_title = f"Rozdział {chapter.number}"
            if chapter.title:
                chapter_title += f": {chapter.title}"
            doc.add_heading(chapter_title, 1)

            # Content
            paragraphs = chapter.content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph(para.strip())
                    p.paragraph_format.first_line_indent = Inches(0.5)

            # Page break
            doc.add_page_break()

        # Save
        filename = f"{book.id}.docx"
        filepath = self.output_dir / filename
        doc.save(filepath)

        logger.info(f"Exported to DOCX: {filepath}")
        return str(filepath)

    async def _export_txt(self, book) -> str:
        """Export to TXT."""
        content = []

        # Title
        content.append(book.title or "Bez tytułu")
        content.append("=" * len(book.title or "Bez tytułu"))
        content.append("")

        if book.subtitle:
            content.append(book.subtitle)
            content.append("")

        # Chapters
        for chapter in book.chapters:
            content.append(f"ROZDZIAŁ {chapter.number}")
            if chapter.title:
                content.append(chapter.title)
            content.append("-" * 40)
            content.append("")
            content.append(chapter.content)
            content.append("")
            content.append("")

        # Save
        filename = f"{book.id}.txt"
        filepath = self.output_dir / filename
        filepath.write_text("\n".join(content), encoding='utf-8')

        logger.info(f"Exported to TXT: {filepath}")
        return str(filepath)

    async def _export_md(self, book) -> str:
        """Export to Markdown."""
        content = []

        # Title
        content.append(f"# {book.title or 'Bez tytułu'}")
        content.append("")

        if book.subtitle:
            content.append(f"*{book.subtitle}*")
            content.append("")

        content.append("---")
        content.append("")

        # Chapters
        for chapter in book.chapters:
            title = f"## Rozdział {chapter.number}"
            if chapter.title:
                title += f": {chapter.title}"
            content.append(title)
            content.append("")
            content.append(chapter.content)
            content.append("")
            content.append("---")
            content.append("")

        # Save
        filename = f"{book.id}.md"
        filepath = self.output_dir / filename
        filepath.write_text("\n".join(content), encoding='utf-8')

        logger.info(f"Exported to Markdown: {filepath}")
        return str(filepath)

    async def _export_pdf(self, book) -> str:
        """Export to PDF (placeholder - would use reportlab or libreoffice)."""
        # For now, export to DOCX and note that PDF conversion requires additional setup
        docx_path = await self._export_docx(book)
        logger.warning("PDF export not fully implemented - exported to DOCX instead")
        return docx_path

    async def _export_epub(self, book) -> str:
        """Export to EPUB (placeholder - would use ebooklib)."""
        # For now, export to TXT
        txt_path = await self._export_txt(book)
        logger.warning("EPUB export not fully implemented - exported to TXT instead")
        return txt_path
