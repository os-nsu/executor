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

import os
import time

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
        device_path = f'/dev/{device_name}'
    
        try:
            with open(f'/sys/class/block/{device_name}/dev', 'r') as f:
                dev_info = f.read().strip()
                return dev_info
        except FileNotFoundError:
            print(f"Device {device_path} not found")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def __init__(self, name):
        self.name = name

    def created(self) -> bool:
        return os.path.isdir(f'/sys/fs/cgroup/{self.name}')

    def create(self) -> bool:
        if self.created():
            print(f'cgroup create failed, group {self.name} is exist')
            return False

        try:
            os.system(f"echo '+cpuset' > /sys/fs/cgroup/cgroup.subtree_control")
            os.system(f"echo '+io' > /sys/fs/cgroup/cgroup.subtree_control")
            os.system(f"mkdir /sys/fs/cgroup/{self.name}")
        except:
            print(f'cgroup create failed')
            return False

        return True

    def remove(self) -> bool:
        try:
            os.system(f"rmdir /sys/fs/cgroup/{self.name}")
        except:
            print('cgroup remove fail')
            return False

        return True


    def attach_process(self, process_id):
        with open(f"/sys/fs/cgroup/{self.name}/cgroup.procs", 'a+') as f:
            f.write(str(process_id) + '\n')

    def set_disk_rw_speed_limit(self, disk_name, speed_limit):
        device_major_minor_id = self.__get_device_major_minor_id(disk_name)

        with open(f"/sys/fs/cgroup/{self.name}/io.max", 'w') as f:
            f.write(device_major_minor_id + f' rbps={speed_limit}')
        
        with open(f"/sys/fs/cgroup/{self.name}/io.max", 'w') as f:
            f.write(device_major_minor_id + f' wbps={speed_limit}')
    
    def set_cpu_core_count_limit(self, count):
        with open(f"/sys/fs/cgroup/{self.name}/cpuset.cpus", 'w') as f:
            f.write(str(count))

    def set_memory_usage_limit(self, limit):
        with open(f"/sys/fs/cgroup/{self.name}/memory.max", 'w') as f:
            f.write(str(limit) + 'M')

    # выводит потребление cpu каждым ядром
    def __read_proc_stat_per_core(self):
        cpu_times = {}
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('cpu'):
                    parts = line.split()
                    if parts[0] == 'cpu':
                        continue
                    core_id = parts[0]
                    values = list(map(int, parts[1:]))
                    active_time = sum(values)
                    cpu_times[core_id] = active_time
        return cpu_times

    # выводит общее потребление cpu
    def __read_proc_stat(self):
        with open('/proc/stat', 'r') as f:
            for line in f:
                parts = line.split()
                values = list(map(int, parts[1:]))
                total_time = sum(values)
                return total_time

    # выводит потребление cpu данной cgroup
    def __read_cpu_stat(self):
        usage_usec = 0
        try:
            with open(f'/sys/fs/cgroup/{self.name}/cpu.stat', 'r') as f:
                for line in f:
                    # в usage_usec лежит число микросекунд, потраченных на пользовательские и системные задачи
                    if line.startswith('usage_usec'):
                        usage_usec = int(line.split()[1])
                        break
        except FileNotFoundError:
            print(f"File cpu.stat not found for cgroup {self.name}")
        return usage_usec

    # выводит потребление cpu в процентном соотношении
    def get_total_cpu_usage(self):
        clk_tck = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        # рассчитываем сколько микросекунд в одном тике (в /proc/stat время указано в тиках процессора)
        tick_in_microseconds = 1_000_000 / clk_tck # clk_tck - количество тиков в секунде

        cgroup_usage_before = self.__read_cpu_stat()
        cpu_times_before = self.__read_proc_stat()

        time.sleep(1)

        cgroup_usage_after = self.__read_cpu_stat()
        cpu_times_after = self.__read_proc_stat()

        cgroup_usage_diff = cgroup_usage_after - cgroup_usage_before
        cpu_times_diff = cpu_times_after - cpu_times_before

        cpu_percentage = (cgroup_usage_diff / (cpu_times_diff * tick_in_microseconds)) * 100
        return cpu_percentage

    # TODO: нужно найти способ получать статистику на каждое ядро (пока работает некорректно)
    def get_cpu_usage_per_core(self):
        clk_tck = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
        # Рассчитываем сколько микросекунд в одном тике
        tick_in_microseconds = 1_000_000 / clk_tck

        cgroup_usage_before = self.__read_cpu_stat()
        cpu_times_before = self.__read_proc_stat_per_core()

        time.sleep(1)

        cgroup_usage_after = self.__read_cpu_stat()
        cpu_times_after = self.__read_proc_stat_per_core()

        cgroup_usage_diff = cgroup_usage_after - cgroup_usage_before

        cpu_percentages = {}
        for core, (active_before, idle_before) in cpu_times_before.items():
            active_after, idle_after = cpu_times_after[core]
            active_diff = active_after - active_before
            total_diff = active_diff + (idle_after - idle_before)

            if total_diff > 0:
                cpu_percentage = (cgroup_usage_diff / (total_diff * tick_in_microseconds)) * 100
                cpu_percentages[core] = cpu_percentage
        return cpu_percentages

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