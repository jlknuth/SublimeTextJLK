import sublime
import sublime_plugin


class SaveCloseFileCommand(sublime_plugin.TextCommand):
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)
        self.window = self.view.window()

    def run(self, edit):
        self.view.run_command("save")
        if not self.view.is_dirty():
            self.view.window().run_command("close_file")
