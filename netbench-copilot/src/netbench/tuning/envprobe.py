from __future__ import annotations


def env_snapshot_commands() -> list[str]:
    return [
        "lscpu",
        "numactl --hardware",
        "cat /proc/meminfo | grep Huge",
        "ip link show",
    ]
