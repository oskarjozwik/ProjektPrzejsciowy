import wx
import socket
import threading
import os


class FileWatcher:
	_instance = None
	_lock = threading.Lock()
	
	def __new__(cls, filename = "pos_def.txt"):
		with cls._lock:
			if cls._instance is None:
				cls._instance = super(FileWatcher, cls).__new__(cls)
				cls._instance.filename = filename
				cls._instance.last_mtime = cls._instance._get_file_mtime()
				cls._instance.subscribers = []
				cls._instance.timer = None
		return cls._instance
	
	def _get_file_mtime(self):
		try:
			return os.path.getmtime(self.filename)
		except Exception:
			return 0
	
	def start_watching(self, parent_window):
		with self._lock:
			if self.timer is None:
				self.timer = wx.Timer(parent_window)
				parent_window.Bind(wx.EVT_TIMER, self.OnCheckFile, self.timer)
				self.timer.Start(1000)
	
	def subscribe(self, callback):
		with self._lock:
			if callback not in self.subscribers:
				self.subscribers.append(callback)
	
	def unsubscribe(self, callback):
		with self._lock:
			if callback in self.subscribers:
				self.subscribers.remove(callback)
	
	def OnCheckFile(self, event):
		current_mtime = self._get_file_mtime()
		if current_mtime != self.last_mtime:
			self.last_mtime = current_mtime
			choices = self.get_predefined_choices()
			with self._lock:
				for callback in self.subscribers:
					callback(choices)
	
	def get_predefined_choices(self):
		choices = []
		try:
			with open(self.filename, "r") as file:
				for line in file:
					parts = line.split()
					if len(parts) == 2:
						choices.append(parts[0])
		except FileNotFoundError:
			pass
		return choices


class ControllerPanel(wx.Panel):
	def __init__(self, parent, onDeleteCallback):
		super().__init__(parent, style = wx.SIMPLE_BORDER)
		self.onDeleteCallback = onDeleteCallback
		self.panel_modes = []
		self.stepper_controls = []
		self.dcControl = None
		self.listener_running = False
		self.listener_thread = None
		self.listener_socket = None
		
		# Subscribe to centralized file watcher
		self.file_watcher = FileWatcher("pos_def.txt")
		self.file_watcher.subscribe(self.OnPredefinedChoicesUpdated)
		
		# Main vertical sizer for the entire panel
		main_vbox = wx.BoxSizer(orient = wx.VERTICAL)
		
		# Top horizontal sizer: [ Port Inputs ] [ Motor Choice Dropdown ] [ Stretchable Space ] [ Delete Button ]
		panel_hbox = wx.BoxSizer(orient = wx.HORIZONTAL)
		
		# Vertical sizer for the port inputs
		vbox = wx.BoxSizer(orient = wx.VERTICAL)
		
		# Driver port sub-sizer (horizontal)
		driver_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
		self.driverPortLabel = wx.StaticText(parent = self, label = 'Driver port')
		driver_sizer.Add(self.driverPortLabel, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		self.driverInputPort = None
		self.inputPortTextbox = wx.SpinCtrl(parent = self, min = 0, max = 65535, initial = 5005)
		driver_sizer.Add(self.inputPortTextbox, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		vbox.Add(driver_sizer, proportion = 0, flag = wx.ALIGN_RIGHT | wx.ALL, border = 2)
		
		# Response port sub-sizer (horizontal)
		response_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
		self.responsePortLabel = wx.StaticText(parent = self, label = 'Response port')
		response_sizer.Add(self.responsePortLabel, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		self.responseInputPort = None
		self.responsePortTextbox = wx.SpinCtrl(parent = self, min = 0, max = 65535, initial = 6005)
		self.responsePortTextbox.Bind(wx.EVT_SPINCTRL, self.OnResponsePortChanged)
		self.responsePortTextbox.Bind(wx.EVT_TEXT, self.OnResponsePortChanged)
		response_sizer.Add(
			self.responsePortTextbox,
			proportion = 0,
			flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL,
			border = 5
		)
		vbox.Add(response_sizer, proportion = 0, flag = wx.ALIGN_RIGHT | wx.ALL, border = 2)
		
		panel_hbox.Add(vbox, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		# Dropdown menu for motor type
		motor_choices = ["Stepper", "DC motor"]
		self.motorChoice = wx.Choice(parent = self, choices = motor_choices)
		self.motorChoice.SetSelection(0)  # Default to the first option ("Stepper")
		self.motorChoice.Bind(wx.EVT_CHOICE, self.OnMotorChoiceChanged)
		panel_hbox.Add(self.motorChoice, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		# Expandable gap (spacer) between the dropdown and the delete button
		panel_hbox.AddStretchSpacer(prop = 1)
		
		# Delete button on the right
		self.deleteButton = wx.Button(parent = self, label = 'Delete')
		self.deleteButton.Bind(wx.EVT_BUTTON, self.OnDeleteButtonClick)
		panel_hbox.Add(self.deleteButton, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		main_vbox.Add(panel_hbox, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)
		
		# Horizontal separator line 1
		self.staticLine = wx.StaticLine(parent = self, style = wx.LI_HORIZONTAL)
		main_vbox.Add(self.staticLine, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 5)
		
		# Lower sizer for dynamic content below the first separator
		self.lower_vbox = wx.BoxSizer(orient = wx.VERTICAL)
		main_vbox.Add(self.lower_vbox, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 5)
		
		# Horizontal separator line 2 (before status row)
		self.statusLine = wx.StaticLine(parent = self, style = wx.LI_HORIZONTAL)
		main_vbox.Add(self.statusLine, proportion = 0, flag = wx.EXPAND | wx.LEFT | wx.RIGHT, border = 5)
		
		# Status row at the bottom
		status_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
		self.statusLabel = wx.StaticText(parent = self, label = 'Status')
		status_sizer.Add(self.statusLabel, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		self.statusTextBox = wx.TextCtrl(parent = self, value = '', style = wx.TE_READONLY)
		status_sizer.Add(self.statusTextBox, proportion = 1, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
		
		main_vbox.Add(status_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 2)
		
		self.SetSizer(main_vbox)
		
		# Apply initial background color and lower section content
		self.UpdateBackgroundColor()
		self.UpdateLowerSection()
		
		# Start listening for incoming responses on the response port
		self.StartResponseListener()
	
	def OnPredefinedChoicesUpdated(self, choices):
		wx.CallAfter(self.RefreshPredefinedChoicesWithChoices, choices)
	
	def RefreshPredefinedChoicesWithChoices(self, choices):
		for control in self.stepper_controls:
			if isinstance(control, wx.Choice):
				current_sel = control.GetStringSelection()
				control.Clear()
				for choice in choices:
					control.Append(choice)
				if current_sel in choices:
					control.SetStringSelection(current_sel)
				elif choices:
					control.SetSelection(0)
		if self.dcControl and isinstance(self.dcControl, wx.Choice):
			current_sel = self.dcControl.GetStringSelection()
			self.dcControl.Clear()
			for choice in choices:
				self.dcControl.Append(choice)
			if current_sel in choices:
				self.dcControl.SetStringSelection(current_sel)
			elif choices:
				self.dcControl.SetSelection(0)
	
	def OnMotorChoiceChanged(self, event):
		self.panel_modes = []  # Reset modes when switching motor type
		self.UpdateBackgroundColor()
		self.UpdateLowerSection()
	
	def OnResponsePortChanged(self, event):
		self.StartResponseListener()
		event.Skip()
	
	def StartResponseListener(self):
		self.StopResponseListener()
		try:
			port = int(self.responsePortTextbox.GetValue())
		except ValueError:
			return
		
		self.listener_running = True
		self.listener_thread = threading.Thread(target = self._listen_loop, args = (port,), daemon = True)
		self.listener_thread.start()
	
	def StopResponseListener(self):
		self.listener_running = False
		if self.listener_socket:
			try:
				self.listener_socket.close()
			except Exception:
				pass
			self.listener_socket = None
	
	def _listen_loop(self, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		try:
			sock.bind(('127.0.0.1', port))
			sock.settimeout(1.0)
		except Exception:
			return
		
		self.listener_socket = sock
		
		while self.listener_running:
			try:
				data, addr = sock.recvfrom(1024)
				message = data.decode('utf-8', errors = 'ignore')
				wx.CallAfter(self.SafeSetStatus, message)
			except socket.timeout:
				continue
			except Exception:
				break
		
		try:
			sock.close()
		except Exception:
			pass
	
	def SafeSetStatus(self, message):
		try:
			if not self.IsBeingDeleted() and hasattr(self, 'statusTextBox'):
				self.statusTextBox.SetValue(message)
		except RuntimeError:
			pass
	
	def UpdateBackgroundColor(self):
		selection = self.motorChoice.GetStringSelection()
		if selection == "Stepper":
			# Slightly blue
			self.SetBackgroundColour(wx.Colour(230, 242, 255))
		elif selection == "DC motor":
			# Slightly orange
			self.SetBackgroundColour(wx.Colour(255, 240, 230))
		self.Refresh()
	
	def UpdateLowerSection(self):
		# Clear existing items from lower_vbox and destroy their windows
		self.lower_vbox.Clear(delete_windows = True)
		self.stepper_controls = []
		self.dcControl = None
		
		selection = self.motorChoice.GetStringSelection()
		choices = self.file_watcher.get_predefined_choices()
		
		if selection == "Stepper":
			stepper_configs = [
				("Target", "target", 0),
				("Current", "current", 0),
				("Speed", "speed", 250)
			]
			
			if not self.panel_modes or len(self.panel_modes) != 3:
				self.panel_modes = ['Custom', 'Custom', 'Custom']
			
			for i, (label_text, cmd_name, default_val) in enumerate(stepper_configs):
				sub_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
				
				label = wx.StaticText(parent = self, label = label_text)
				sub_sizer.Add(label, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
				
				sub_sizer.AddStretchSpacer(prop = 1)
				
				# Vertically arranged radio control (Custom / Predefined)
				radio_vbox = wx.BoxSizer(orient = wx.VERTICAL)
				rb_custom = wx.RadioButton(parent = self, label = 'Custom', style = wx.RB_GROUP)
				rb_predefined = wx.RadioButton(parent = self, label = 'Predefined')
				
				if self.panel_modes[i] == 'Predefined':
					rb_predefined.SetValue(True)
				else:
					rb_custom.SetValue(True)
				
				rb_custom.Bind(wx.EVT_RADIOBUTTON, lambda evt, idx = i: self.OnModeChanged(idx, 'Custom', evt))
				rb_predefined.Bind(wx.EVT_RADIOBUTTON, lambda evt, idx = i: self.OnModeChanged(idx, 'Predefined', evt))
				
				radio_vbox.Add(rb_custom, proportion = 0, flag = wx.ALL, border = 1)
				radio_vbox.Add(rb_predefined, proportion = 0, flag = wx.ALL, border = 1)
				sub_sizer.Add(radio_vbox, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 2)
				
				control_panel = wx.Panel(parent = self)
				control_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
				
				if self.panel_modes[i] == 'Predefined':
					control = wx.Choice(parent = control_panel, choices = choices)
					if choices:
						control.SetSelection(0)
				else:
					control = wx.SpinCtrl(parent = control_panel, min = 0, max = 10000, initial = default_val)
				
				control_sizer.Add(control, proportion = 1, flag = wx.EXPAND)
				control_panel.SetSizer(control_sizer)
				control_panel.SetMinSize((100, -1))
				
				self.stepper_controls.append(control)
				sub_sizer.Add(control_panel, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 2)
				
				btn = wx.Button(parent = self, label = 'Update')
				btn.Bind(wx.EVT_BUTTON, lambda evt, cmd = cmd_name, idx = i: self.OnUpdateStepper(cmd, idx, evt))
				sub_sizer.Add(btn, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 2)
				
				self.lower_vbox.Add(sub_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 2)
		else:
			# DC motor: single configuration
			if not self.panel_modes or len(self.panel_modes) != 1:
				self.panel_modes = ['Custom']
			
			sub_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
			
			self.radioLeft = wx.RadioButton(parent = self, label = 'Left', style = wx.RB_GROUP)
			self.radioRight = wx.RadioButton(parent = self, label = 'Right')
			
			sub_sizer.Add(self.radioLeft, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
			sub_sizer.Add(self.radioRight, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
			
			sub_sizer.AddStretchSpacer(prop = 1)
			
			radio_vbox = wx.BoxSizer(orient = wx.VERTICAL)
			rb_custom = wx.RadioButton(parent = self, label = 'Custom', style = wx.RB_GROUP)
			rb_predefined = wx.RadioButton(parent = self, label = 'Predefined')
			
			if self.panel_modes[0] == 'Predefined':
				rb_predefined.SetValue(True)
			else:
				rb_custom.SetValue(True)
			
			rb_custom.Bind(wx.EVT_RADIOBUTTON, lambda evt, idx = 0: self.OnModeChanged(idx, 'Custom', evt))
			rb_predefined.Bind(wx.EVT_RADIOBUTTON, lambda evt, idx = 0: self.OnModeChanged(idx, 'Predefined', evt))
			
			radio_vbox.Add(rb_custom, proportion = 0, flag = wx.ALL, border = 1)
			radio_vbox.Add(rb_predefined, proportion = 0, flag = wx.ALL, border = 1)
			sub_sizer.Add(radio_vbox, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 2)
			
			control_panel = wx.Panel(parent = self)
			control_sizer = wx.BoxSizer(orient = wx.HORIZONTAL)
			
			if self.panel_modes[0] == 'Predefined':
				self.dcControl = wx.Choice(parent = control_panel, choices = choices)
				if choices:
					self.dcControl.SetSelection(0)
			else:
				self.dcControl = wx.SpinCtrl(parent = control_panel, min = 0, max = 10000, initial = 1000)
			
			control_sizer.Add(self.dcControl, proportion = 1, flag = wx.EXPAND)
			control_panel.SetSizer(control_sizer)
			control_panel.SetMinSize((100, -1))
			
			sub_sizer.Add(control_panel, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
			
			self.sendButton = wx.Button(parent = self, label = 'Send')
			self.sendButton.Bind(wx.EVT_BUTTON, self.OnSendDC)
			sub_sizer.Add(self.sendButton, proportion = 0, flag = wx.ALIGN_CENTER_VERTICAL | wx.ALL, border = 5)
			
			self.lower_vbox.Add(sub_sizer, proportion = 0, flag = wx.EXPAND | wx.ALL, border = 2)
		
		self.Layout()
		self.InvalidateBestSize()
		top_frame = self.GetTopLevelParent()
		if top_frame:
			top_frame.Layout()
			if hasattr(top_frame, 'scrolledWindow'):
				if hasattr(top_frame, 'LayoutColumns'):
					top_frame.LayoutColumns()
				top_frame.scrolledWindow.FitInside()
	
	def OnModeChanged(self, idx, mode, event):
		if self.panel_modes[idx] != mode:
			self.panel_modes[idx] = mode
			self.UpdateLowerSection()
	
	def SendCommand(self, command_name, control, is_predefined):
		port_val = self.inputPortTextbox.GetValue()
		try:
			comm_port = int(port_val)
		except ValueError:
			self.statusTextBox.SetValue(f'{port_val} is not a valid port number.')
			return
		
		if is_predefined:
			if isinstance(control, wx.Choice):
				parameter = control.GetStringSelection()
			else:
				parameter = str(control.GetValue()).strip()
			
			definition_found = False
			try:
				with open("pos_def.txt", "r") as file:
					for line in file:
						parts = line.split()
						if len(parts) != 2:
							continue
						if parameter == parts[0]:
							parameter = parts[1]
							definition_found = True
							break
			except FileNotFoundError:
				self.statusTextBox.SetValue('Definition file "pos_def.txt" cannot be opened.')
				return
			if not definition_found:
				self.statusTextBox.SetValue('No parameter definition found.')
				return
		else:
			parameter = str(control.GetValue()).strip()
		
		full_command = f'{command_name} {parameter}'
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.sendto(full_command.encode(), ('127.0.0.1', comm_port))
			sock.close()
			self.statusTextBox.SetValue(f'Command "{full_command}" sent.')
		except Exception as e:
			self.statusTextBox.SetValue(f'Socket error: {e}')
	
	def OnUpdateStepper(self, command_name, idx, event):
		control = self.stepper_controls[idx]
		is_predefined = (self.panel_modes[idx] == 'Predefined')
		self.SendCommand(command_name, control, is_predefined)
	
	def OnSendDC(self, event):
		command_name = 'left' if self.radioLeft.GetValue() else 'right'
		control = self.dcControl
		is_predefined = (self.panel_modes[0] == 'Predefined')
		self.SendCommand(command_name, control, is_predefined)
	
	def OnDeleteButtonClick(self, event):
		self.file_watcher.unsubscribe(self.OnPredefinedChoicesUpdated)
		self.StopResponseListener()
		if self.onDeleteCallback:
			self.onDeleteCallback(self)


class ExampleFrame(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		main_panel = wx.Panel(parent = self)
		main_vbox = wx.BoxSizer(orient = wx.VERTICAL)
		
		self.addPanelButton = wx.Button(parent = main_panel, label = 'New panel')
		main_vbox.Add(self.addPanelButton, flag = wx.ALL, border = 10)
		self.addPanelButton.Bind(event = wx.EVT_BUTTON, handler = self.OnAddPanelButtonClick)
		
		# Scrolled window container for controller panels
		self.scrolledWindow = wx.ScrolledWindow(parent = main_panel, style = wx.VSCROLL)
		self.scrolledWindow.SetScrollRate(5, 5)
		
		# Use a FlexGridSizer to support multiple columns based on available width
		self.panels_grid = wx.FlexGridSizer(cols = 1, hgap = 10, vgap = 10)
		self.scrolledWindow.SetSizer(self.panels_grid)
		
		main_vbox.Add(self.scrolledWindow, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 5)
		main_panel.SetSizer(main_vbox)
		
		self.controllers = []
		
		# Initialize the centralized file watcher at the frame level
		self.file_watcher = FileWatcher("pos_def.txt")
		self.file_watcher.start_watching(self)
		
		self.SetTitle("Manual controller")
		self.SetSize((500, 450))
		self.SetMinSize((300, 150))
		self.Centre()
		
		# Bind resize event to dynamically adjust columns
		self.Bind(wx.EVT_SIZE, self.OnFrameResize)
	
	def OnFrameResize(self, event):
		self.LayoutColumns()
		event.Skip()
	
	def LayoutColumns(self):
		if not self.controllers:
			self.panels_grid.SetCols(1)
			self.scrolledWindow.FitInside()
			return
		
		available_width = self.scrolledWindow.GetClientSize().width
		if available_width <= 0:
			return
		
		max_panel_width = max(panel.GetBestSize().width for panel in self.controllers)
		slot_width = max_panel_width + 20
		
		cols = available_width // slot_width
		if cols < 1:
			cols = 1
		
		if self.panels_grid.GetCols() != cols:
			self.panels_grid.SetCols(cols)
			self.scrolledWindow.Layout()
			self.scrolledWindow.FitInside()
	
	def OnAddPanelButtonClick(self, event):
		newPanel = ControllerPanel(parent = self.scrolledWindow, onDeleteCallback = self.RemovePanel)
		self.controllers.append(newPanel)
		self.panels_grid.Add(newPanel, proportion = 0, flag = wx.ALL, border = 5)
		self.LayoutColumns()
		self.scrolledWindow.Layout()
		self.scrolledWindow.FitInside()
	
	def RemovePanel(self, panel):
		if panel in self.controllers:
			self.controllers.remove(panel)
			self.panels_grid.Detach(panel)
			panel.Destroy()
			self.LayoutColumns()
			self.scrolledWindow.Layout()
			self.scrolledWindow.FitInside()


if __name__ == '__main__':
	app = wx.App()
	frame = ExampleFrame(None)
	frame.Show()
	app.MainLoop()