import time
import curses
import argparse
from cgroupstats import CgroupStats


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env_name', type=str, required=True, help='environment name')
    parser.add_argument('--cpu', action='store_true', help='CPU usage')
    parser.add_argument('--memory', action='store_true', help='RAM usage')
    parser.add_argument('--disk', action='store_true', help='disk usage')
    parser.add_argument('--network', action='store_true', help='network usage')

    args = parser.parse_args()

    cgroup_stats = CgroupStats(args.env_name)

    def display_data(screen):
        curses.curs_set(0)
        while True:
            usage_string = []
            screen.clear()
            usage_string.append(f"Usage statistics for cgroup {cgroup_stats.name}\n")
            if args.cpu:
                usage_string.append(f"Cpu usage: \n{cgroup_stats.get_cpu_usage()}\n")
            if args.memory:
                usage_string.append(f"Memory usage: \n{cgroup_stats.get_memory_usage()}\n")
            if args.disk:
                io_stats = cgroup_stats.get_io_stat()
                usage_string.append(f"I/O statistics for cgroup {cgroup_stats.name}:\n")
                for device, stats in io_stats.items():
                    usage_string.append(f"Device: {device}\n")
                    usage_string.append(f"  Read bytes: {stats.get('rbytes', 0)}\n")
                    usage_string.append(f"  Write bytes: {stats.get('wbytes', 0)}\n")
                    usage_string.append(f"  Read I/O operations: {stats.get('rios', 0)}\n")
                    usage_string.append(f"  Write I/O operations: {stats.get('wios', 0)}\n")
                    usage_string.append(f"  Delayed bytes: {stats.get('dbytes', 0)}\n")
                    usage_string.append(f"  Delayed I/O operations: {stats.get('dios', 0)}\n")

                io_pressure = cgroup_stats.get_io_pressure()
                if io_pressure:
                    usage_string.append("I/O pressure:\n")
                    usage_string.append(
                        f"  Some pressure (avg over 10s, 60s, 300s): {io_pressure['some']['avg10']}, {io_pressure['some']['avg60']}, {io_pressure['some']['avg300']}\n")
                    usage_string.append(
                        f"  Full pressure (avg over 10s, 60s, 300s): {io_pressure['full']['avg10']}, {io_pressure['full']['avg60']}, {io_pressure['full']['avg300']}\n")
                    usage_string.append(f"  Total full pressure time: {io_pressure['full']['total']}")

            if args.network:
                usage_string.append(f"Network usage: {cgroup_stats.get_network_usage()}")

            screen.addstr(''.join(usage_string))
            screen.refresh()
            time.sleep(1)

    try:
        curses.wrapper(display_data)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()
