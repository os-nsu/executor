import time
import curses


class CursesCgroupStatPrinter:
    def __init__(self, cgroup_stats, stat_metrics):
        self.requested_stats = stat_metrics
        self.cgroup_stats = cgroup_stats

    def __format_cpu_usage(self, cpu_usage):
        usage_string = []
        usage_string.append(f"  usage_usec: {cpu_usage.get('usage_usec', 0)}")
        usage_string.append(f"  user_usec: {cpu_usage.get('user_usec', 0)}")
        usage_string.append(f"  system_usec: {cpu_usage.get('system_usec', 0)}")
        return usage_string

    def __format_memory_usage(self, memory_usage):
        usage_string = []
        usage_string.append(f"  memory_current: {memory_usage.get('memory_current', 0)}")
        usage_string.append(f"  memory_peak: {memory_usage.get('memory_peak', 0)}")
        return usage_string

    def __format_io_stats(self, io_stats):
        usage_string = []
        for device, stats in io_stats.items():
            usage_string.append(f"Device: {device}")
            usage_string.append(f"  Read bytes: {stats.get('rbytes', 0)}")
            usage_string.append(f"  Write bytes: {stats.get('wbytes', 0)}")
            usage_string.append(f"  Read I/O operations: {stats.get('rios', 0)}")
            usage_string.append(f"  Write I/O operations: {stats.get('wios', 0)}")
            usage_string.append(f"  Delayed bytes: {stats.get('dbytes', 0)}")
            usage_string.append(f"  Delayed I/O operations: {stats.get('dios', 0)}")
        return usage_string

    def __format_io_pressure(self, io_pressure):
        usage_string = []
        usage_string.append(
            f'  Some pressure (avg over 10s, 60s, 300s): {io_pressure['some']['avg10']}, {io_pressure['some']['avg60']}, {io_pressure['some']['avg300']}')
        usage_string.append(
            f'  Full pressure (avg over 10s, 60s, 300s): {io_pressure['full']['avg10']}, {io_pressure['full']['avg60']}, {io_pressure['full']['avg300']}')
        usage_string.append(f'  Total full pressure time: {io_pressure['full']['total']}')
        return usage_string

    def __display_data(self, screen):
        curses.curs_set(0)
        while True:
            usage_string = []
            screen.clear()
            usage_string.append(f'Usage statistics for cgroup {self.cgroup_stats.name}\n')
            if self.requested_stats['cpu']:
                cpu_usage = self.cgroup_stats.get_cpu_usage()
                formated_cpu_usage = '\n'.join(self.__format_cpu_usage(cpu_usage))
                usage_string.append(f'Cpu usage:\n{formated_cpu_usage}\n')
            if self.requested_stats['memory']:
                memory_usage = self.cgroup_stats.get_memory_usage()
                formated_memory_usage = '\n'.join(self.__format_memory_usage(memory_usage))
                usage_string.append(f'\nMemory usage:\n{formated_memory_usage}\n')
            if self.requested_stats['disk']:
                usage_string.append('\nDisk usage:\n')

                io_stats = self.cgroup_stats.get_io_stat()
                formated_io_stats = '\n'.join(self.__format_io_stats(io_stats))
                usage_string.append(f'IO statistics:\n {formated_io_stats}\n')

                io_pressure = self.cgroup_stats.get_io_pressure()
                formated_io_pressure = '\n'.join(self.__format_io_pressure(io_pressure))
                usage_string.append(f'I/O pressure:\n{formated_io_pressure}\n')

            screen.addstr(''.join(usage_string))
            screen.refresh()
            time.sleep(1)

    def show_data(self):
        try:
            curses.wrapper(self.__display_data)
        except curses.error:
            print("Curses error: make sure the window is large enough.")
        except KeyboardInterrupt:
            print('Exiting...')
