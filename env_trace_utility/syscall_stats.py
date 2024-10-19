import os
import threading

from env_stat_utility.cgroup_stats import CgroupStats


class SyscallStats:
    def __init__(self, name):
        self.name = name

    def __trace_pid(self, pid):
        os.system("mkdir traces")
        ec = os.system(f"strace -f -tt -C -S calls -U name,calls -o traces/{self.name}_trace -p {pid}")
        if ec != 0:
            print(f"Failed to trace pid: {pid}")

    def get_cgroup_pids(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cgroup.procs', 'r') as f:
                cgroup_pids = []
                for line in f:
                    cgroup_pids.append(line.strip())
                return cgroup_pids
        except FileNotFoundError:
            print(f"cgroup.procs file not found for cgroup {self.name}")
            return None
        except Exception as e:
            print(f"Error getting cgroup pids: {e}")
            return None

    def get_syscall_stats(self, requested_pid):
        if requested_pid is not None:
            self.__trace_pid(requested_pid)
        else:
            traced_pids = self.get_cgroup_pids()
            threads = []
            for pid in traced_pids:
                thread = threading.Thread(target=self.__trace_pid, args=(pid,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
