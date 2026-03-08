from __future__ import annotations

from netbench.benchmarks.base import BenchmarkAdapter
from netbench.parsing.cryptoperf_parser import parse_cryptoperf_logs


class CryptoPerfAdapter(BenchmarkAdapter):
    name = "cryptoperf"

    def render_command(self, run_yaml: dict, scenario_key: str) -> list[str]:
        scenario = run_yaml.get("scenarios", {}).get(scenario_key, {})
        eal = run_yaml.get("eal", {})
        core_list = eal.get("core_list", "0-3")
        socket_mem = eal.get("socket_mem", "1024")
        file_prefix = eal.get("file_prefix", "nb")
        algo = scenario.get("algorithm", "aes-gcm")
        burst = scenario.get("burst_size", 32)
        total_ops = scenario.get("total_ops", 1000000)
        cmd = (
            "dpdk-test-crypto-perf "
            f"-l {core_list} --socket-mem {socket_mem} --file-prefix {file_prefix} "
            f"-- --ptest throughput --cipher-algo {algo} --burst-sz {burst} "
            f"--total-ops {total_ops}"
        )
        return [cmd]

    def parse_results(self, log_paths: list[str]) -> tuple[dict, list[str]]:
        return parse_cryptoperf_logs(log_paths)
