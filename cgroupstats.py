import os


class CgroupStats:
    def __init__(self, name):
        self.name = name

    # выводит потребление cpu данной cgroup в виде времени использования процессора (в микросекундах)
    def get_cpu_usage(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cpu.stat', 'r') as f:
                usage_usec = 0  # user_usec + system_usec
                user_usec = 0  # число микросекунд, потраченных на пользовательские задачи
                system_usec = 0  # число микросекунд, потраченных на системные задачи
                for line in f:
                    if line.startswith('usage_usec'):
                        usage_usec = int(line.split()[1])
                    if line.startswith('user_usec'):
                        user_usec = int(line.split()[1])
                    if line.startswith('system_usec'):
                        system_usec = int(line.split()[1])
                return usage_usec, user_usec, system_usec
        except FileNotFoundError:
            print(f"File cpu.stat not found for cgroup {self.name}")
            return None

    def get_memory_usage(self):
        try:
            with open(f'/sys/fs/cgroup/{self.name}/memory.current', 'r') as f:
                memory_current = int(f.read().strip())
            with open(f'/sys/fs/cgroup/{self.name}/memory.max', 'r') as f:
                memory_max = int(f.read().strip())
            return memory_current, memory_max
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

    def get_network_usage(self) -> dict:
        network_usage = {}
        try:
            with open(f"/sys/fs/cgroup/{self.name}/cgroup.procs", 'r') as f:
                pids = [line.strip() for line in f.readlines()]

            for pid in pids:
                try:
                    with open(f"/proc/{pid}/net/dev", 'r') as net_file:
                        for line in net_file.readlines()[2:]:
                            fields = line.split()
                            interface = fields[0].strip(':')
                            receive_bytes = int(fields[1])
                            transmit_bytes = int(fields[9])
                            if interface not in network_usage:
                                network_usage[interface] = {'rx_bytes': 0, 'tx_bytes': 0}
                            network_usage[interface]['rx_bytes'] += receive_bytes
                            network_usage[interface]['tx_bytes'] += transmit_bytes
                except FileNotFoundError:
                    print(f"Network stats for process {pid} not found")
                except Exception as e:
                    print(f"Error reading network usage for process {pid}: {e}")
        except FileNotFoundError:
            print(f"Processes file not found for cgroup {self.name}")
        except Exception as e:
            print(f"Error reading processes file: {e}")

        return network_usage
