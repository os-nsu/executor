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
