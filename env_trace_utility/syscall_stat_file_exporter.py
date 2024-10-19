import json

class SyscallStatFileExporter:
    @staticmethod
    def save_to_json(stats_dict, filename):
        try:
            with open(filename, 'w+') as f:
                f.write(json.dumps(stats_dict, indent='\t'))
        except FileExistsError as e:
            print(f'File exists: {e}')
        except PermissionError as e:
            print(f'Permission denied: {e}')
