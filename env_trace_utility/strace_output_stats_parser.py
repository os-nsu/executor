import os
import threading

class StraceOutputStatsParser:
    # this method does not check for validity of the trace file
    @staticmethod
    def __get_syscall_summary_stats_from_strace_file(trace_file):
        with open(trace_file, 'r') as f:
            summary = {}
            is_summary_block_started = False

            for line in f:
                if not is_summary_block_started:
                    if line.startswith('---'):
                        is_summary_block_started = True
                    continue

                if line.startswith('---'):  # end of summary block
                    break

                syscall_name = line.split()[0]
                syscall_count = int(line.split()[1])
                summary[syscall_name] = syscall_count

        return summary

    @staticmethod
    def collect_syscall_summary_stats_from_strace_files(trace_files):
        result_stats = {}

        for file in trace_files:
            stats_from_pid = StraceOutputStatsParser.__get_syscall_summary_stats_from_strace_file(file)
            for syscall_name, syscall_count in stats_from_pid.items():
                result_stats[syscall_name] = result_stats.get(syscall_name, 0) + syscall_count

        return result_stats
