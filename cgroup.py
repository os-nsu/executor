import os

CGROUP_MOUNT_PATH = '/sys/fs/cgroup'

class CGroup:
    @staticmethod
    def check_controllers() -> bool:
        print('cgroup mount checking...')

        if not os.path.ismount(CGROUP_MOUNT_PATH):
            print('cgroup is not mounted to /sys/fs')
            return False

        print('done')
        print('all checks ok')
        return True

    def __get_device_major_minor_id(self, device_name):
        try:
            with open(f"/sys/class/block/{device_name}/dev", "r") as f:
                dev_info = f.read().strip()
                return dev_info
        except FileNotFoundError:
            print(f"device {device_name} not found")
            return None
        except Exception as ex:
            print(f"get device info error: {ex}")
            return None

    def __init__(self, name):
        self.name = name

    def created(self) -> bool:
        return os.path.isdir(f"/sys/fs/cgroup/{self.name}")

    def create(self) -> bool:
        if self.created():
            return False

        os.system(f"echo '+cpuset' > /sys/fs/cgroup/cgroup.subtree_control")
        os.system(f"echo '+io' > /sys/fs/cgroup/cgroup.subtree_control")
        os.system(f"mkdir /sys/fs/cgroup/{self.name}")
        return True

    def remove(self):
        os.system(f"rmdir /sys/fs/cgroup/{self.name}")

    def attach_process(self, process_id):
        with open(f"/sys/fs/cgroup/{self.name}/cgroup.procs", 'a+') as f:
            f.write(str(process_id) + '\n')

    def set_disk_rw_speed_limit(self, disk_name, speed_limit):
        device_major_minor_id = self.__get_device_major_minor_id(disk_name)

        with open(f"/sys/fs/cgroup/{self.name}/io.max", 'a+') as f:
            f.write(device_major_minor_id + f' rbps={int(speed_limit) * 1000}')
            f.write(device_major_minor_id + f' wbps={int(speed_limit) * 1000}')
    
    def set_cpu_core_count_limit(self, count):
        with open(f"/sys/fs/cgroup/{self.name}/cpuset.cpus", 'a+') as f:
            f.write(str(count))

    def set_memory_usage_limit(self, limit):
        with open(f"/sys/fs/cgroup/{self.name}/memory.max", 'a+') as f:
            f.write(str(limit) + 'M')


    # выводит потребление cpu данной cgroup в виде времени использования процессора (в микросекундах)
    def get_cpu_usage(self):
        usage_usec = 0   # user_usec + system_usec
        user_usec = 0    # число микросекунд, потраченных на пользовательские задачи
        system_usec = 0  # число микросекунд, потраченных на системные задачи
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cpu.stat', 'r') as f:
                for line in f:
                    if line.startswith('usage_usec'):
                        usage_usec = int(line.split()[1])
                    if line.startswith('user_usec'):
                        user_usec = int(line.split()[1])
                    if line.startswith('system_usec'):
                        system_usec = int(line.split()[1])    
        except FileNotFoundError:
            print(f"File cpu.stat not found for cgroup {self.name}")
        return usage_usec, user_usec, system_usec


    def get_memory_usage(self) -> int:
        try:
            with open(f'/sys/fs/cgroup/{self.name}/memory.current', 'r') as f:
                return int(f.read().strip())
        except FileNotFoundError:
            print(f"Memory usage file not found for cgroup {self.name}")
        except Exception as e:
            print(f"Error reading memory usage: {e}")
            return 0

    def get_io_stat(self):
        io_stat_path = os.path.join(f'/sys/fs/cgroup/{self.name}', 'io.stat')
        io_pressure_path = os.path.join(f'/sys/fs/cgroup/{self.name}', 'io.pressure')
        io_max_path = os.path.join(f'/sys/fs/cgroup/{self.name}', 'io.max')

        if not os.path.exists(io_stat_path):
            print(f"No I/O statistics available for {self.name}")
            return
        
        if not os.path.exists(io_max_path):
            print(f"No I/O max limits set for cgroup {self.name}")
            return

        io_stats = {}
        io_pressure = {}
        io_max = {}
                
        with open(io_max_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                device = parts[0]
                io_max[device] = {}
                for limit in parts[1:]:
                    key, value = limit.split('=')
                    io_max[device][key] = value
            

        with open(io_stat_path, 'r') as f:
            for line in f:
                parts = line.split()
                device = parts[0]
                io_stats[device] = {}
                for stat in parts[1:]:
                    key, value = stat.split('=')
                    io_stats[device][key] = int(value)

        if os.path.exists(io_pressure_path):
            with open(io_pressure_path, 'r') as f:
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
        
        return io_stats, io_pressure, io_max

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
