import os
import threading


class SyscallStats:
    def __init__(self, tracee):
        self.tracee = tracee
        self.dir_name = f"traces/{tracee}_trace_files"
        self.lock = threading.Lock()

    def __get_syscalls_from_trace_file(self, trace_file):
        try:
            with open(trace_file, 'r') as f:
                syscall_dict = {}
                parse = False
                for line in f:
                    if parse:
                        if line.startswith('-'):
                            continue
                        syscall_dict[line.split()[0]] = int(line.split()[1])
                    elif line.startswith('syscall'):
                        parse = True
                return syscall_dict
        except FileNotFoundError:
            print(f"File not found: {trace_file}")
            return None

    def __trace_pid(self, pid):
        # несколько потоков могут одновременно попытаться создать папку, поэтому лочимся
        with self.lock:
            if not os.path.exists(self.dir_name):
                os.system(f"mkdir -p {self.dir_name}")
        trace_filename = f"{self.dir_name}/trace_with_forks.{pid}"
        ec = os.system(f"strace -f -tt -C -S calls -U name,calls -o {trace_filename} -p {pid}")
        if ec != 0:
            print(f"Failed to trace pid: {pid}")
            return -1
        return 0

    def __get_tracing_stats(self, filename):
        syscall_dict = self.__get_syscalls_from_trace_file(filename)
        return syscall_dict

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

    def __summarize_cgroup_syscall_stats(self, traced_pids):
        sum_tracing_stats = {}
        for pid in traced_pids:
            pid_tracing_stats = self.__get_tracing_stats(f"{self.dir_name}/trace_with_forks.{pid}")
            for key, value in pid_tracing_stats.items():
                sum_tracing_stats[key] = sum_tracing_stats.get(key, 0) + value
        return sum_tracing_stats

    def __trace_cgroup(self, cgroup_name):
        traced_pids = self.__get_cgroup_pids(cgroup_name)
        if traced_pids is None:
            print(f"No pids found for cgroup {cgroup_name}")
            return None
        threads = []
        for pid in traced_pids:
            thread = threading.Thread(target=self.__trace_pid, args=(pid,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        return self.__summarize_cgroup_syscall_stats(traced_pids)

    def get_stats(self):
        tracing_stats = {}
        if isinstance(self.tracee, int):
            if self.__trace_pid(self.tracee) == 0:
                tracing_stats = self.__get_tracing_stats(f"{self.dir_name}/trace_with_forks.{self.tracee}")
        elif isinstance(self.tracee, str):
            tracing_stats = self.__trace_cgroup(self.tracee)
        return tracing_stats
