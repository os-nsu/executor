import argparse
from cgroup_stats import CgroupStats
from curses_cgroup_stat_printer import CursesCgroupStatPrinter
from cgroup_stat_file_exporter import CgroupStatFileExporter
import threading

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env_name', type=str, required=True, help='environment name')
    parser.add_argument('--cpu', action='store_true', help='CPU usage')
    parser.add_argument('--memory', action='store_true', help='RAM usage')
    parser.add_argument('--disk', action='store_true', help='disk usage')
    parser.add_argument('--syscalls', action='store_true', help='syscall usage')
    # parser.add_argument('--mode', type=str, default='json', help='mode (json | watch)')
    args = parser.parse_args()

    cgroup_stats = CgroupStats(args.env_name)

    # Запуск в отдельном потоке для того, чтобы не блокировать основной поток, который собирает статистику.
    if args.syscalls:
        # thread = threading.Thread(target=cgroup_stats.get_syscall_stats)
        thread = threading.Thread(target=cgroup_stats.get_syscall_stats_with_perf)
        thread.daemon = True
        thread.start()
        print("Syscall stats are starting to print to trace.pid file")

    requested_stats = {key: value for key, value in vars(args).items() if key in ['cpu', 'memory', 'disk']}

    # Статистика выводится в файл, а затем показывается в терминальной сессии.
    if True in requested_stats.values():
        filename = 'stats.json'
        json_builder = CgroupStatFileExporter(cgroup_stats, requested_stats)
        json_builder.save_to_json(filename)
        print(f"The statistics have been saved to a file {filename}")

    printer = CursesCgroupStatPrinter(cgroup_stats, requested_stats)
    printer.show_data()


if __name__ == "__main__":
    main()
