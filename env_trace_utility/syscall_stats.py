import os
import threading


class SyscallStats:
    def __init__(self, tracee):
        self.tracee = tracee

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
        if not os.path.isdir("traces"):
            os.system("mkdir traces")
        ec = os.system(f"strace -f -tt -C -S calls -U name,calls -o traces/trace -p {pid}") # тут придумать специфицированное название файла
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
                cgroup_pids = []
                for line in f:
                    cgroup_pids.append(line.strip())
                return cgroup_pids
        except FileNotFoundError:
            print(f"cgroup.procs file not found for cgroup {self.tracee}")
            return None
        except Exception as e:
            print(f"Error getting cgroup pids: {e}")
            return None

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

    def get_stats(self):
        tracing_stats = {}
        # хотим отследить pid
        if isinstance(self.tracee, int):
            if self.__trace_pid(self.tracee) == 0:
                tracing_stats = self.__get_tracing_stats("traces/trace")
        # хотим отследить cgroup
        elif isinstance(self.tracee, str):
            if self.__trace_cgroup(self.tracee):
                pass
            # TODO: добавить суммарную tracing stats по всем процессам в cgroup
            # в цикле собрать статы по каждому процессу с помощью __get_tracing_stats("traces/trace.pid")
            # просуммировать количество вызовов по каждому сисколу

        return tracing_stats
