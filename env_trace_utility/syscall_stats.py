import os
import threading

from env_trace_utility.strace_output_stats_parser import StraceOutputStatsParser


class SyscallStats:
    def __init__(self, tracee):
        self.tracee = tracee
        self.trace_output_dir_name = f"traces/{tracee}_trace_files"

    @staticmethod
    def __run_strace_and_wait(pid, trace_output_file):
        ec = os.system(f"strace -f -tt -C -S calls -U name,calls -o {trace_output_file} -p {pid}")
        if ec != 0:
            print(f"Failed to trace pid: {pid}")
            return -1
        return 0

    def __get_cgroup_pids(self, cgroup_name):
        try:
            with open(f'/sys/fs/cgroup/{cgroup_name}/cgroup.procs', 'r') as f:
                lines = f.readlines()
                cgroup_pids = []
                for line in lines:
                    cgroup_pids.append(line.strip())
                return cgroup_pids
        except FileNotFoundError:
            print(f"cgroup.procs file not found for cgroup {self.tracee}")
            return None
        except Exception as e:
            print(f"Error getting cgroup pids: {e}")
            return None

    def __trace_pids_and_wait_for_completion(self, traced_pids, trace_output_files):
        if not os.path.exists(self.trace_output_dir_name):
            os.system(f"mkdir -p {self.trace_output_dir_name}")

        threads = []

        for i in range(len(traced_pids)):
            pid = traced_pids[i]
            trace_output_file = trace_output_files[i]
            thread = threading.Thread(target=self.__run_strace_and_wait, args=(pid, trace_output_file))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return

    def get_syscall_summary_stats(self):
        if isinstance(self.tracee, str):  # cgroup is traced
            traced_pids = self.__get_cgroup_pids(self.tracee)
        else:  # single pid is traced
            traced_pids = [self.tracee]

        trace_output_files = [f"{self.trace_output_dir_name}/trace_with_forks.{pid}" for pid in traced_pids]

        print(f"Will trace {len(traced_pids)} pids: {traced_pids}")

        self.__trace_pids_and_wait_for_completion(traced_pids, trace_output_files)

        syscall_summary_stats = StraceOutputStatsParser.collect_syscall_summary_stats_from_strace_files(trace_output_files)

        return syscall_summary_stats
