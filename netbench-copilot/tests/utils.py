from __future__ import annotations

from pathlib import Path


def build_pdf(path: Path, lines: list[str]) -> None:
    def escape_pdf(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    content_lines = []
    y = 760
    for line in lines:
        content_lines.append(f"BT /F1 11 Tf 50 {y} Td ({escape_pdf(line)}) Tj ET")
        y -= 14
    content = "\n".join(content_lines)

    objects = []
    objects.append("1 0 obj<< /Type /Catalog /Pages 2 0 R>>endobj\n")
    objects.append("2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1>>endobj\n")
    objects.append(
        "3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R>>>>>>endobj\n"
    )
    objects.append(
        f"4 0 obj<< /Length {len(content.encode('utf-8'))} >>stream\n"
        f"{content}\nendstream endobj\n"
    )
    objects.append("5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica>>endobj\n")

    xref_positions = []
    pdf = "%PDF-1.4\n"
    xref_positions.append(0)
    for obj in objects:
        xref_positions.append(len(pdf.encode('utf-8')))
        pdf += obj
    xref_start = len(pdf.encode('utf-8'))
    pdf += "xref\n0 6\n"
    pdf += "0000000000 65535 f \n"
    for pos in xref_positions[1:]:
        pdf += f"{pos:010d} 00000 n \n"
    pdf += "trailer<< /Size 6 /Root 1 0 R>>\n"
    pdf += f"startxref\n{xref_start}\n%%EOF\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pdf.encode("utf-8"))


SAMPLE_LINES = [
    "SECTION: METRICS",
    "METRIC throughput: The rate of packets or bits per second observed during steady state.",
    "METRIC ops_per_sec: The number of crypto operations per second.",
    "METRIC pps: Packets per second measured at the port in forwarding mode.",
    "SECTION: TUNING",
    "HUGEPAGES: Use 1G hugepages for DPDK where available to reduce TLB pressure.",
    "IRQ_AFFINITY: Pin IRQs to housekeeping cores separate from dataplane cores.",
    "ISOLCPUS: Use isolcpus/nohz_full/rcu_nocbs for dataplane cores.",
    "DISABLE_IRQBALANCE: Disable irqbalance for deterministic latency.",
    "DISABLE_THP: Disable transparent hugepages for DPDK apps.",
    "KERNEL_CMDLINE: Use isolcpus,nohz_full,rcu_nocbs for dataplane cores.",
    "VERIFY_CMD: grep HugePages /proc/meminfo",
    "VERIFY_CMD: cat /sys/kernel/mm/transparent_hugepage/enabled",
    "BIOS: Setting SMT off may reduce jitter. Requires reboot.",
]
