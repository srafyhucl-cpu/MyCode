from __future__ import annotations

from datetime import date
from pathlib import Path
import re

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "docs" / "copyright"
OUT_FILE = OUT_DIR / "阅游 V1.1.0 源代码鉴别材料.pdf"
SOFTWARE_NAME = "阅游 V1.1.0"
APPLICANT = "胡传龙"
LINES_PER_PAGE = 50
TOTAL_PAGES = 60
FONT_SIZE = 7
MAX_LINE_CHARS = 108
SECTION_LINES = LINES_PER_PAGE * (TOTAL_PAGES // 2)
SOURCE_PATTERNS = [
    # 1. 最核心独创业务逻辑：游戏 + TTS总控
    "lib/features/game_2048/providers/game_provider.dart",
    "lib/features/audio/services/sfx_service.dart",
    "lib/features/audio/services/tts_engine_service.dart",
    "lib/features/audio/providers/tts_audio_notifier.dart",
    "lib/features/reader/domain/text_parser.dart",
    "lib/features/reader/presentation/widgets/teleprompter_view.dart",
    # 2. 音频/TTS拆分模块
    "lib/features/audio/services/tts_audio_adapters.dart",
    "lib/features/audio/services/tts_audio_downloader.dart",
    "lib/features/audio/services/tts_audio_janitor.dart",
    "lib/features/audio/services/tts_diagnostics_service.dart",
    "lib/features/audio/services/tts_http_client.dart",
    "lib/features/audio/domain/*.dart",
    # 3. 阅读器相关模块
    "lib/features/reader/domain/*.dart",
    "lib/features/reader/presentation/**/*.dart",
    # 4. 其他正式业务功能
    "lib/features/library/**/*.dart",
    "lib/features/game_2048/**/*.dart",
    "lib/features/settings/**/*.dart",
    "lib/features/dashboard/**/*.dart",
    "lib/features/update/**/*.dart",
    "lib/shared/**/*.dart",
    # 5. 基础设施与入口
    "lib/core/config/*.dart",
    "lib/core/constants/*.dart",
    "lib/core/utils/*.dart",
    "lib/core/database/*.dart",
    "lib/main.dart",
    # 阅读器总控（压在服务端之前，确保进入后30页尾段）
    "lib/features/reader/providers/reader_provider.dart",
    # 6. Go 服务端正式业务代码压尾
    "server/main.go",
    "server/config.go",
    "server/response.go",
    "server/handler_tts.go",
    "server/handler_book.go",
    # 7. 测试代码仅作为最后补充，正常情况下不纳入
    # "test/features/audio/tts_contract_test.dart",
    # "test/features/game_2048/game_provider_test.dart",
    # "test/features/reader/text_parser_test.dart",
]
FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simsun.ttc"),
]
EMOJI_PATTERN = re.compile(
    "["
    "\\U0001F300-\\U0001FAFF"
    "\\U00002700-\\U000027BF"
    "\\U00002600-\\U000026FF"
    "\\uFE0F"
    "]+"
)


def _ordered_files() -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for pattern in SOURCE_PATTERNS:
        matches = sorted(ROOT.glob(pattern), key=lambda p: p.as_posix())
        for file in matches:
            if file.is_file() and file not in seen:
                files.append(file)
                seen.add(file)
    return files


def _wrap_line(raw: str) -> list[str]:
    """超长行拆为多个子行，续行加·前缀。"""
    if len(raw) <= MAX_LINE_CHARS:
        return [raw]
    sub: list[str] = [raw[:MAX_LINE_CHARS]]
    rest = raw[MAX_LINE_CHARS:]
    while rest:
        chunk = rest[:MAX_LINE_CHARS - 3]
        sub.append("\u00b7  " + chunk)
        rest = rest[MAX_LINE_CHARS - 3:]
    return sub


def _read_source_lines(file: Path) -> list[str]:
    relative = file.relative_to(ROOT).as_posix()
    lines: list[str] = []
    lines.append(f"// ===== 文件：{relative} =====")
    content = file.read_text(encoding="utf-8", errors="replace").splitlines()
    for index, line in enumerate(content, start=1):
        stripped = line.rstrip()
        if stripped:
            raw = f"{index:04d}  {stripped}"
            lines.extend(_wrap_line(raw))
    lines.append(f"// ===== 文件结束：{relative} =====")
    lines.append("")
    return lines


def _collect_all_lines(files: list[Path]) -> list[str]:
    """收集所有源文件的非空行（含文件标题行）。"""
    all_lines: list[str] = []
    for file in files:
        all_lines.extend(_read_source_lines(file))
    return all_lines


def _select_material(all_lines: list[str]) -> tuple[list[str], bool]:
    """
    决定输出内容：
    - 总行数 ≤ 60×50=3000：直接返回全部行，返回 False（不足60页）。
    - 总行数 > 3000：返回前1500行 + 后1500行（不重叠），返回 True。
    """
    total_capacity = TOTAL_PAGES * LINES_PER_PAGE  # 3000
    half = total_capacity // 2  # 1500

    if len(all_lines) <= total_capacity:
        return all_lines, False

    head = all_lines[:half]
    tail_start = max(half, len(all_lines) - half)
    tail = all_lines[tail_start:]
    return head + tail, True


def _slice_pages(lines: list[str]) -> list[list[str]]:
    """将行列表按 LINES_PER_PAGE 分页，最后一页不足时保留实际行数，不填充空行。"""
    pages: list[list[str]] = []
    for i in range(0, len(lines), LINES_PER_PAGE):
        pages.append(lines[i:i + LINES_PER_PAGE])
    return pages


class SourcePdf(FPDF):
    def header(self) -> None:
        self.set_font("MicrosoftYaHei", "", 9)
        self.cell(0, 6, f"{SOFTWARE_NAME} 源代码鉴别材料  第 {self.page_no()} 页", align="C")
        self.ln(8)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("MicrosoftYaHei", "", 8)
        self.cell(0, 6, f"申请人：{APPLICANT}    生成日期：{date.today().isoformat()}", align="C")


def _font_path() -> Path:
    for font in FONT_CANDIDATES:
        if font.exists():
            return font
    raise FileNotFoundError("未找到中文字体，请安装微软雅黑或宋体。")


def _sanitize_for_pdf(text: str) -> str:
    return EMOJI_PATTERN.sub("", text).replace("•", "-").replace("\t", "    ")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = _ordered_files()
    all_lines = _collect_all_lines(files)
    total_pages_all = (len(all_lines) + LINES_PER_PAGE - 1) // LINES_PER_PAGE
    material, is_over_60 = _select_material(all_lines)
    if is_over_60:
        notice = (
            f"说明：本软件完整源程序经整理共{total_pages_all}页。"
            "现根据软件功能主次排序后，按照软件著作权登记源程序鉴别材料要求，"
            "提交连续前30页和连续后30页，共60页。每页不少于50行。"
        )
        material = [notice] + material[:len(material) - 1]
    pages = _slice_pages(material)

    pdf = SourcePdf(format="A4")
    font_path = _font_path()
    pdf.add_font("MicrosoftYaHei", "", str(font_path))
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(left=12, top=12, right=12)

    for page in pages:
        pdf.add_page()
        pdf.set_font("MicrosoftYaHei", "", FONT_SIZE)
        for line in page:
            pdf.cell(0, 4.9, _sanitize_for_pdf(line), new_x="LMARGIN", new_y="NEXT")

    if not is_over_60:
        pdf.add_page()
        pdf.set_font("MicrosoftYaHei", "", 10)
        pdf.ln(40)
        note = "源程序不足60页，已提交全部源码。"
        pdf.cell(0, 10, note, align="C")

    pdf.output(str(OUT_FILE))
    total_pages = len(pages) + (0 if is_over_60 else 1)
    print(f"已生成：{OUT_FILE}")
    print(f"页数：{total_pages}")
    if not is_over_60:
        print("注：源程序不足60页，已提交全部源码。")


if __name__ == "__main__":
    main()
