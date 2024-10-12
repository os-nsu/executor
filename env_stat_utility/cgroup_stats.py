import os


class CgroupStats:
    def __init__(self, name):
        self.name = name

    def get_cpu_usage(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cpu.stat', 'r') as f:
                cpu_usage = {}
                for line in f:
                    if line.startswith('usage_usec'):
                        cpu_usage['usage_usec'] = int(line.split()[1])
                    if line.startswith('user_usec'):
                        cpu_usage['user_usec'] = int(line.split()[1])
                    if line.startswith('system_usec'):
                        cpu_usage['system_usec'] = int(line.split()[1])
                return cpu_usage
        except FileNotFoundError:
            print(f"File cpu.stat not found for cgroup {self.name}")
            return None
        except Exception as e:
            print(f"Error reading cpu usage: {e}")
            return None

    def get_memory_usage(self):
        try:
            memory_usage = {}
            with open(f'/sys/fs/cgroup/{self.name}/memory.current', 'r') as f:
                memory_usage['memory_current'] = int(f.read().strip())
            with open(f'/sys/fs/cgroup/{self.name}/memory.peak', 'r') as f:
                memory_usage['memory_peak'] = int(f.read().strip())
            return memory_usage
        except FileNotFoundError:
            print(f"Memory usage file not found for cgroup {self.name}")
            return None
        except Exception as e:
            print(f"Error reading memory usage: {e}")
            return None

    def get_io_stat(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/io.stat', 'r') as f:
                io_stats = {}
                for line in f:
                    parts = line.split()
                    device = parts[0]
                    io_stats[device] = {}
                    for stat in parts[1:]:
                        key, value = stat.split('=')
                        io_stats[device][key] = int(value)
                return io_stats
        except FileNotFoundError:
            print(f"IO stats file not found for cgroup {self.name}")
            return None
        except Exception as e:
            print(f"Error reading IO stats: {e}")
            return None

    def get_io_pressure(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/io.pressure', 'r') as f:
                io_pressure = {}
                for line in f:
                    if line.startswith("some"):
                        some_data = line.split()
                        io_pressure['some'] = {
                            'avg10': some_data[1].split('=')[1],
                            'avg60': some_data[2].split('=')[1],
                            'avg300': some_data[3].split('=')[1],
                            'total': some_data[4].split('=')[1],
                        }
                    elif line.startswith("full"):
                        full_data = line.split()
                        io_pressure['full'] = {
                            'avg10': full_data[1].split('=')[1],
                            'avg60': full_data[2].split('=')[1],
                            'avg300': full_data[3].split('=')[1],
                            'total': full_data[4].split('=')[1],
                        }
                return io_pressure
        except FileNotFoundError:
            print(f"IO pressure file not found for cgroup {self.name}")
            return None
        except Exception as e:
            print(f"Error reading IO pressure: {e}")
            return None

    def get_syscall_stats(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cgroup.procs', 'r') as f:
                for line in f:
                    traced_pid = line.strip()
                    os.system(f"strace -ff -tt -o trace -p {traced_pid}")
        except FileNotFoundError:
            print(f"cgroup.procs file not found for cgroup {self.name}")
        except Exception as e:
            print(f"Error getting syscall stats: {e}")
