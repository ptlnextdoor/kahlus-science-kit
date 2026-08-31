"""
docx/make_docs.py
Example: build one complete ME-report DOCX using helpers.py.
Run: python make_docs.py
Output: ../output/example_report.docx
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from helpers import (
    new_doc, title_block, abstract, section, body,
    bullets, figure, table, references,
)

OUTPUT_DOCX = os.path.join(os.path.dirname(__file__), "..", "output", "example_report.docx")
FIGURES     = os.path.join(os.path.dirname(__file__), "..", "output", "figures")


def build_example():
    os.makedirs(os.path.dirname(OUTPUT_DOCX), exist_ok=True)
    doc = new_doc()

    title_block(
        doc,
        dept        = "DEPARTMENT OF MECHANICAL ENGINEERING",
        institution = "San José State University — Kahlus Research Program",
        title       = "Example Project Report",
        subtitle    = "Demonstrating the Kahlus house style for scientific documents",
        doc_type    = "Technical Project Plan",
        prepared    = "Your Name (Student)",
        submitted   = "Dr. Supervisor, Professor",
        date        = "31 August 2026",
        builds_on   = "kahlus-science-kit repository (github.com/aayushyapatel/kahlus-science-kit).",
    )

    abstract(doc,
        "This document demonstrates every structural element of the Kahlus ME-report house style: "
        "title block, abstract, numbered sections, figures with captions, booktabs tables, "
        "bullet lists, and a numbered reference list. All figures are generated from "
        "make_figures.py using real geometry or synthetic data — no AI-generated images.")

    section(doc, "ex", "Why a programmatic document builder")
    body(doc,
        "Generating documents from Python scripts (rather than typing in Word) means the layout "
        "is reproducible, version-controlled, and free of manual formatting errors. Figures are "
        "also generated programmatically from the same run, so the document and the data are "
        "always in sync.")
    bullets(doc, [
        "Reproducible: re-run the scripts → identical output.",
        "Version-controlled: diff the Python, not the binary.",
        "Consistent: every document shares the same helpers.",
        "Fast: adding a new project is copy-paste of a build function.",
    ])

    section(doc, "ex", "Example figure")
    figure(doc,
           path         = os.path.join(FIGURES, "fig_example_pipeline.png"),
           width_inches = 6.0,
           label        = "Figure 1.",
           cap          = "Pipeline overview. Boxes represent processing stages; the accent-colored "
                          "gate at the right is the claim gate that a result must pass before it "
                          "is reported.")

    section(doc, "ex", "Example table")
    table(doc,
          label  = "Table 1.",
          cap    = "Project index. Spend column is 0 for software-only tracks.",
          header = ["ID", "Project", "Type", "Spend"],
          rows   = [
              ["P01", "Benchmark (software)", "Science", "$0"],
              ["P02", "Pretraining campaign",  "Compute", "$0"],
              ["P03", "Wearable bench",         "Hardware", "~$2,220"],
          ],
          widths = [0.5, 2.8, 1.3, 0.9])

    references(doc, [
        "Author et al., Title of the paper, Journal name, vol. X, pp. Y–Z, year.",
        "kahlus-science-kit repository, github.com/aayushyapatel/kahlus-science-kit.",
    ])

    doc.save(OUTPUT_DOCX)
    print("wrote", OUTPUT_DOCX)


if __name__ == "__main__":
    build_example()
