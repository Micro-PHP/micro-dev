import os, logging, subprocess


def execute_shell_command(cmd, cwd=None, capture_output=False):
    if cwd is None:
        cwd = os.getcwd()
    logging.info(f'Running a command:"{cmd}" in a working directory {cwd}')
    try:
        result = subprocess.run(cmd, check=True, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f'STDOUT: {result.stdout}')
        if capture_output:
            return result.stdout.strip()  # Return the stdout if capture_output is True
    except subprocess.CalledProcessError as e:
        logging.error(f'Command "{cmd}" failed with error: {e}')
        logging.error(f'STDERR: {e.stderr}')
        exit(1)
