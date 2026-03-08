from __future__ import annotations

from netbench.benchmarks.base import BenchmarkAdapter
from netbench.parsing.l3fwd_parser import parse_l3fwd_logs


class L3FwdAdapter(BenchmarkAdapter):
    name = "l3fwd"

    def render_command(self, run_yaml: dict, scenario_key: str) -> list[str]:
        scenario = run_yaml.get("scenarios", {}).get(scenario_key, {})
        eal = run_yaml.get("eal", {})
        core_list = eal.get("core_list", "0-3")
        socket_mem = eal.get("socket_mem", "1024")
        file_prefix = eal.get("file_prefix", "nb")
        port_mask = scenario.get("port_mask", "0x3")
        cmd = (
            "l3fwd "
            f"-l {core_list} --socket-mem {socket_mem} --file-prefix {file_prefix} "
            f"-- -p {port_mask}"
        )
        return [cmd]

    def parse_results(self, log_paths: list[str]) -> tuple[dict, list[str]]:
        return parse_l3fwd_logs(log_paths)
