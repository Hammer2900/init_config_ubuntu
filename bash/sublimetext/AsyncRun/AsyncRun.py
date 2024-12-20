import sublime
import sublime_plugin
import subprocess
import threading
import queue
import os
import time


class AsyncRunCommand(sublime_plugin.TextCommand):
    """
    Sublime Text command to run code asynchronously.

    This command supports running and stopping code execution in a separate thread,
    displaying output in the editor, and showing a progress indicator.
    """

    _lock = threading.RLock()  # Reentrant lock for synchronizing access to shared resources
    _running = False
    _process = None
    _output_queue = None
    _stop_event = None
    _run_thread = None
    _update_thread = None
    _progress_thread = None
    _working_directory = '/dev/shm/'

    @classmethod
    def set_working_directory(cls, directory):
        """
        Sets the working directory for the command.

        Args:
            directory (str): The directory path to set as the working directory.
        """
        with cls._lock:
            if not os.path.isdir(directory):
                sublime.error_message(f"The directory '{directory}' does not exist.")
                return

            cls._working_directory = directory
            sublime.status_message(f'Working directory set to: {directory}')

    def run(self, edit, action='run'):
        """
        Handles the execution of the command.

        Args:
            edit (sublime.Edit): The edit object.
            action (str): The action to perform ('run' or 'stop').
        """
        if action == 'run':
            self._start_execution()
        elif action == 'stop':
            self._stop_execution()

    def _start_execution(self):
        """Starts the code execution in a separate thread."""
        with self._lock:
            if self._running:
                sublime.error_message('A command is already running. Stop it first.')
                return

            self._running = True
            self._stop_event = threading.Event()
            self._output_queue = queue.Queue()

            code = self._get_code_to_execute()
            self.view.run_command('insert_snippet', {'contents': f'{code}\n'})

            self._run_thread = threading.Thread(target=self._run_code_async, args=(code,))
            self._update_thread = threading.Thread(target=self._update_output)
            self._progress_thread = threading.Thread(target=self._show_progress)

            self._run_thread.start()
            self._update_thread.start()
            self._progress_thread.start()

    def _get_code_to_execute(self):
        """
        Retrieves the code to be executed from the current selection or line.

        Returns:
            str: The code to be executed.
        """
        selection = self.view.sel()[0]
        if selection.empty():
            line_region = self.view.line(selection)
            return self.view.substr(line_region)
        else:
            return self.view.substr(selection)

    def _show_progress(self):
        """Displays a progress indicator in the status bar."""
        frames = ['|', '/', '-', '\\']
        i = 0
        while True:
            with self._lock:
                if not self._running or self._stop_event.is_set():
                    break
            frame = frames[i % len(frames)]
            sublime.status_message(f'Running command... {frame}')
            time.sleep(0.1)
            i += 1
        sublime.status_message('Command execution finished')

    def _stop_execution(self):
        """Stops the currently running code execution."""
        with self._lock:
            if self._running:
                self._stop_event.set()
                if self._process:
                    self._process.terminate()
                    try:
                        self._process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print('Process did not terminate in time.')

                self._join_threads()
                self._running = False
                sublime.status_message('Command execution stopped')
            else:
                sublime.status_message('No command is running')

    def _join_threads(self):
        """Joins all active threads."""
        if self._run_thread:
            self._run_thread.join(timeout=5)
        if self._update_thread:
            self._update_thread.join(timeout=5)
        if self._progress_thread:
            self._progress_thread.join(timeout=5)

    def _run_code_async(self, code):
        """
        Executes the given code asynchronously.

        Args:
            code (str): The code to execute.
        """
        try:
            with self._lock:
                self._process = subprocess.Popen(
                    code,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    shell=True,
                    cwd=self._working_directory,
                )
            self._process_output(self._process.stdout)
            self._process_output(self._process.stderr)
            self._process.wait()
        except Exception as e:
            self._output_queue.put(f'Error running code: {str(e)}')
        finally:
            with self._lock:
                self._running = False
            self._output_queue.put(None)  # Signal end of output
            self._join_threads()

    def _process_output(self, output_stream):
        """
        Processes the output stream from the subprocess.

        Args:
            output_stream: The output stream to process.
        """
        for line in output_stream:
            with self._lock:
                if self._stop_event.is_set():
                    break
            self._output_queue.put(line)
        output_stream.close()

    def _update_output(self):
        """Updates the editor with the output from the subprocess."""
        while True:
            try:
                line = self._output_queue.get(timeout=0.1)
                if line is None:
                    self.view.run_command(
                        'insert_snippet',
                        {
                            'contents': '\n# ====================================== end ====================================== #\n'
                        },
                    )
                    break
                self.view.run_command('insert_snippet', {'contents': line})
            except queue.Empty:
                with self._lock:
                    if not self._running and self._output_queue.empty():
                        break
                continue


class AsyncRunListener(sublime_plugin.EventListener):
    """
    EventListener for the AsyncRun plugin.
    """

    def on_query_context(self, view, key, operator, operand, match_all):
        """
        Handles context queries for key bindings.

        Args:
            view (sublime.View): The view.
            key (str): The context key.
            operator (int): The operator.
            operand: The operand.
            match_all (bool): Whether all conditions must match.

        Returns:
            bool or None: True if the context matches, False otherwise, or None if the key is not handled.
        """
        if key == 'async_run_enabled':
            with AsyncRunCommand._lock:
                return AsyncRunCommand._running
        return None


class StopAsyncRunCommand(sublime_plugin.TextCommand):
    """
    Sublime Text command to stop the currently running AsyncRun command.
    """

    def run(self, edit):
        """
        Stops the AsyncRun command.

        Args:
            edit (sublime.Edit): The edit object.
        """
        AsyncRunCommand._stop_execution(AsyncRunCommand)


class ChangeDirCommand(sublime_plugin.TextCommand):
    """
    Sublime Text command to change the working directory for AsyncRun.
    """

    def run(self, edit):
        """
        Changes the working directory.

        Args:
            edit (sublime.Edit): The edit object.
        """
        directory = self.view.substr(self.view.line(self.view.sel()[0]))
        AsyncRunCommand.set_working_directory(directory)
