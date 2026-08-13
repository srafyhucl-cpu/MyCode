"""生成《阅游 V1.1.0》独创性说明 PDF。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generate_document_pdf import (  # noqa: E402
    DocumentPdf,
    OUT_DIR,
    FONT_SIZE,
    _font_path,
    _markdown_to_elements,
    _render_elements,
)

IN_FILE = OUT_DIR / "阅游V1.1.0独创性说明.md"
OUT_FILE = OUT_DIR / "阅游 V1.1.0 独创性说明.pdf"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    content = IN_FILE.read_text(encoding="utf-8-sig")
    elements = _markdown_to_elements(content)

    pdf = DocumentPdf(format="A4")
    pdf.add_font("MicrosoftYaHei", "", str(_font_path()))
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(left=16, top=14, right=16)

    pdf.add_page()
    pdf.set_font("MicrosoftYaHei", "", FONT_SIZE)
    _render_elements(pdf, elements)

    pdf.output(str(OUT_FILE))
    print(f"已生成：{OUT_FILE}")
    print(f"页数：{pdf.page_no()}")


if __name__ == "__main__":
    main()
