# OS-Test executor

Директория содержит резличные скрипты для управления окружением, в рамках которого тестируются программы студентов.

## Создание окружения

Окружение позволяет запускать процессы с различными ограничениями, такими как:
1. Количество процессорных ядер;
2. Объем памяти;
3. Скорость чтения/записи с блочного устройства.

За создание и удаление окружения отвечает скрипт: `env-create.py`

В качестве аргументов скрипт должен получить:
1. Название окружения (--env_name);
2. Количество доступных процессорных ядер (--cpu);
3. Количество доступной памяти (--memory);
4. Имя блочного устройства, для которого нужно задать ограничение скорости чтения/записи (--disk_name);
5. Скорость чтения/записи с блочного устройства (--disk_speed).

Каждый аргумент является **обязательным** для создания окружения.

Пример создания окружения с именем `my_env`, количеством доступных ядер процессора `2`, количеством доступной памяти `512 MB`, именем блочного устройства `my_disk` и скоростью чтения записи с блочного устройства `10 MB/sec`:

`python3 env-create.py --env_name my_env --cpu 2 --memory 512 --disk_name my_disk --disk_speed 10`

## Удаление окружения

За удаление окружения отвечает скрипт: `env-destroy.py` с единственным аргументом - именем окружения (--env_name).

Пример удаления окружения с именем my_env:

`python3 env-destroy.py --env_name my_env`

## Ограничение скорости приема/передачи через сетевой интерфейс

За ограничение скорости приема/передачи через сетевой интерфейс отвечает скрипт: `env_speed_ctl.sh`.

В качестве аргументов скрипт должен получить:
1. Имя сетевого интерфейса (-a);
2. Максимальная скорость приема (-d);
3. Максимальная скорость передачи (-u);

Пример ограничения на сетевом интерфейсе `my_iface` скорости приема до `4096 KiB` и скорости передачи до `8192 KiB`:

`env_speed_ctl.sh -a my_iface -d 4096 -u 8192`

Пример снятия ограничений на сетевом интерфейсе `my_iface`:

`env_speed_ctl.sh -c my_iface`

## Создание и удаление виртуального сетевого интерфейса

За создание и удаление виртуальных сетевых интерфейсов отвечает скрипт: `env_net_ctl.sh`.

В качестве аргументов скрипт должен получить:
1. Режим работы (-a): создание (create), удаление (remove);
2. Имя виртуального Ethernet устройства (--veth-name);
3. Имя сетевого неймспейса (--ns-name);
4. IP адреса, назначаемые виртуальному Ethernet устройству (--front-ip и --back-ip). Семантически он представляет из себя "реальный" провод с двумя концам, поэтому IP адресов два.
5. Имя парного Ethernet устройства, через который будет осуществляться маршрутизация трафика (--base-eth).

Пример создания виртуального сетевого интерфейса:

`env_net_ctl.sh -a create --veth-name veth0 --base-eth eth0 --ns-name example0 --front-ip 192.168.0.1 --back-ip 192.168.0.2`

Проверка жизнеспособности:

`ip netns exec example0 ping google.com`

Пример удаления виртуального сетевого интерфейса, созданного выше:

`env_net_ctl.sh -a remove --ns-name example0 --veth-name veth0`

Замечание: Размер маски сети равен 24 битам, поэтому для адресов хостов используются только оставшиеся 8 бит адреса.

## Получение статистики по окружению

Статистика по окружению ведется по следующим контроллерам:
1. cpu\
    Поддерживаются следующие метрики:
    - usage_usec - общее время использования cpu в микросекундах;
    - user_usec - пользовательское время использования cpu в микросекундах;
    - system_usec - системное время использования cpu в микросекундах.
2. memory\
    Поддерживаются следующие метрики:
   - memory_current - общий объем памяти, используемый окружением в данный момент;
   - memory_peak - максимальное использование памяти, записанное для окружения с момента создания окружения.
3. io\
    Контроллер «io» регулирует распределение ресурсов ввода-вывода.\
    Поддерживаются следующие метрики (для каждого блочного устройства):
    - rbytes - прочитано байт;
    - wbytes - записано байт;
    - rios - количество операций ввода-вывода чтения;
    - wios - количество операций ввода-вывода записи;
    - dbytes - байтов отброшено;
    - dios - количество отброшенных операций ввода-вывода.
4. network\
    Сейчас не работает.

За получение статистики по окружению отвечает скрипт: `env-get-stats.py`

В качестве обязательных аргументов скрипт должен получить:
1. Название окружения (--env_name).

Также в качестве опциональных аргументов скрипт может получить следующие контроллеры, по которым выведется статистика:
1. --cpu;
2. --memory;
3. --disk;
4. --network;
5. --interface_name.

Другие опциональные аргументы:
1. Файл вывода (--output или -o);
2. Формат вывода, аналогичный утилите watch (--watch или -w).

Пример получения статистики по окружению `my_env`:

`python3 env-get-stats.py --env_name my_env --cpu --memory --disk --network --interface_name my_iface_name --output stats.json`

## Получение статистики по системным вызовам
За получение статистики по системным вызовам окружения или процесса отвечает скрипт `env_strace.py`

В качестве обязательных аргументов скрипт должен получить следующие аргументы:
1. либо название окружения ('--env_name'), либо идентификатор процесса ('--pid')

Также в качестве опциональных аргументов можно скрипт может получить следующие аргументы:
1. `--output_file` (значение по умолчанию: `syscall_trace.json`)

Пример получения статистики по системным вызовам окружения:

`python3 env-strace.py --env_name my_env --output some_syscall_trace.json`

Пример получения статистики по системным вызовам конкретного процесса и его будущих потомков:

`python3 env-strace.py --pid 12345 --output some_syscall_trace.json`
