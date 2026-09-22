from io import BytesIO
from pathlib import Path
from pypdf import PdfReader

class InputError(ValueError):
    def __init__(self, message, status=422):
        super().__init__(message)
        self.status = status


def validate_text(text, config):
    text = text.strip()
    if len(text) < 20 or sum(c.isalpha() for c in text) < 10:
        raise InputError('No usable text found. Supply a text-based PDF or UTF-8 TXT; scanned PDFs need OCR first.')
    if len(text) > config.max_characters:
        raise InputError(f'Text exceeds {config.max_characters} characters.', 413)
    if '\x00' in text or sum(c.isprintable() or c.isspace() for c in text) / len(text) < .95:
        raise InputError('Text contains unreadable binary content. Supply UTF-8 TXT or a text-based PDF.')
    return text


def parse_document(filename, data, config):
    if len(data) > config.max_file_bytes:
        raise InputError('File exceeds the configured size limit.', 413)
    extension = Path(filename or '').suffix.lower()
    if extension not in {'.txt', '.pdf'}:
        raise InputError('Supported file types are PDF and TXT.', 415)
    if not data:
        raise InputError('The uploaded file is empty.')
    try:
        if extension == '.txt':
            text = data.decode('utf-8-sig')
        else:
            reader = PdfReader(BytesIO(data), strict=False)
            if reader.is_encrypted:
                raise InputError('Encrypted PDFs are unsupported. Upload an unencrypted copy.')
            if len(reader.pages) > config.max_pdf_pages:
                raise InputError('PDF exceeds the configured page limit.', 413)
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or '')
                if sum(map(len, pages)) > config.max_characters:
                    raise InputError('Extracted PDF text exceeds the configured limit.', 413)
            text = '\n'.join(pages)
    except InputError:
        raise
    except Exception as exc:
        raise InputError('Could not read this file. Try a text-based PDF or UTF-8 TXT.') from exc
    return validate_text(text, config)
