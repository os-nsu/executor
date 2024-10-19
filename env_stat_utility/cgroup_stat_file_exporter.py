import json


class CgroupStatFileExporter:
    def __init__(self, cgroup_stats, requested_stats):
        self.requested_stats = requested_stats
        self.cgroup_stats = cgroup_stats

    def save_to_json(self, filename):
        try:
            stats_dict = {}
            if self.requested_stats['cpu']:
                stats_dict['cpu_usage'] = self.cgroup_stats.get_cpu_usage()
            if self.requested_stats['memory']:
                stats_dict['memory_usage'] = self.cgroup_stats.get_memory_usage()
            if self.requested_stats['disk']:
                disk_usage_dict = {"io_stat": self.cgroup_stats.get_io_stat(),
                                   "io_pressure": self.cgroup_stats.get_io_pressure()}
                stats_dict['disk_usage'] = disk_usage_dict
            with open(filename, 'w+') as f:
                f.write(json.dumps(stats_dict, indent='\t'))
        except FileExistsError as e:
            print(f'File not found: {e}')
        except PermissionError as e:
            print(f'Permission denied: {e}')
