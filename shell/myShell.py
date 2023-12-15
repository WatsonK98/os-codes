#! /usr/bin/env python3

import os
import sys
import re

pid = os.getpid()

while True:
    os.write(1, ("$").encode())
    try:
        input_cmd = os.read(0, 50).decode().strip()
    except OSError:
        break

    if input_cmd == "exit":
        break

    # Split commands based on pipe symbol '|'
    commands = input_cmd.split('|')

    # Iterate over each command in the pipeline
    prev_read = 0  # File descriptor to read from initially
    pipe_out = None  # Define pipe_out outside of the if block

    for i, cmd in enumerate(commands):
        rc = os.fork()

        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        elif rc == 0:  # child
            os.write(1, ("Child: My pid==%d. Parent's pid=%d\n" % (os.getpid(), pid)).encode())

            # Redirect input if not the first command
            if i > 0:
                os.dup2(prev_read, 0)
                os.close(prev_read)

            # Redirect output if not the last command
            if i < len(commands) - 1:
                # Using pipe here to create a new pipe for the child process
                pipe_out, pipe_in = os.pipe()
                os.dup2(pipe_in, 1)
                os.close(pipe_in)

            # Parse and execute the command
            args = cmd.split()
            for dir in re.split(":", os.environ['PATH']):
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass

            os.write(2, ("Child: Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)

        else:  # parent
            os.write(1, ("Parent: My pid=%d. Child's pid=%d\n" % (pid, rc)).encode())
            os.wait()  # Wait for the child process to finish

            if i < len(commands) - 1:
                # Close the write end of the previous pipe, so the next command reads from the pipe
                os.close(prev_read)

                # Check if pipe_out is defined before setting prev_read
                if pipe_out is not None:
                    prev_read = pipe_out  # File descriptor to read from next
