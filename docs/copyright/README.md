# 阅游软著材料说明

本目录存放阅游 V1.1.0 软件著作权申请材料与生成工具。

## 提交材料（PDF，编号命名）

| 文件 | 说明 |
| --- | --- |
| `01_阅游V1.1.0_软件源程序雷同补充说明.pdf` | 源程序雷同情况补充说明（2 页） |
| `02_阅游V1.1.0_独创性说明.pdf` | 软件独创性说明（2 页） |
| `03_阅游V1.1.0_源代码鉴别材料.pdf` | 源代码鉴别材料（前 30 页 + 后 30 页，每页 50 行） |
| `04_阅游V1.1.0_源代码目录清单.pdf` | 全部源代码文件目录清单 |
| `05_阅游V1.1.0_Git提交记录.pdf` | Git 提交记录（开发过程证明） |
| `阅游 V1.1.0 文档鉴别材料.pdf` | 技术设计说明书（文档鉴别材料，13 页） |
| `阅游 V1.1.0 用户手册.pdf` | 用户操作手册（早期版本，保留溯源） |

## 源文档（Markdown，可再生成）

| 文件 | 对应 PDF |
| --- | --- |
| `阅游V1.1.0软件源程序补充说明.md` | 01_ 软件源程序雷同补充说明 |
| `阅游V1.1.0独创性说明.md` | 02_ 独创性说明 |
| `阅游V1.1.0文档鉴别材料.md` | 阅游 V1.1.0 文档鉴别材料 |

## 生成脚本

| 脚本 | 功能 |
| --- | --- |
| `generate_document_pdf.py` | Markdown 渲染器 + 文档鉴别材料 PDF 生成 |
| `generate_source_pdf.py` | 源代码鉴别材料 PDF（扫描 `lib/`、`server/`、`test/`） |
| `generate_supplement_pdf.py` | 软件源程序雷同补充说明 PDF |
| `generate_originality_pdf.py` | 独创性说明 PDF |
| `generate_catalog_pdf.py` | 源代码目录清单 PDF |
| `generate_gitlog_pdf.py` | Git 提交记录 PDF |

## 生成命令

```powershell
python docs/copyright/generate_document_pdf.py     # 文档鉴别材料
python docs/copyright/generate_source_pdf.py       # 源代码鉴别材料
python docs/copyright/generate_supplement_pdf.py   # 雷同补充说明
python docs/copyright/generate_originality_pdf.py  # 独创性说明
python docs/copyright/generate_catalog_pdf.py      # 源代码目录清单
python docs/copyright/generate_gitlog_pdf.py       # Git 提交记录
```

生成文件输出在 `docs/copyright/`，提交软著时按上表编号命名（01-05）归档。

## 提交前注意

- 申请人姓名已填写为“胡传龙”
- 软件名称、版本号、开发完成日期必须与申请表一致
- 源代码鉴别材料要求：前 30 页 + 后 30 页、每页 50 行、覆盖 Flutter 客户端与 Go 服务端
- `screenshots/` 目录存放界面截图，文档鉴别材料据此插入真实截图
- 纸质提交时建议使用 A4 纸单面打印
