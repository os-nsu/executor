import argparse
from cgroup_stats import CgroupStats
from curses_cgroup_stat_printer import CursesCgroupStatPrinter
from cgroup_stat_file_exporter import CgroupStatFileExporter


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env_name', type=str, required=True, help='environment name')
    parser.add_argument('--cpu', action='store_true', help='CPU usage')
    parser.add_argument('--memory', action='store_true', help='RAM usage')
    parser.add_argument('--disk', action='store_true', help='disk usage')

    args = parser.parse_args()

    cgroup_stats = CgroupStats(args.env_name)
    requested_stats = {key: value for key, value in vars(args).items() if key in ['cpu', 'memory', 'disk']}

    # Статистика выводится в файл, а затем показывается в терминальной сессии.
    json_builder = CgroupStatFileExporter(cgroup_stats, requested_stats)
    json_builder.save_to_json("stats.json")

    printer = CursesCgroupStatPrinter(cgroup_stats, requested_stats)
    printer.show_data()


if __name__ == "__main__":
    main()
