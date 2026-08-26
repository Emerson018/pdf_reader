import time
import logging
from typing import Dict, Any, Tuple
import fitz  # PyMuPDF for PDF generation

logger = logging.getLogger(__name__)


class ExportService:
    """Service to format and compile RAG chat answers into downloadable Markdown and PDF reports with citations."""

    @staticmethod
    def generate_report(
        content: str,
        metadata: Dict[str, Any] = None,
        format_type: str = "markdown"
    ) -> Tuple[bytes, str, str]:
        metadata = metadata or {}
        timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        date_filename_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        agent_name = metadata.get("agent", "DocumentAgent")
        search_query = metadata.get("search_query", "Consulta RAG")
        rag_source = metadata.get("rag_source", "PostgreSQL pgvector")
        cache_hit = metadata.get("cache_hit", False)

        # Build Markdown Document Structure
        md_text = f"# 📄 Relatório de Consulta RAG - Plataforma de IA\n\n"
        md_text += f"**Data de Emissão:** {timestamp_str}\n"
        md_text += f"**Agente Responsável:** {agent_name}\n"
        md_text += f"**Fonte de Busca:** {rag_source} {'(⚡ Redis Cache Hit)' if cache_hit else ''}\n"
        md_text += f"**Pergunta / Termo Pesquisado:** *\"{search_query}\"*\n\n"
        md_text += f"---\n\n"
        md_text += f"## 📝 Resposta Gerada pela IA\n\n"
        md_text += f"{content}\n\n"
        md_text += f"---\n\n"
        md_text += f"## 🔍 Fontes e Metadados do Banco de Dados\n\n"
        md_text += f"- **Algoritmo de Busca:** Hybrid Vector + PostgreSQL Full-Text Search (RRF Fusion)\n"
        md_text += f"- **Dimensão do Vetor:** 768D (Gemini Embeddings)\n"

        search_filters = metadata.get("search_filters", {})
        if search_filters:
            md_text += f"- **Filtros Aplicados:** {search_filters}\n"

        if format_type.lower() == "pdf":
            filename = f"Relatorio_RAG_{date_filename_str}.pdf"
            media_type = "application/pdf"

            # Create clean PDF document using PyMuPDF (fitz)
            doc = fitz.open()
            page = doc.new_page()
            rect = page.rect
            margin = 50
            
            # Simple clean text layout for PDF export
            font_size = 10
            line_height = 14
            y = margin

            # Add Header Title
            page.insert_text((margin, y), "Relatorio de Consulta RAG - Plataforma de IA", fontsize=14, color=(0.1, 0.1, 0.4))
            y += 24
            page.insert_text((margin, y), f"Data: {timestamp_str} | Agente: {agent_name}", fontsize=9, color=(0.4, 0.4, 0.4))
            y += 18
            page.insert_text((margin, y), f"Consulta: \"{search_query}\"", fontsize=10, color=(0.2, 0.2, 0.2))
            y += 25

            # Insert body lines
            lines = md_text.split("\n")
            for line in lines:
                if y > rect.height - margin:
                    page = doc.new_page()
                    y = margin

                line_clean = line.replace("**", "").replace("## ", "").replace("# ", "").replace("*", "")
                if line.startswith("#"):
                    page.insert_text((margin, y), line_clean, fontsize=12, color=(0.1, 0.2, 0.5))
                    y += 18
                elif line_clean.strip():
                    # Wrap text if long
                    words = line_clean.split(" ")
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) > 80:
                            page.insert_text((margin, y), current_line, fontsize=font_size, color=(0.1, 0.1, 0.1))
                            y += line_height
                            if y > rect.height - margin:
                                page = doc.new_page()
                                y = margin
                            current_line = word + " "
                        else:
                            current_line += word + " "
                    if current_line:
                        page.insert_text((margin, y), current_line, fontsize=font_size, color=(0.1, 0.1, 0.1))
                        y += line_height

            pdf_bytes = doc.tobytes()
            doc.close()
            return pdf_bytes, filename, media_type
        else:
            filename = f"Relatorio_RAG_{date_filename_str}.md"
            media_type = "text/markdown"
            return md_text.encode("utf-8"), filename, media_type


export_service = ExportService()
