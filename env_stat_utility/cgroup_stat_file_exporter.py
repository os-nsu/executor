import json


class CgroupStatFileExporter:
    @staticmethod
    def save_dict_to_json(cgroup_stats_dictionary, cgroup_stat_output_filename):
        try:
            with open(cgroup_stat_output_filename, 'w+') as f:
                f.write(json.dumps(cgroup_stats_dictionary, indent='\t'))
        except FileExistsError as e:
            print(f'File not found: {e}')
        except PermissionError as e:
            print(f'Permission denied: {e}')
