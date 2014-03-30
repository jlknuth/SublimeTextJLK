import sublime, sublime_plugin

POSNS = {}	# Based on each view's id, store edited positions.
			# The first element stores the most recently edited line
			# number, so that the same line is not saved repeatedly.

class LastEditLineCommand(sublime_plugin.TextCommand):
	posn = -1	# always add 2 to this, which indexes the first
				# edited position (for the current view)
	def run(self, edit):
		vid = self.view.id()
		# if there are no edited positions stored, just return
		if not POSNS.has_key(vid): return
		# identify the previously edited position
		self.posn = (self.posn + 2) % (len(POSNS[vid]) - 1)
		edited_region = sublime.Region(POSNS[vid][-(self.posn + 1)], POSNS[vid][-self.posn])
		self.view.sel().clear()
		# bring the edited region into view and select it
		self.view.show(edited_region)
		self.view.sel().add(edited_region)

class CaptureEditing(sublime_plugin.EventListener):
	# def __init__(self): POSNS = {}
	def on_modified(self, view):
		vid = view.id()
		sel = view.sel()[0]
		currA = sel.begin()
		currB = sel.end()
		curr_line, _ = view.rowcol(currB)
		if not POSNS.has_key(vid):	# if a dictionary entry doesn't already
									# exist for this view..
			POSNS[vid] = [curr_line, currA - sel.empty(), currB]
			self.prev_size = view.size()	# store the initial size
			return
		self.curr_size = view.size()
		self.diff = self.curr_size - self.prev_size	# has the file grown/shrunk?
		self.prev_size = self.curr_size
		for index, value in enumerate(POSNS[vid]):
			if index > 0 and value >= currB:
				# for every saved position, increase or reduce it by the
				# difference in file size (but only if it's beyond the cursor)
				if self.diff > 0:
					POSNS[vid][index] = min(value + self.diff, self.curr_size - 1)
					# min is used so that we don't go beyond the end of the file
				elif self.diff < 0:
					POSNS[vid][index] = max(value + self.diff, currA)
					# max is used in case the edited position has been deleted
		if POSNS[vid][0] == curr_line or abs(POSNS[vid][-2] - currA) == 1 \
			or abs(POSNS[vid][-1] - currB) == 1:
			POSNS[vid][-2] = min(POSNS[vid][-2], currA)
			POSNS[vid][-1] = max(POSNS[vid][-1], currB)
		else:
			POSNS[vid].extend([currA - sel.empty(), currB])		# add the edited position
			if len(POSNS[vid]) > 11: POSNS[vid][1:] = POSNS[vid][3:]
		POSNS[vid][0] = curr_line			# update the current line
