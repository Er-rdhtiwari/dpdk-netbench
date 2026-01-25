from __future__ import annotations

from netbench.tuning.validators import validate_plan


def test_validate_plan_ok() -> None:
    run_yaml = {
        "benchmark": "cryptoperf",
        "platform": "generic",
        "scenarios": {"scenario_001": {"algorithm": "aes-gcm"}},
        "eal": {"core_list": "0-3", "socket_mem": "1024", "file_prefix": "nb"},
        "logging": {"stdout": "logs/stdout.txt"},
        "env_snapshot_cmds": ["lscpu"],
    }
    tuning_profile = {
        "hugepages": "Use 1G hugepages",
        "irq_affinity": "Pin IRQs",
        "isolcpus": "Use isolcpus",
        "disable_irqbalance": "Disable irqbalance",
        "disable_thp": "Disable THP",
        "kernel_cmdline": "isolcpus,nohz_full,rcu_nocbs",
        "bios": "Requires reboot",
        "verification_cmds": ["grep HugePages /proc/meminfo"],
        "requires_approval": True,
    }
    valid, reasons, fixes = validate_plan(run_yaml, tuning_profile, {})
    assert valid
    assert reasons == []
