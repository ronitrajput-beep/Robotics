"""Create an ordinary-text review copy without changing the faculty form.

Word mobile may not operate the faculty template's content controls. Preserve
the table layout, technical answers and images, and unwrap controls in a new
copy. Unreported personal facts and unobserved peer work are never invented.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {"w": W[1:-1]}
SOURCE = ROOT / "docs/MDRIIA_Group_06_Technical_Dossier.docx"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(text: str, highlight: bool = False) -> E._Element:
    node = E.Element(W + "r")
    props = E.SubElement(node, W + "rPr")
    E.SubElement(props, W + "sz").set(W + "val", "14")
    if highlight:
        E.SubElement(props, W + "highlight").set(W + "val", "yellow")
    value = E.SubElement(node, W + "t")
    value.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    value.text = text
    return node


def paragraph(text: str) -> E._Element:
    node = E.Element(W + "p")
    node.append(run(text))
    return node


def replacements() -> dict[str, tuple[str, str]]:
    result = {
        "M06.S5.video_length": (
            "Simulation segment: 03:21.52, including visible cameras and the "
            "business graph. Face introduction, conclusion and final edited "
            "presentation have not been supplied.",
            "submission/complete_camera_video_v1/VIDEO_CHECKS.json",
        ),
        "M06.S5.live_mujoco": (
            "Yes", "Fresh rendered MuJoCo mission; not slides or a replayed pose trace."
        ),
        "M06.S5.business_graph": (
            "Yes", "Final 12 seconds of the completed camera-inclusive simulation video."
        ),
        "M06.S5.all_members_speak": (
            "Not verified", "No completed three-member face/voice edit supplied."
        ),
        "M06.S5.linkedin_url": (
            "Not supplied", "No public LinkedIn post URL supplied in this conversation."
        ),
    }
    for group in ("M07", "M12"):
        prefix = f"M06.S5.peer_{group}."
        for metric in ("problem", "physics", "business", "data", "clarity"):
            result[prefix + metric] = (
                "Not assessed", "Assigned peer submission/video could not be retrieved; no score inferred."
            )
        result[prefix + "best_moment"] = (
            "Not assessed; video not reviewed.", "No observed video timestamp exists."
        )
    result["M06.S5.peer_M07.question"] = (
        "How does the mobile manipulator detect contact with a patient or "
        "unexpected obstacle and stop safely?",
        "Proposed viva question based only on the assigned project title; not an observed defect.",
    )
    result["M06.S5.peer_M12.question"] = (
        "How is an apparent pipeline defect distinguished from a shadow, and "
        "how is detection confidence validated?",
        "Proposed viva question based only on the assigned project title; not an observed defect.",
    )
    return result


def unresolved(tag: str) -> tuple[str, str]:
    if tag.startswith("M06.SIGN."):
        return "Not confirmed by member", "Personal sign-off/consent cannot be inferred."
    if tag.startswith("M06.S2.script"):
        return (
            "Per-file authorship not confirmed",
            "Project uses AI-assisted implementation. Reported general roles do not establish per-file authorship.",
        )
    return "Not reported", "This individual fact or self-assessment was not supplied."


def build(output: Path) -> Path:
    if output.exists():
        raise FileExistsError(f"Choose a new output directory to preserve existing edits: {output}")
    with ZipFile(SOURCE) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    original = E.fromstring(files["word/document.xml"])
    root = deepcopy(original)
    changes = replacements()
    audit = []
    for control in root.xpath("//w:sdt", namespaces=NS):
        tag = control.find("w:sdtPr/w:tag", NS).get(W + "val")
        content = control.find(W + "sdtContent")
        text = "".join(content.xpath(".//w:t/text()", namespaces=NS))
        options = control.xpath("w:sdtPr/w:dropDownList/w:listItem/@w:displayText", namespaces=NS)
        pending = text in ("Select ▾", "MEMBER TO COMPLETE")
        answer, basis = changes.get(tag, unresolved(tag) if pending else (text, "Existing technical dossier; unchanged."))
        if tag in changes and answer in ("Yes", "No"):
            assert answer in options
        if answer != text:
            for child in list(content):
                content.remove(child)
            content.append(run(answer, pending and basis.startswith("This individual")))
        parent = control.getparent()
        index = parent.index(control)
        for child in list(content):
            parent.insert(index, child)
            index += 1
        parent.remove(control)
        audit.append({"tag": tag, "original_answer": text, "answer": answer,
                      "original_options": options, "basis": basis,
                      "needs_member_input": answer in ("Not reported", "Not confirmed by member", "Per-file authorship not confirmed")})

    # Replace stale instructions in the derivative, keeping the faculty form itself intact.
    for p in root.xpath("//w:p", namespaces=NS):
        text = "".join(p.xpath(".//w:t/text()", namespaces=NS))
        new = None
        if "TECHNICAL REVIEW COPY — member declarations" in text:
            new = text.replace(
                "TECHNICAL REVIEW COPY — member declarations, video, peer reviews and signatures pending.",
                "IPAD TEXT REVIEW COPY — all fields contain an answer or an explicit status; no dropdown controls. Unsigned.",
            )
        elif text.startswith("Technical sections populated from the completed frozen validation"):
            new = (
                "Technical sections are populated from completed frozen validation and the reproducible business scenario. "
                "This separate ordinary-text copy avoids mobile dropdown limitations. Unknown personal facts are marked "
                "Not reported/Not confirmed; unreviewed peer work is Not assessed. These statuses are not selected "
                "rubric answers, and this is not a completed signed submission."
            )
        elif text.startswith("From the group directory, use the pinned Python environment"):
            new = (
                "From the group directory, use the pinned Python environment in requirements.txt. Headless execution "
                "requires MUJOCO_GL=egl before importing MuJoCo. Commands: submission/REPRODUCE.md. Raw final CSVs use XZ. "
                "This derivative uses ordinary editable text; original controls and choices remain in the preserved "
                "faculty Word form. Every original choice and answer is recorded in the companion FIELD_AUDIT.json."
            )
        elif text.startswith("Team: review all technical claims and code;"):
            new = (
                "Team actions still requiring personal completion: confirm unreported hours, individual self-assessments, "
                "per-file authorship and sign-off; provide actual peer-video reviews; record the face/voice portions, "
                "publish the final team video and supply its LinkedIn URL; sign personally and export the final PDF. "
                "No signature, consent, peer score or publication has been fabricated. Faculty/Teams submission is separate."
            )
        if new is not None:
            for child in list(p):
                if child.tag != W + "pPr":
                    p.remove(child)
            p.append(run(new))

    body = root.find(W + "body")
    index = len(body) - (1 if body[-1].tag == W + "sectPr" else 0)
    for text in (
        "Reported team contributions (provided by the user)",
        "Arush (E048): primary 3D modelling, coding and MuJoCo simulation. Ronit (E052): "
        "3D-model assistance and business modelling. Harshvardhan (E058): business modelling and economics. "
        "These project roles do not establish exact hours, commit percentages or individual script authorship.",
        "Current demonstration: submission/complete_camera_video_v1/Group06_Complete_Simulation_With_Cameras.mp4 "
        "(3:21.52). The companion three-person narration script is ready, but actual face/voice footage and a "
        "published LinkedIn URL have not been supplied.",
    ):
        body.insert(index, paragraph(text))
        index += 1

    output.mkdir(parents=True)
    target = output / "Group06_Dossier_iPad_Editable.docx"
    files["word/document.xml"] = E.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for name, data in files.items():
            archive.writestr(name, data)
    assert not root.xpath("//w:sdt", namespaces=NS)
    assert not root.xpath("//w:t[text()='Select ▾' or text()='MEMBER TO COMPLETE']", namespaces=NS)
    assert len(audit) == 212
    assert len(original.xpath("//w:tbl", namespaces=NS)) == len(root.xpath("//w:tbl", namespaces=NS))
    assert len(original.xpath("//w:drawing", namespaces=NS)) == len(root.xpath("//w:drawing", namespaces=NS))
    report = {
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "output_sha256": sha(target), "fields": audit,
        "tables_preserved": len(root.xpath("//w:tbl", namespaces=NS)),
        "images_preserved": len(root.xpath("//w:drawing", namespaces=NS)),
        "no_content_controls": True, "no_dropdown_placeholders": True,
        "peer_review": "Not assessed: at faculty main d5b7da279a034fcd08b090766ef96ed31b196684, both assigned groups' roster video URLs are PENDING_SUBMISSION and their dossier video fields are type here. No marks invented. See PEER_VIDEO_CHECK.json.",
        "status": "Mobile-editable review copy; personal confirmations and actual peer review remain required.",
    }
    (output / "FIELD_AUDIT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    (output / "README.md").write_text(
        "# iPad-editable dossier review copy\n\n"
        "Open Group06_Dossier_iPad_Editable.docx in Word. This copy uses ordinary text, not dropdowns. "
        "The faculty Word template and previous dossier are unchanged.\n\n"
        "Technical answers are retained. Current simulation video details and user-reported team roles are updated. "
        "Unknown hours, self-assessments, per-file authorship and personal sign-off are stated explicitly. "
        "Peer videos were unavailable, so no scores or best-moment timestamps are invented. "
        "Proposed viva questions are based only on the assigned project titles.\n\n"
        "This is an unsigned review copy, not a completed faculty submission. A matching PDF is provided for viewing. "
        "Use the Word copy for edits and re-export after personal confirmations.\n\n"
        "FIELD_AUDIT.json preserves all 212 original tags, original dropdown choices, resulting text and evidence basis. "
        "Rebuild into a new folder with `python submission/build_ipad_dossier.py --output-dir <new-directory>`.\n"
    )
    print(json.dumps({"word": str(target), "fields": len(audit), "tables": report["tables_preserved"], "images": report["images_preserved"]}, indent=2))
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=ROOT / "submission/dossier_ipad_review_v1")
    args = parser.parse_args()
    build(args.output_dir.resolve())
