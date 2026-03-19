import logging
import os
import shlex
import subprocess

class ShellError(Exception):
    pass

def execute_shell_command(cmd, cwd=None, capture_output=False):
    if cwd is None:
        cwd = os.getcwd()
    args = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
    logging.info(f'Running command: {shlex.join(args)} in working directory {cwd}')
    try:
        result = subprocess.run(
            args,
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logging.info(f'STDOUT: {result.stdout}')
        if capture_output:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f'Command "{shlex.join(args)}" failed with error: {e}')
        logging.error(f'STDERR: {e.stderr}')
        raise ShellError(f'Command "{shlex.join(args)}" failed with error: {e.stderr.strip() or e}')
