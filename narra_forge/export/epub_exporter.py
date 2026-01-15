"""
ePub Exporter for NARRA_FORGE.
Converts narrative outputs to ePub format.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

try:
    from ebooklib import epub
except ImportError:
    epub = None


class EpubExporter:
    """
    Exporter for ePub format.

    Features:
    - Metadata (title, author, language, date)
    - Table of contents
    - Chapters with formatting
    - CSS styling
    - Cover image support (optional)
    """

    def __init__(self):
        if epub is None:
            raise ImportError("ebooklib is required for ePub export. Install: pip install ebooklib")

    def export(
        self,
        narrative_data: Dict[str, Any],
        output_path: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export narrative to ePub format.

        Args:
            narrative_data: Complete narrative data with segments
            output_path: Path where to save the ePub file
            metadata: Optional metadata (title, author, description, etc.)

        Returns:
            Path to created ePub file
        """
        # Create book
        book = epub.EpubBook()

        # Set metadata
        book_metadata = self._prepare_metadata(narrative_data, metadata)
        book.set_identifier(book_metadata['identifier'])
        book.set_title(book_metadata['title'])
        book.set_language(book_metadata['language'])
        book.add_author(book_metadata['author'])

        if 'description' in book_metadata:
            book.add_metadata('DC', 'description', book_metadata['description'])

        # Add CSS style
        style = self._get_default_css()
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style
        )
        book.add_item(nav_css)

        # Create chapters
        chapters = self._create_chapters(narrative_data)

        # Add chapters to book
        for chapter in chapters:
            book.add_item(chapter)

        # Create table of contents
        book.toc = tuple(chapters)

        # Add navigation files
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Create spine (reading order)
        book.spine = ['nav'] + chapters

        # Write ePub file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        epub.write_epub(str(output_path), book, {})

        return str(output_path)

    def _prepare_metadata(
        self,
        narrative_data: Dict[str, Any],
        custom_metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Prepare book metadata."""
        metadata = {
            'identifier': custom_metadata.get('identifier', f'narra-forge-{uuid.uuid4().hex[:8]}') if custom_metadata else f'narra-forge-{uuid.uuid4().hex[:8]}',
            'title': 'Untitled Narrative',
            'author': 'NARRA_FORGE',
            'language': 'pl',
        }

        # Extract from narrative data
        if 'metadata' in narrative_data:
            meta = narrative_data['metadata']
            if 'brief' in meta and hasattr(meta['brief'], 'title'):
                metadata['title'] = meta['brief'].title or metadata['title']

        if 'output' in narrative_data and isinstance(narrative_data['output'], dict):
            if 'title' in narrative_data['output']:
                metadata['title'] = narrative_data['output']['title']

        # Apply custom metadata
        if custom_metadata:
            metadata.update(custom_metadata)

        # Add description from world if available
        if 'metadata' in narrative_data and 'world' in narrative_data['metadata']:
            world = narrative_data['metadata']['world']
            if hasattr(world, 'description'):
                metadata['description'] = world.description[:500]  # Max 500 chars

        return metadata

    def _create_chapters(self, narrative_data: Dict[str, Any]) -> List[epub.EpubHtml]:
        """Create ePub chapters from narrative data."""
        chapters = []

        # Get segments
        segments = self._extract_segments(narrative_data)

        if not segments:
            # Fallback: single chapter with full output
            content = self._extract_full_text(narrative_data)
            chapter = epub.EpubHtml(
                title='Narracja',
                file_name='chapter_01.xhtml',
                lang='pl'
            )
            chapter.content = f'<h1>Narracja</h1><div class="narrative">{self._format_text(content)}</div>'
            chapters.append(chapter)
            return chapters

        # Create chapter for each segment
        for i, segment in enumerate(segments, 1):
            chapter_title = segment.get('title', f'Rozdział {i}')
            chapter_content = segment.get('text', segment.get('content', ''))

            chapter = epub.EpubHtml(
                title=chapter_title,
                file_name=f'chapter_{i:02d}.xhtml',
                lang='pl'
            )

            chapter.content = f'''
                <h1>{chapter_title}</h1>
                <div class="narrative">
                    {self._format_text(chapter_content)}
                </div>
            '''

            chapters.append(chapter)

        return chapters

    def _extract_segments(self, narrative_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract narrative segments from data."""
        # Try different keys where segments might be stored
        if 'output' in narrative_data:
            output = narrative_data['output']

            # Check if output has segments
            if isinstance(output, dict):
                if 'segments' in output:
                    return output['segments']
                elif 'chapters' in output:
                    return output['chapters']

            # Check if output is list of segments
            elif isinstance(output, list):
                return output

        # Check in metadata
        if 'metadata' in narrative_data:
            if 'edited_segments' in narrative_data['metadata']:
                return narrative_data['metadata']['edited_segments']
            elif 'stylized_segments' in narrative_data['metadata']:
                return narrative_data['metadata']['stylized_segments']
            elif 'segments' in narrative_data['metadata']:
                return narrative_data['metadata']['segments']

        return []

    def _extract_full_text(self, narrative_data: Dict[str, Any]) -> str:
        """Extract full narrative text as fallback."""
        if 'output' in narrative_data:
            output = narrative_data['output']

            if isinstance(output, str):
                return output
            elif isinstance(output, dict):
                if 'text' in output:
                    return output['text']
                elif 'content' in output:
                    return output['content']

        return "Brak treści narracji."

    def _format_text(self, text: str) -> str:
        """Format text for HTML."""
        if not text:
            return ""

        # Split by paragraphs and wrap in <p> tags
        paragraphs = text.split('\n\n')
        formatted = []

        for para in paragraphs:
            para = para.strip()
            if para:
                # Handle dialogue
                if para.startswith('—') or para.startswith('–') or para.startswith('-'):
                    formatted.append(f'<p class="dialogue">{para}</p>')
                else:
                    formatted.append(f'<p>{para}</p>')

        return '\n'.join(formatted)

    def _get_default_css(self) -> str:
        """Get default CSS styling for ePub."""
        return """
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Georgia, serif;
    line-height: 1.6;
    margin: 1em;
    text-align: justify;
}

h1 {
    font-size: 2em;
    margin: 1em 0 0.5em 0;
    text-align: center;
    font-weight: bold;
}

h2 {
    font-size: 1.5em;
    margin: 1em 0 0.5em 0;
}

p {
    margin: 0 0 1em 0;
    text-indent: 1.5em;
}

p.dialogue {
    margin-left: 2em;
    font-style: italic;
}

.narrative {
    margin: 2em 0;
}

/* First paragraph no indent */
h1 + .narrative > p:first-child,
h2 + .narrative > p:first-child {
    text-indent: 0;
}
"""
