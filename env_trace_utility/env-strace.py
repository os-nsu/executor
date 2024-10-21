import argparse
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from syscall_stats import SyscallStats


def parse_arguments():
    parser = argparse.ArgumentParser(
        'Syscall tracing utility. You can monitor system calls either in specific processes or processes within a cgroup'
    )

    # mutex group для взаимоисключающих параметров (можем трейсить либо конкретный процесс, либо cgroup)
    mutex_group = parser.add_mutually_exclusive_group()

    # для удобства записываю в переменную tracee с помощью опции dest
    mutex_group.add_argument('--env_name', type=str, dest='tracee', help='environment name')
    mutex_group.add_argument('--pid', '-p', type=int, dest='tracee', help='process id')
    parser.add_argument('--output_file', '-o', type=str, default='syscall_trace.json', help='output file')
    args = parser.parse_args()

    if not args.tracee:
        parser.error('At least one of the arguments must be specified: --env_name or --pid')

    return args


def save_to_json(stats_dict, filename):
    try:
        with open(filename, 'w+') as f:
            f.write(json.dumps(stats_dict, indent='\t'))
    except FileExistsError as e:
        print(f'File exists: {e}')
    except PermissionError as e:
        print(f'Permission denied: {e}')


def main():
    args = parse_arguments()
    syscall_stats = SyscallStats(args.tracee)
    # получение статистики в виде словаря
    syscall_summary_stats = syscall_stats.get_syscall_summary_stats()
    # получение статистики в виде json-файла
    save_to_json(syscall_summary_stats, f"{syscall_stats.trace_output_dir_name}/{args.output_file}")


if __name__ == "__main__":
    main()
