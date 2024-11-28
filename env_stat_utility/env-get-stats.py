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
    parser.add_argument('--network', action='store_true', help='network usage (bytes transmitted and received)')
    parser.add_argument('--interface_name', type=str, help='virtual network interface name')
    parser.add_argument('-w', '--watch', action='store_true', help='watch mode')
    parser.add_argument('-o', '--output', type=str, default='stats.json', help='output file (.json)')
    args = parser.parse_args()

    if not args.interface_name:
        parser.error(f"Error: the arguments '--interface_name' must be specified together")

    cgroup_stats = CgroupStats(args.env_name, args.interface_name)

    requested_stats = {key: value for key, value in vars(args).items() if key in ['cpu', 'memory', 'disk', 'network']}
    if True in requested_stats.values():
        if args.watch:
            printer = CursesCgroupStatPrinter(cgroup_stats, requested_stats)
            printer.show_data()
        else:
            output_filename = args.output
            json_builder = CgroupStatFileExporter(cgroup_stats, requested_stats)
            json_builder.save_to_json(output_filename)
            print(f"{cgroup_stats.name} statistics have been saved to a file {output_filename}")
    else:
        print("No stats requested")

if __name__ == "__main__":
    main()
