import argparse
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


def kill_brutal(avd_name=None):
    logging.info('killing all emulators')
    ps_res = run(['ps', '-e'], capture_output=True, text=True)
    if avd_name is not None:
        # Kill only process for specific emulator
        pid_list = [int(line.split()[0]) for line in ps_res.stdout.split(
            '\n') if 'qemu-system-x86_64' in line and avd_name in line]
    else:
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


def stop_emulator(emulator: str, timeout_seconds: int) -> bool:
    try:
        run([adb_command(), '-s', emulator, 'emu', 'kill'], timeout=timeout_seconds)
        return True
    except TimeoutExpired as exception:
        logging.error('got timeout exception: %s', exception)
        return False


def stop_emulators(timeout_seconds: int, emulator_serial: str = None, avd_name: str = None) -> None:
    if emulator_serial is not None:
        emulator_list = [emulator_serial]
    else:
        logging.info('Get emulator list')
        try:
            emulator_list = get_emulator_list(timeout_seconds)
        except TimeoutExpired:
            logging.warning('got timeout in listing devices. going to kill brutal')
            kill_brutal(avd_name)
            return

        if not emulator_list:
            logging.warning('No emulators running!')
            return

    all_killed = True
    for emulator_name in emulator_list:
        logging.info('terminating %s', emulator_name)
        emulator_killed = stop_emulator(emulator_name, timeout_seconds)
        all_killed = all_killed and emulator_killed
    if not all_killed:
        kill_brutal(avd_name)


if __name__ == '__main__':
    # To only kill a specific emulator, it's possible to pass the emulator serial ("emulator-5554") and the avd name ("android28")
    parser = argparse.ArgumentParser()
    parser.add_argument('--emulator_serial', default=None)
    parser.add_argument('--avd_name', default=None)
    args = parser.parse_args()
    if args.avd_name is not None and args.emulator_serial is None:
        parser.error("Must provide emulator_serial when providing avd_name")
    if args.avd_name is None and args.emulator_serial is not None:
        parser.error("Must provide avd_name when providing emulator_serial")
    stop_emulators(TIMEOUT_STOP_EMULATORS, args.emulator_serial, args.avd_name)
