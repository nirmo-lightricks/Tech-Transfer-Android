import logging
from os import environ, kill
from signal import SIGKILL
from subprocess import run, TimeoutExpired
TIMEOUT_STOP_EMULATORS = 90

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def adb_command() -> str:
    adb_home = environ['ADB_HOME']
    return f'{adb_home}/adb'


def get_emulator_list(timeout_seconds: int) -> str:
    res = run([adb_command(), 'devices'], capture_output=True,
              text=True, timeout=timeout_seconds)
    return [line.split()[0]
            for line in res.stdout.split('\n') if 'emulator' in line]

# killing brutal is just a last resort because we essentially are throwing a 1000Kg hammer on the emulator
# it means just exit without saving internal state, etc


def kill_brutal():
    logging.info('killing all emulators')
    ps_res = run(['ps', '-e'], capture_output=True, text=True)
    pid_list = [int(line.split()[0]) for line in ps_res.stdout.split(
        '\n') if 'qemu-system-x86_64' in line]
    if len(pid_list) > 5:
        raise Exception(
            f'pid list is too big. not killing whole server {pid_list}')
    if not pid_list:
        raise Exception(f'did not find any emulator. we have a bug here')
    for pid in pid_list:
        logging.info('going to kill %s', pid)
        kill(pid, SIGKILL)


def stop_emulator(emulator: str, timeout_seconds: str) -> bool:
    try:
        run([adb_command(), '-s', emulator, 'emu', 'kill'], timeout=timeout_seconds)
        return True
    except TimeoutExpired as exception:
        logging.error('got timeout exception: %s', exception)
        return False


def stop_emulators(timeout_seconds: int) -> None:
    logging.info('Get emulator list')
    try:
        emulator_list = get_emulator_list(timeout_seconds)
    except TimeoutExpired:
        logging.warn('got timeout in listing devices. going to kill brutal')
        kill_brutal()

    if not emulator_list:
        logging.warning('No emulators running!')
        return
    all_killed = True
    for emulator_name in emulator_list:
        logging.info('terminating %s', emulator_name)
        emulator_killed = stop_emulator(emulator_name, timeout_seconds)
        all_killed = all_killed and emulator_killed
    if not all_killed:
        kill_brutal()


if __name__ == '__main__':
    stop_emulators(TIMEOUT_STOP_EMULATORS)
