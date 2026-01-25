from __future__ import annotations

from netbench.tuning.advisor import build_plan_and_tuning


def test_plan_schema_success() -> None:
    retrieved = [
        {"text": "HUGEPAGES: Use 1G hugepages for DPDK where available to reduce TLB pressure."},
        {"text": "IRQ_AFFINITY: Pin IRQs to housekeeping cores separate from dataplane cores."},
        {"text": "ISOLCPUS: Use isolcpus/nohz_full/rcu_nocbs for dataplane cores."},
        {"text": "DISABLE_IRQBALANCE: Disable irqbalance for deterministic latency."},
        {"text": "DISABLE_THP: Disable transparent hugepages for DPDK apps."},
        {"text": "KERNEL_CMDLINE: Use isolcpus,nohz_full,rcu_nocbs for dataplane cores."},
        {"text": "BIOS: Setting SMT off may reduce jitter. Requires reboot."},
        {"text": "VERIFY_CMD: grep HugePages /proc/meminfo"},
    ]
    run_plan, tuning_profile, errors = build_plan_and_tuning(
        "cryptoperf", "generic", "AES-GCM cryptoperf on 4 cores", retrieved
    )
    assert errors == []
    assert run_plan["benchmark"] == "cryptoperf"
    assert tuning_profile["requires_approval"] is True
