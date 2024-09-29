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
