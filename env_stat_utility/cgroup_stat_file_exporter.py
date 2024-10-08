import json


class CgroupStatFileExporter:
    def __init__(self, cgroup_stats, requested_stats):
        self.requested_stats = requested_stats
        self.cgroup_stats = cgroup_stats

    def save_to_json(self, filename):
        try:
            stats_list = {}
            if self.requested_stats['cpu']:
                stats_list['cpu_usage'] = (self.cgroup_stats.get_cpu_usage())
            if self.requested_stats['memory']:
                stats_list['memory_usage'] = (self.cgroup_stats.get_memory_usage())
            if self.requested_stats['disk']:
                disk_usage_list = {"io_stat": self.cgroup_stats.get_io_stat(),
                                   "io_pressure": self.cgroup_stats.get_io_pressure()}
                stats_list['disk_usage'] = disk_usage_list
            with open(filename, 'w') as f:
                f.write(json.dumps(stats_list, indent=4))

        except FileNotFoundError:
            print('File not found')
        except PermissionError:
            print('Permission denied')
