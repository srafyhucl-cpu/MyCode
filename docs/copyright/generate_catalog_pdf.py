"""自动扫描全部源代码文件，生成《阅游 V1.1.0》源代码目录清单 PDF。"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

from fpdf import FPDF

sys.path.insert(0, str(Path(__file__).parent))

from generate_document_pdf import _font_path  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "copyright"
OUT_FILE = OUT_DIR / "阅游 V1.1.0 源代码目录清单.pdf"
SOFTWARE_NAME = "阅游 V1.1.0"
APPLICANT = "胡传龙"

# 扫描根目录下的源代码：客户端 lib/，服务端 server/，测试 test/
SCAN_DIRS = [
    ("lib", "*.dart"),
    ("server", "*.go"),
    ("test", "*.dart"),
]
EXCLUDE_PARTS = {".dart_tool", "build", ".idea", "__pycache__"}


class CatalogPdf(FPDF):
    def header(self) -> None:
        self.set_font("MicrosoftYaHei", "", 9)
        self.cell(0, 6, f"{SOFTWARE_NAME} 源代码目录清单  第 {self.page_no()} 页", align="C")
        self.ln(7)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("MicrosoftYaHei", "", 8)
        self.cell(0, 6, f"申请人：{APPLICANT}    生成日期：{date.today().isoformat()}", align="C")


def _count_lines(path: Path) -> tuple[int, int]:
    """返回 (总行数, 非空行数)。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return 0, 0
    lines = text.splitlines()
    non_empty = sum(1 for ln in lines if ln.strip())
    return len(lines), non_empty


def _scan_files() -> list[tuple[Path, int, int]]:
    results: list[tuple[Path, int, int]] = []
    for sub, pattern in SCAN_DIRS:
        base = ROOT / sub
        if not base.exists():
            continue
        for path in sorted(base.rglob(pattern)):
            if any(part in EXCLUDE_PARTS for part in path.parts):
                continue
            total, non_empty = _count_lines(path)
            results.append((path, total, non_empty))
    return results


def _group_files(files: list[tuple[Path, int, int]]) -> dict[str, list[tuple[Path, int, int]]]:
    groups: dict[str, list[tuple[Path, int, int]]] = {}
    for path, total, non_empty in files:
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("lib/features/"):
            parts = rel.split("/")
            group_name = f"lib/features/{parts[2]}"
        elif rel.startswith("lib/core/"):
            parts = rel.split("/")
            group_name = f"lib/core/{parts[2]}" if len(parts) > 3 else "lib/core"
        elif rel.startswith("lib/shared/"):
            group_name = "lib/shared"
        elif rel.startswith("lib/"):
            group_name = "lib（根目录）"
        elif rel.startswith("server/"):
            group_name = "server（Go 服务端）"
        elif rel.startswith("test/"):
            group_name = "test（自动化测试）"
        else:
            group_name = "其他"
        groups.setdefault(group_name, []).append((path, total, non_empty))
    return groups


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = _scan_files()
    groups = _group_files(files)

    total_files = len(files)
    total_lines = sum(t for _, t, _ in files)
    total_non_empty = sum(n for _, _, n in files)

    pdf = CatalogPdf(format="A4")
    pdf.add_font("MicrosoftYaHei", "", str(_font_path()))
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(left=14, top=14, right=14)
    pdf.add_page()

    # 标题
    pdf.set_font("MicrosoftYaHei", "", 16)
    pdf.cell(0, 10, "阅游 V1.1.0 源代码目录清单", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # 概览
    pdf.set_font("MicrosoftYaHei", "", 10)
    pdf.cell(0, 6, f"申请人：{APPLICANT}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"软件名称：{SOFTWARE_NAME}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"生成日期：{date.today().isoformat()}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"源代码文件总数：{total_files}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"源代码总行数：{total_lines}（含空行）", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"源代码非空行数：{total_non_empty}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # 各分组明细
    pdf.set_font("MicrosoftYaHei", "", 11)
    pdf.cell(0, 7, "二、源代码文件分组明细", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # 按分组顺序：先 lib/features，再 lib/core，再 lib/shared，再 server，再 test
    sort_priority = [
        "lib/features/",
        "lib/core/",
        "lib/shared",
        "lib（根目录）",
        "server",
        "test",
        "其他",
    ]

    def _group_sort_key(name: str) -> tuple[int, str]:
        for idx, prefix in enumerate(sort_priority):
            if name.startswith(prefix):
                return (idx, name)
        return (999, name)

    for group_name in sorted(groups.keys(), key=_group_sort_key):
        files_in_group = groups[group_name]
        group_total = sum(t for _, t, _ in files_in_group)
        group_non_empty = sum(n for _, _, n in files_in_group)

        pdf.set_font("MicrosoftYaHei", "", 10)
        pdf.set_fill_color(238, 238, 238)
        title = f"  {group_name}  （{len(files_in_group)} 个文件 · {group_total} 行 · 非空 {group_non_empty} 行）"
        pdf.cell(0, 6.4, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

        pdf.set_font("MicrosoftYaHei", "", 8.5)
        for path, total, non_empty in files_in_group:
            rel = path.relative_to(ROOT).as_posix()
            line = f"    {rel}    [{total} 行 / 非空 {non_empty} 行]"
            # 长路径自动换行
            width = pdf.w - pdf.l_margin - pdf.r_margin
            if pdf.get_string_width(line) > width:
                # 尝试折行
                pdf.cell(0, 5, f"    {rel}", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(0, 5, f"        [{total} 行 / 非空 {non_empty} 行]", new_x="LMARGIN", new_y="NEXT")
            else:
                pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    # 末尾声明
    pdf.ln(2)
    pdf.set_font("MicrosoftYaHei", "", 10)
    pdf.multi_cell(0, 6,
        "声明：以上为本软件全部源代码文件目录清单，已按业务模块分组列出文件路径与行数统计。"
        "完整源代码文件可应审查人员要求另行提交。"
    )

    pdf.output(str(OUT_FILE))
    print(f"已生成：{OUT_FILE}")
    print(f"页数：{pdf.page_no()}    文件数：{total_files}    总行数：{total_lines}")


if __name__ == "__main__":
    main()
