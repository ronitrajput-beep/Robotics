"""Package the business-only reproducible analysis and supporting report."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "submission/business_model_report_v1"


def package():
    checks = json.loads((OUTPUT / "CHECKS.json").read_text())
    assert checks["pass"] and checks["recalculation_matches_retained_results"]
    files = {}
    for name in ["Group06_Business_Model_Report.docx", "Group06_Business_Model_Report.pdf"]:
        files["docs/" + name] = OUTPUT / name
    for name in ["ASSIGNMENT_CHECKLIST.md", "CHECKS.json", "REPORT_SOURCE_MANIFEST.json", "RECALCULATION_CHECK.json", "ASSIGNMENT_SOURCE.json", "FACULTY_RUBRIC_SNAPSHOT.md", "README.md", "requirements-business.txt"]:
        files[name] = (ROOT / "submission/ASSIGNMENT_CHECKLIST.md") if name == "ASSIGNMENT_CHECKLIST.md" else OUTPUT / name
    for name in ["final_business_model.py", "final_business_inputs.json"]:
        files["analytics/" + name] = ROOT / "analytics" / name
    for path in (ROOT / "analytics/final_business_v1").iterdir():
        if path.is_file():
            files[str(path.relative_to(ROOT))] = path
    for name in ["summary.csv", "protocol.json", "statistics.json", "batch_complete.json", "trace_audit.json"]:
        files["analytics/final_validation_v1/" + name] = ROOT / "analytics/final_validation_v1" / name
    files["tests/test_final_business.py"] = ROOT / "tests/test_final_business.py"
    manifest = []
    target = OUTPUT / "Group06_Business_Model_Package.zip"
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for relative, path in sorted(files.items()):
            content = path.read_bytes()
            archive.writestr("Group06_Business_Model/" + relative, content)
            manifest.append({"path": relative, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        archive.writestr("Group06_Business_Model/PACKAGE_MANIFEST.json", json.dumps({"scope": "Business-only report and reproducible analysis; genuine full-batch run summary included; bulk raw telemetry remains in the full project repository.", "files": manifest}, indent=2) + "\n")
    with ZipFile(target) as archive:
        assert archive.testzip() is None
        for item in manifest:
            assert hashlib.sha256(archive.read("Group06_Business_Model/" + item["path"])).hexdigest() == item["sha256"]
    (OUTPUT / "PACKAGE_MANIFEST.json").write_text(json.dumps({"files": manifest, "zip_sha256": hashlib.sha256(target.read_bytes()).hexdigest()}, indent=2) + "\n")
    print(json.dumps({"zip": str(target), "bytes": target.stat().st_size, "files": len(files)}, indent=2))
    return target


if __name__ == "__main__":
    package()
