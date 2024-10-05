import time
import curses

class CursesPrinter:
    def __init__(self, cgroup_stats, stat_metrics):
        self.stat_metrics = stat_metrics
        self.cgroup_stats = cgroup_stats

    def __display_data(self, screen):
        curses.curs_set(0)
        while True:
            usage_string = []
            screen.clear()
            usage_string.append(f"Usage statistics for cgroup {self.cgroup_stats.name}\n")
            if self.stat_metrics['cpu']:
                usage_string.append(f"Cpu usage: \n{self.cgroup_stats.get_cpu_usage()}\n")
            if self.stat_metrics['memory']:
                usage_string.append(f"Memory usage: \n{self.cgroup_stats.get_memory_usage()}\n")
            if self.stat_metrics['disk']:
                io_stats = self.cgroup_stats.get_io_stat()
                usage_string.append(f"I/O statistics for cgroup {self.cgroup_stats.name}:\n")
                for device, stats in io_stats.items():
                    usage_string.append(f"Device: {device}\n")
                    usage_string.append(f"  Read bytes: {stats.get('rbytes', 0)}\n")
                    usage_string.append(f"  Write bytes: {stats.get('wbytes', 0)}\n")
                    usage_string.append(f"  Read I/O operations: {stats.get('rios', 0)}\n")
                    usage_string.append(f"  Write I/O operations: {stats.get('wios', 0)}\n")
                    usage_string.append(f"  Delayed bytes: {stats.get('dbytes', 0)}\n")
                    usage_string.append(f"  Delayed I/O operations: {stats.get('dios', 0)}\n")

                io_pressure = self.cgroup_stats.get_io_pressure()
                if io_pressure:
                    usage_string.append("I/O pressure:\n")
                    usage_string.append(
                        f"  Some pressure (avg over 10s, 60s, 300s): {io_pressure['some']['avg10']}, {io_pressure['some']['avg60']}, {io_pressure['some']['avg300']}\n")
                    usage_string.append(
                        f"  Full pressure (avg over 10s, 60s, 300s): {io_pressure['full']['avg10']}, {io_pressure['full']['avg60']}, {io_pressure['full']['avg300']}\n")
                    usage_string.append(f"  Total full pressure time: {io_pressure['full']['total']}")

            if self.stat_metrics['network']:
                usage_string.append(f"Network usage: {self.cgroup_stats.get_network_usage()}")

            screen.addstr(''.join(usage_string))
            screen.refresh()
            time.sleep(1)

    def show_data(self):
        try:
            curses.wrapper(self.__display_data)
        except KeyboardInterrupt:
            print("Exiting...")