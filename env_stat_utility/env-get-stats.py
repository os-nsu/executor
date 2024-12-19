import argparse

from cgroup_stats import CgroupStats
from curses_cgroup_stat_printer import CursesCgroupStatPrinter
from cgroup_stat_file_exporter import CgroupStatFileExporter


def parse_arguments():
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
        parser.error(f"Error: the argument '--interface_name' is required")

    return args


def collect_cgroup_stats(cgroup_stats, requested_stats):
    stats_dict = {}

    if requested_stats['cpu']:
        stats_dict['cpu_usage'] = cgroup_stats.get_cpu_usage()
    if requested_stats['memory']:
        stats_dict['memory_usage'] = cgroup_stats.get_memory_usage()
    if requested_stats['disk']:
        disk_usage_dict = {"io_stat": cgroup_stats.get_io_stat(),
                           "io_pressure": cgroup_stats.get_io_pressure()}
        stats_dict['disk_usage'] = disk_usage_dict
    if requested_stats['network']:
        stats_dict['network_usage'] = cgroup_stats.get_network_stat()

    return stats_dict


def main():
    args = parse_arguments()

    cgroup_stats = CgroupStats(args.env_name, args.interface_name)

    requested_stats = {key: value for key, value in vars(args).items() if key in ['cpu', 'memory', 'disk', 'network']}
    if True in requested_stats.values():
        if args.watch:
            printer = CursesCgroupStatPrinter(cgroup_stats, requested_stats)
            printer.show_data()
        else:
            stats_dict = collect_cgroup_stats(cgroup_stats, requested_stats)
            output_filename = args.output

            CgroupStatFileExporter.save_dict_to_json(stats_dict, output_filename)
            print(f"{cgroup_stats.name} statistics have been saved to a file {output_filename}")
    else:
        print("No stats requested")

if __name__ == "__main__":
    main()
