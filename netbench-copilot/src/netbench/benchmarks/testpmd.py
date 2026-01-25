from __future__ import annotations

from netbench.benchmarks.base import BenchmarkAdapter
from netbench.parsing.testpmd_parser import parse_testpmd_logs


class TestPmdAdapter(BenchmarkAdapter):
    name = "testpmd"

    def render_command(self, run_yaml: dict, scenario_key: str) -> list[str]:
        scenario = run_yaml.get("scenarios", {}).get(scenario_key, {})
        eal = run_yaml.get("eal", {})
        core_list = eal.get("core_list", "0-3")
        socket_mem = eal.get("socket_mem", "1024")
        file_prefix = eal.get("file_prefix", "nb")
        forward_mode = scenario.get("forward_mode", "io")
        frame_size = scenario.get("frame_size", 64)
        cmd = (
            "testpmd "
            f"-l {core_list} --socket-mem {socket_mem} --file-prefix {file_prefix} "
            f"-- --forward-mode {forward_mode} --txd {frame_size} --rxd {frame_size}"
        )
        return [cmd]

    def parse_results(self, log_paths: list[str]) -> tuple[dict, list[str]]:
        return parse_testpmd_logs(log_paths)
