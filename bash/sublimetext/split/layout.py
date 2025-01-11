import sublime_plugin


class SingleColumnCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.run_command(
            'set_layout',
            {'cols': [0.0, 1.0], 'rows': [0.0, 1.0], 'cells': [[0, 0, 1, 1]]},
        )


class OpenScratchInNewLayoutCommand(sublime_plugin.WindowCommand):
    def run(self):
        num_groups = self.window.num_groups()

        if num_groups > 1:
            active_group = 1
        else:
            self.window.run_command(
                'set_layout',
                {
                    'cols': [0.0, 0.5, 1.0],
                    'rows': [0.0, 1.0],
                    'cells': [[0, 0, 1, 1], [1, 0, 2, 1]],
                },
            )
            active_group = 1
        new_view = self.window.new_file()
        self.window.set_view_index(new_view, active_group, len(self.window.views_in_group(active_group)))
        new_view.run_command('insert', {'characters': '# Title1\n'})
        self.window.focus_view(new_view)
