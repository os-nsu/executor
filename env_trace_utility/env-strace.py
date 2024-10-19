import argparse
import os
import sys

from syscall_stat_file_exporter import SyscallStatFileExporter

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


def main():
    args = parse_arguments()
    syscall_stats = SyscallStats(args.tracee)
    # получение статистики в виде словаря
    syscall_stats_dict = syscall_stats.get_stats()
    # получение статистики в виде json-файла
    SyscallStatFileExporter.save_to_json(syscall_stats_dict, args.output_file)


if __name__ == "__main__":
    main()
