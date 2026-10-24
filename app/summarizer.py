import io
import httpx
from pypdf import PdfReader

def download_and_extract_pdf_text(pdf_url: str) -> str:
    """Downloads a PDF from a URL and extracts all text content."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = httpx.get(pdf_url, headers=headers, timeout=15, follow_redirects=True)
        if response.status_code == 200:
            pdf_file = io.BytesIO(response.content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text.strip()
    except Exception as e:
        print(f"Error downloading/parsing PDF from {pdf_url}: {e}")
    return ""

def summarize_pdf_notice(pdf_url: str, fallback_title: str) -> str:
    """Extracts text from a PDF notice and generates a concise summary."""
    text = download_and_extract_pdf_text(pdf_url)
    if not text:
        return f"Official notice published regarding {fallback_title}. Click link to view full document."
    
    # Simple extractive summary: Take the first few meaningful lines or sentence block
    lines = [line.strip() for line in text.split("\n") if len(line.strip()) > 30]
    if lines:
        summary_snippet = " ".join(lines[:3]) # Combine first 3 descriptive lines
        if len(summary_snippet) > 300:
            summary_snippet = summary_snippet[:297] + "..."
        return summary_snippet
    
    return f"Detailed notification document available for {fallback_title}."
