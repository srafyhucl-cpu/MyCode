"""导出 git 提交记录为 PDF，作为开发过程证明材料。"""
from __future__ import annotations

import subprocess
import sys
from datetime import date
from pathlib import Path

from fpdf import FPDF

sys.path.insert(0, str(Path(__file__).parent))

from generate_document_pdf import _font_path, _sanitize_for_pdf  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "copyright"
OUT_FILE = OUT_DIR / "阅游 V1.1.0 Git提交记录.pdf"
SOFTWARE_NAME = "阅游 V1.1.0"
APPLICANT = "胡传龙"


class GitLogPdf(FPDF):
    def header(self) -> None:
        self.set_font("MicrosoftYaHei", "", 9)
        self.cell(0, 6, f"{SOFTWARE_NAME} Git 提交记录  第 {self.page_no()} 页", align="C")
        self.ln(7)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("MicrosoftYaHei", "", 8)
        self.cell(0, 6, f"申请人：{APPLICANT}    生成日期：{date.today().isoformat()}", align="C")


def _git_log() -> tuple[list[tuple[str, str, str, str]], int, str, str]:
    """返回 (提交列表, 总数, 最早日期, 最晚日期)。每条 (hash, date, author, subject)。"""
    fmt = "%h|%ad|%an|%s"
    result = subprocess.run(
        ["git", "log", f"--pretty=format:{fmt}", "--date=short"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    commits: list[tuple[str, str, str, str]] = []
    for ln in lines:
        parts = ln.split("|", 3)
        if len(parts) == 4:
            commits.append((parts[0], parts[1], parts[2], parts[3]))
    if not commits:
        return commits, 0, "", ""
    earliest = commits[-1][1]
    latest = commits[0][1]
    return commits, len(commits), earliest, latest


def _git_stat() -> str:
    try:
        result = subprocess.run(
            ["git", "shortlog", "-sn", "--all"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    commits, total, earliest, latest = _git_log()
    shortlog = _git_stat()

    pdf = GitLogPdf(format="A4")
    pdf.add_font("MicrosoftYaHei", "", str(_font_path()))
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.set_margins(left=14, top=14, right=14)
    pdf.add_page()

    pdf.set_font("MicrosoftYaHei", "", 16)
    pdf.cell(0, 10, "阅游 V1.1.0 Git 提交记录", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("MicrosoftYaHei", "", 10)
    pdf.cell(0, 6, f"申请人：{APPLICANT}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"软件名称：{SOFTWARE_NAME}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"生成日期：{date.today().isoformat()}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"提交总数：{total}", new_x="LMARGIN", new_y="NEXT")
    if earliest and latest:
        pdf.cell(0, 6, f"开发周期：{earliest} 至 {latest}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    if shortlog:
        pdf.set_font("MicrosoftYaHei", "", 11)
        pdf.cell(0, 7, "一、贡献者统计（git shortlog）", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("MicrosoftYaHei", "", 9)
        for line in shortlog.splitlines():
            pdf.cell(0, 5.2, _sanitize_for_pdf(line), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    pdf.set_font("MicrosoftYaHei", "", 11)
    pdf.cell(0, 7, "二、提交记录明细（按时间倒序）", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    # 表头
    pdf.set_font("MicrosoftYaHei", "", 8.5)
    pdf.set_fill_color(238, 238, 238)
    pdf.cell(20, 5.5, "Hash", border=1, fill=True, align="C")
    pdf.cell(22, 5.5, "Date", border=1, fill=True, align="C")
    pdf.cell(28, 5.5, "Author", border=1, fill=True, align="C")
    pdf.cell(0, 5.5, "Subject", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("MicrosoftYaHei", "", 8)
    width_subject = pdf.w - pdf.l_margin - pdf.r_margin - 20 - 22 - 28
    for h, d, a, s in commits:
        s_clean = _sanitize_for_pdf(s)
        # 截断超长 subject
        while pdf.get_string_width(s_clean) > width_subject - 2:
            s_clean = s_clean[:-1]
        a_clean = _sanitize_for_pdf(a)
        if pdf.get_string_width(a_clean) > 26:
            while pdf.get_string_width(a_clean + "…") > 26:
                a_clean = a_clean[:-1]
            a_clean += "…"
        pdf.cell(20, 5, h, border=1)
        pdf.cell(22, 5, d, border=1)
        pdf.cell(28, 5, a_clean, border=1)
        pdf.cell(0, 5, s_clean, border=1, new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("MicrosoftYaHei", "", 9)
    pdf.multi_cell(0, 5.5,
        "本文件由 git log 命令导出，可在申请人本地仓库通过 git log --pretty=format:'%h|%ad|%an|%s' --date=short 复现。"
        "提交记录证明本软件自首次提交起即由申请人持续独立开发，具有完整开发过程证据链。"
    )

    pdf.output(str(OUT_FILE))
    print(f"已生成：{OUT_FILE}")
    print(f"页数：{pdf.page_no()}    提交数：{total}")


if __name__ == "__main__":
    main()
