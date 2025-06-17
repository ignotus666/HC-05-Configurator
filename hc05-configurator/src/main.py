import sys
import glob
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QHBoxLayout, QTextEdit, QMenuBar, QAction, QFileDialog, QDialog, QCheckBox, QDialogButtonBox
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap
import serial
import time
import os
import json
import platform
if platform.system() == 'Windows':
    CONFIG_PATH = os.path.join(os.getenv('APPDATA', os.path.expanduser('~')), 'hc05_configurator_prefs.json')
else:
    CONFIG_PATH = os.path.expanduser("~/.hc05_configurator_prefs.json")

# Comprehensive list of HC-05 AT commands with tooltips and parameter hints
ALL_AT_COMMANDS = [
    {"key": "AT", "label": "AT (Test)", "tooltip": "Test command mode. Returns OK if module is responsive.", "param_hint": "(no parameters)"},
    {"key": "VERSION", "label": "AT+VERSION?", "tooltip": "Get firmware version.", "param_hint": "(no parameters)"},
    {"key": "ADDR", "label": "AT+ADDR?", "tooltip": "Get Bluetooth address.", "param_hint": "(no parameters)"},
    {"key": "NAME", "label": "AT+NAME? / AT+NAME=", "tooltip": "Get or set device name.", "param_hint": "<name> (for set)"},
    {"key": "ROLE", "label": "AT+ROLE? / AT+ROLE=", "tooltip": "Get or set role: 0=Slave, 1=Master, 2=Slave-Loop.", "param_hint": "0, 1, or 2 (for set)"},
    {"key": "PSWD", "label": "AT+PSWD? / AT+PSWD=", "tooltip": "Get or set password.", "param_hint": "<password> (for set)"},
    {"key": "UART", "label": "AT+UART? / AT+UART=", "tooltip": "Get or set UART: baud, stop, parity.", "param_hint": "<baud>,<stop>,<parity> (for set)"},
    {"key": "CMODE", "label": "AT+CMODE? / AT+CMODE=", "tooltip": "Get or set connection mode.", "param_hint": "0, 1, or 2 (for set)"},
    {"key": "BIND", "label": "AT+BIND? / AT+BIND=", "tooltip": "Get or set bind address.", "param_hint": "<address> (for set)"},
    {"key": "POLAR", "label": "AT+POLAR? / AT+POLAR=", "tooltip": "Get or set LED output polarity.", "param_hint": "<PIO,level> (for set)"},
    {"key": "PIO", "label": "AT+PIO? / AT+PIO=", "tooltip": "Get or set PIO pin output.", "param_hint": "<pin,level> (for set)"},
    {"key": "INQM", "label": "AT+INQM? / AT+INQM=", "tooltip": "Get or set inquiry parameters.", "param_hint": "<mode,max_num,length> (for set)"},
    {"key": "CLASS", "label": "AT+CLASS? / AT+CLASS=", "tooltip": "Get or set class of device.", "param_hint": "<class> (for set)"},
    {"key": "IPSCAN", "label": "AT+IPSCAN? / AT+IPSCAN=", "tooltip": "Get or set scan parameters.", "param_hint": "<interval,window,interval,window> (for set)"},
    {"key": "INIT", "label": "AT+INIT", "tooltip": "Initialize SPP profile.", "param_hint": "(no parameters)"},
    {"key": "INQ", "label": "AT+INQ", "tooltip": "Inquiry for nearby devices.", "param_hint": "(no parameters)"},
    {"key": "FSAD", "label": "AT+FSAD? / AT+FSAD=", "tooltip": "Get or set fixed address.", "param_hint": "<address> (for set)"},
    {"key": "MRAD", "label": "AT+MRAD?", "tooltip": "Get most recently used address.", "param_hint": "(no parameters)"},
    {"key": "STATE", "label": "AT+STATE?", "tooltip": "Get connection state.", "param_hint": "(no parameters)"},
    {"key": "RESET", "label": "AT+RESET", "tooltip": "Reset module.", "param_hint": "(no parameters)"},
    {"key": "ORGL", "label": "AT+ORGL", "tooltip": "Restore factory settings.", "param_hint": "(no parameters)"},
    {"key": "SADDR", "label": "AT+SADDR? / AT+SADDR=", "tooltip": "Get or set serial address.", "param_hint": "<address> (for set)"},
    {"key": "RMAAD", "label": "AT+RMAAD", "tooltip": "Remove all paired devices.", "param_hint": "(no parameters)"},
    {"key": "ADCN", "label": "AT+ADCN? / AT+ADCN=", "tooltip": "Get or set auto-connect number.", "param_hint": "<number> (for set)"},
    {"key": "PAIR", "label": "AT+PAIR=", "tooltip": "Pair with device.", "param_hint": "<address>,<timeout>"},
    {"key": "LINK", "label": "AT+LINK=", "tooltip": "Connect to device.", "param_hint": "<address>"},
    {"key": "DISC", "label": "AT+DISC", "tooltip": "Disconnect.", "param_hint": "(no parameters)"},
    {"key": "ENQ", "label": "AT+ENQ? / AT+ENQ=", "tooltip": "Get or set encryption.", "param_hint": "<0|1> (for set)"},
    {"key": "Q", "label": "AT+Q", "tooltip": "Quit command mode.", "param_hint": "(no parameters)"},
]

# Default enabled commands
DEFAULT_ENABLED = {"NAME", "PSWD", "UART", "CMODE"}
NO_PARAM_COMMANDS = {"RESET", "INIT", "INQ", "DISC", "ORGL", "RMAAD", "AT", "VERSION", "ADDR", "MRAD", "STATE"}

class HC05Configurator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HC-05 Configurator")
        self.setGeometry(100, 100, 500, 500)

        self.serial = None
        # Use all commands for preferences, but only enable defaults
        self.command_prefs = self.load_command_prefs()
        self.profile_path = None

        # Menu bar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open Config Profile", self)
        open_action.triggered.connect(self.open_profile)
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_profile)
        saveas_action = QAction("Save As", self)
        saveas_action.triggered.connect(self.saveas_profile)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(saveas_action)
        pref_menu = menubar.addMenu("Preferences")
        pref_action = QAction("Customize Commands", self)
        pref_action.triggered.connect(self.open_preferences)
        reset_defaults_action = QAction("Reset default parameters", self)
        reset_defaults_action.triggered.connect(self.reset_default_parameters)
        pref_menu.addAction(pref_action)
        pref_menu.addAction(reset_defaults_action)
        self.setMenuBar(menubar)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Icon at top left (robust path for both source and installed)
        icon_label = QLabel()
        icon_paths = [
            os.path.join(os.path.dirname(__file__), '../hc-05.png'),
            os.path.join(os.path.dirname(__file__), 'hc-05.png'),
            os.path.join(os.getcwd(), 'hc-05.png'),
            'hc-05.png',
        ]
        if platform.system() != 'Windows':
            icon_paths += [
                '/usr/share/icons/hicolor/48x48/apps/hc-05.png',
                '/usr/share/pixmaps/hc-05.png',
            ]
        for path in icon_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.layout.insertWidget(0, icon_label, alignment=Qt.AlignLeft)
                break

        self.port_selector = QComboBox()
        self.layout.addWidget(QLabel("Select Serial Port:"))
        self.layout.addWidget(self.port_selector)
        self.refresh_ports()
        self.port_selector.currentIndexChanged.connect(self.open_selected_port)

        # Terminal output area
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("background-color: #111; color: #0f0; font-family: monospace;")
        self.terminal_output.setMinimumHeight(180)
        self.layout.addWidget(QLabel("Terminal Output:"))
        self.layout.addWidget(self.terminal_output)

        # Use a grid layout for commands
        from PyQt5.QtWidgets import QGridLayout
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        self.command_widgets = {}
        self.command_fields = {}
        self.command_query_buttons = {}
        self.command_set_buttons = {}
        self._populate_command_grid()
        self.update_command_visibility()

        # Add Get All and Set All buttons above the grid
        btn_layout = QHBoxLayout()
        get_all_btn = QPushButton("Get All")
        set_all_btn = QPushButton("Set All")
        get_all_btn.setToolTip("Query all active parameters and update their fields.")
        set_all_btn.setToolTip("Set all active parameters with filled-in values.")
        get_all_btn.clicked.connect(self.get_all_parameters)
        set_all_btn.clicked.connect(self.set_all_parameters)
        btn_layout.addWidget(get_all_btn)
        btn_layout.addWidget(set_all_btn)
        self.layout.addLayout(btn_layout)

        # Add Clear Terminal button
        clear_terminal_btn = QPushButton("Clear Terminal")
        clear_terminal_btn.setToolTip("Clear the terminal output area.")
        clear_terminal_btn.clicked.connect(self.clear_terminal)
        self.layout.addWidget(clear_terminal_btn)

        self.restore_window_geometry()

        self.show()

        self._batch_timer = QTimer(self)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._batch_timeout)
        self._batch_mode = None
        self._batch_queue = []
        self._batch_waiting = False
        self._batch_last_key = None

    def refresh_ports(self):
        self.port_selector.clear()
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
        except Exception:
            # Fallback for Linux
            if platform.system() == 'Windows':
                ports = [f'COM{i}' for i in range(1, 21)]
            else:
                import glob
                ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
        self.port_selector.addItems(ports)
        # Auto-select /dev/ttyUSB0 on Linux if present
        if ports:
            preferred_port = '/dev/ttyUSB0'
            if platform.system() != 'Windows' and preferred_port in ports:
                idx = ports.index(preferred_port)
                self.port_selector.setCurrentIndex(idx)
            else:
                self.port_selector.setCurrentIndex(0)
            self.open_selected_port()

    def open_selected_port(self):
        if self.serial:
            self.serial.close()
        port = self.port_selector.currentText()
        if port:
            try:
                self.serial = serial.Serial(port, 38400, timeout=1)
            except Exception as e:
                QMessageBox.critical(self, "Serial Error", f"Could not open port {port}: {e}")
                self.serial = None

    def append_terminal(self, text):
        self.terminal_output.append(text)

    def send_at_command(self, command, read_response=True, update_field=None, batch_mode=False):
        if not self.serial or not self.serial.is_open:
            QMessageBox.warning(self, "Serial Not Open", "Please select a valid serial port.")
            return None
        try:
            self.serial.reset_input_buffer()
            self.serial.write((command + '\r\n').encode())
            self.append_terminal(f">>> {command}")
            time.sleep(0.2)
            if read_response:
                response = self.serial.read(128).decode(errors='ignore').strip()
                if response:
                    self.append_terminal(response)
                    if update_field is not None and update_field in self.command_fields:
                        # Extract only the value part from the response
                        # Handles both +KEY:val and +KEY=val
                        value = ''
                        for line in response.splitlines():
                            line = line.strip()
                            if line.startswith('+') and (':' in line or '=' in line):
                                sep = ':' if ':' in line else '='
                                value = line.split(sep, 1)[1].strip()
                                break
                            elif line and not line.startswith('AT+') and line != 'OK':
                                value = line
                        self.command_fields[update_field].setText(value)
                    if batch_mode and self._batch_waiting:
                        self._batch_timer.stop()
                        self._batch_waiting = False
                        QTimer.singleShot(100, self._process_next_batch_command)
                else:
                    # No response, let timer handle timeout
                    pass
                return response
        except Exception as e:
            QMessageBox.critical(self, "Serial Error", str(e))
        return None

    def query_name(self):
        self.send_at_command('AT+NAME?')

    def set_name(self):
        name = self.command_fields['NAME'].text().strip()
        if name:
            self.send_at_command(f'AT+NAME={name}')

    def query_role(self):
        self.send_at_command('AT+ROLE?')

    def set_role(self):
        role = self.command_fields['ROLE'].text().strip()
        if role in ['0', '1', '2']:
            self.send_at_command(f'AT+ROLE={role}')
        else:
            QMessageBox.warning(self, "Invalid Role", "Role must be 0 (Slave), 1 (Master), or 2 (Slave-Loop)")

    def query_password(self):
        self.send_at_command('AT+PSWD?')

    def set_password(self):
        pswd = self.command_fields['PSWD'].text().strip()
        if pswd:
            self.send_at_command(f'AT+PSWD={pswd}')

    def query_uart(self):
        self.send_at_command('AT+UART?')

    def set_uart(self):
        uart = self.command_fields['UART'].text().strip()
        if uart:
            self.send_at_command(f'AT+UART={uart}')

    def query_cmode(self):
        self.send_at_command('AT+CMODE?')

    def set_cmode(self):
        cmode = self.command_fields['CMODE'].text().strip()
        if cmode in ['0', '1', '2']:
            self.send_at_command(f'AT+CMODE={cmode}')
        else:
            QMessageBox.warning(self, "Invalid CMODE", "CMODE must be 0, 1, or 2.")

    def load_command_prefs(self):
        prefs = {cmd["key"]: (cmd["key"] in DEFAULT_ENABLED) for cmd in ALL_AT_COMMANDS}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    loaded = json.load(f)
                for cmd in ALL_AT_COMMANDS:
                    key = cmd["key"]
                    # Always enable PSWD if missing or disabled
                    if key == "PSWD":
                        prefs[key] = True
                    elif key in loaded:
                        prefs[key] = loaded[key]
            except Exception:
                pass
        return prefs

    def save_command_prefs(self):
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.command_prefs, f)
        except Exception:
            pass

    def set_profile_title(self):
        if self.profile_path:
            import os
            name = os.path.basename(self.profile_path)
            self.setWindowTitle(f"HC-05 Configurator - [{name}]")
        else:
            self.setWindowTitle("HC-05 Configurator")

    def _populate_command_grid(self):
        # Remove old widgets if re-populating
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.command_widgets = {}
        self.command_fields = {}
        self.command_query_buttons = {}
        self.command_set_buttons = {}
        max_rows = 10
        row = col = 0
        # Only include enabled commands
        enabled_cmds = [cmd for cmd in ALL_AT_COMMANDS if self.command_prefs.get(cmd["key"], False)]
        for cmd in enabled_cmds:
            key = cmd["key"]
            # Create row widgets
            label = QLabel(cmd["label"])
            label.setToolTip(cmd["tooltip"])
            field = QLineEdit()
            field.setPlaceholderText(cmd["param_hint"])
            self.command_fields[key] = field
            query_btn = QPushButton("Query")
            query_btn.setToolTip(f"Query {cmd['label']}")
            set_btn = QPushButton("Set")
            set_btn.setToolTip(f"Set {cmd['label']}")
            if key in NO_PARAM_COMMANDS:
                set_btn.setEnabled(False)
                field.setEnabled(False)
            self.command_query_buttons[key] = query_btn
            self.command_set_buttons[key] = set_btn
            # Fix lambda capture for button connections
            query_btn.clicked.connect(lambda _, k=key: self._query_command(k))
            set_btn.clicked.connect(lambda _, k=key: self._set_command(k))
            # Add to grid
            self.grid.addWidget(label, row, col*4)
            self.grid.addWidget(query_btn, row, col*4+1)
            self.grid.addWidget(set_btn, row, col*4+2)
            self.grid.addWidget(field, row, col*4+3)
            self.command_widgets[key] = [label, query_btn, set_btn, field]
            row += 1
            if row == max_rows:
                row = 0
                col += 1
        # Remove setRowStretch for better alignment

    def update_command_visibility(self):
        # Show/hide implemented widgets
        for cmd in self.command_widgets:
            for widget in self.command_widgets[cmd]:
                widget.setVisible(self.command_prefs.get(cmd, False))
        # For commands not implemented, add generic widgets if enabled
        for cmd in ALL_AT_COMMANDS:
            key = cmd["key"]
            if key not in self.command_widgets:
                if self.command_prefs.get(key, False):
                    if not hasattr(self, f"_gen_{key}_widget"):
                        # Create generic widget
                        section = QWidget()
                        layout = QHBoxLayout(section)
                        label = QLabel(cmd["label"])
                        label.setToolTip(cmd["tooltip"])
                        input_field = QLineEdit()
                        input_field.setPlaceholderText(cmd["param_hint"])
                        send_btn = QPushButton("Send")
                        send_btn.setToolTip(f"Send {cmd['label']}")
                        send_btn.clicked.connect(lambda _, k=key, f=input_field: self.send_generic_command(k, f))
                        layout.addWidget(label)
                        layout.addWidget(input_field)
                        layout.addWidget(send_btn)
                        self.layout.addWidget(section)
                        setattr(self, f"_gen_{key}_widget", section)
                    getattr(self, f"_gen_{key}_widget").setVisible(True)
                else:
                    if hasattr(self, f"_gen_{key}_widget"):
                        getattr(self, f"_gen_{key}_widget").setVisible(False)

    def send_generic_command(self, key, input_field):
        # Find the command template
        cmd_info = next((c for c in ALL_AT_COMMANDS if c["key"] == key), None)
        if cmd_info:
            base = cmd_info["label"].split()[0]  # e.g., AT+PAIR=
            param = input_field.text().strip()
            if param and '=' in base:
                command = f"{base}{param}"
            elif param:
                command = f"{base} {param}"
            else:
                command = base
            self.send_at_command(command)
            input_field.clear()

    def save_profile(self):
        if not self.profile_path:
            self.saveas_profile()
            return
        data = {}
        for cmd, enabled in self.command_prefs.items():
            if enabled and cmd in self.command_fields:
                data[cmd] = self.command_fields[cmd].text()
        with open(self.profile_path, 'w') as f:
            import json
            json.dump(data, f)
        self.set_profile_title()

    def saveas_profile(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Config Profile", "", "Config Files (*.cfg)")
        if path:
            if not path.endswith('.cfg'):
                path += '.cfg'
            self.profile_path = path
            self.save_profile()

    def open_profile(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Config Profile", "", "Config Files (*.cfg)")
        if path:
            self.profile_path = path
            with open(path, 'r') as f:
                import json
                data = json.load(f)
            for cmd, value in data.items():
                if cmd in self.command_fields:
                    self.command_fields[cmd].setText(value)
            self.set_profile_title()

    def open_preferences(self):
        from PyQt5.QtWidgets import QDialog, QGridLayout, QCheckBox, QDialogButtonBox
        dlg = QDialog(self)
        dlg.setWindowTitle("Customize Commands")
        grid = QGridLayout(dlg)
        self.checkboxes = {}
        max_rows = 10
        row = col = 0
        for idx, cmd in enumerate(ALL_AT_COMMANDS):
            cb = QCheckBox(f"{cmd['label']}")
            cb.setChecked(self.command_prefs.get(cmd["key"], False))
            cb.setToolTip(cmd["tooltip"])
            self.checkboxes[cmd["key"]] = cb
            grid.addWidget(cb, row, col)
            row += 1
            if row == max_rows:
                row = 0
                col += 1
        # Always move to a new row for the button box
        if row != 0:
            row += 1
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        grid.addWidget(btns, row, 0, 1, col+1)
        if dlg.exec_():
            for cmd in ALL_AT_COMMANDS:
                self.command_prefs[cmd["key"]] = self.checkboxes[cmd["key"]].isChecked()
            self.save_command_prefs()
            self._populate_command_grid()
            self.update_command_visibility()

    def reset_default_parameters(self):
        for cmd in ALL_AT_COMMANDS:
            self.command_prefs[cmd["key"]] = (cmd["key"] in DEFAULT_ENABLED)
        self.save_command_prefs()
        self._populate_command_grid()
        self.update_command_visibility()
        QMessageBox.information(self, "Defaults Restored", "Default parameters have been restored.")

    def closeEvent(self, event):
        # Save window geometry and command prefs
        self.save_command_prefs()
        try:
            geo = self.saveGeometry().data().hex()
            with open(CONFIG_PATH, 'r+') as f:
                data = json.load(f)
                data['window_geometry'] = geo
                f.seek(0)
                json.dump(data, f)
                f.truncate()
        except Exception:
            pass
        super().closeEvent(event)

    def restore_window_geometry(self):
        try:
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, 'r') as f:
                    data = json.load(f)
                geo = data.get('window_geometry')
                if geo:
                    from PyQt5.QtCore import QByteArray
                    self.restoreGeometry(QByteArray.fromHex(geo.encode()))
        except Exception:
            pass

    def _query_command(self, key):
        # Always populate the field with the response
        self.send_at_command(self._get_query_command_string(key), update_field=key)

    def get_all_parameters(self):
        self._batch_queue = []
        for cmd in ALL_AT_COMMANDS:
            key = cmd["key"]
            if self.command_prefs.get(key, False) and key in self.command_fields:
                if '?' in cmd["label"] or key in ["NAME", "ROLE", "PSWD", "UART", "CMODE"]:
                    self._batch_queue.append(("query", key))
        self._batch_mode = "query"
        self._process_next_batch_command()

    def set_all_parameters(self):
        self._batch_queue = []
        for cmd in ALL_AT_COMMANDS:
            key = cmd["key"]
            if self.command_prefs.get(key, False) and key in self.command_fields:
                value = self.command_fields[key].text().strip()
                if value:
                    self._batch_queue.append(("set", key))
        self._batch_mode = "set"
        self._process_next_batch_command()

    def _process_next_batch_command(self):
        if not self._batch_queue:
            self._batch_mode = None
            self._batch_waiting = False
            return
        action, key = self._batch_queue.pop(0)
        self._batch_waiting = True
        if action == "query":
            self._batch_last_key = key
            self._batch_timer.start(2000)  # 2 second timeout
            self.send_at_command(self._get_query_command_string(key), update_field=key, batch_mode=True)
        elif action == "set":
            self._batch_last_key = key
            self._batch_timer.start(2000)
            self._set_command(key, batch_mode=True)

    def _batch_timeout(self):
        # Timeout: move to next command
        self._batch_waiting = False
        self._process_next_batch_command()

    def _set_command(self, key, batch_mode=False):
        value = self.command_fields[key].text().strip()
        if not value and key not in {"RESET", "INIT", "INQ", "DISC", "ORGL", "RMAAD"}:
            if not batch_mode:
                QMessageBox.warning(self, "Input Required", "Please enter a value.")
            return
        # Map to specific method if implemented, else generic
        if key == "NAME":
            self.send_at_command(f'AT+NAME={value}', batch_mode=batch_mode)
        elif key == "ROLE":
            if value in ['0', '1', '2']:
                self.send_at_command(f'AT+ROLE={value}', batch_mode=batch_mode)
            else:
                if not batch_mode:
                    QMessageBox.warning(self, "Invalid Role", "Role must be 0 (Slave), 1 (Master), or 2 (Slave-Loop)")
        elif key == "PSWD":
            self.send_at_command(f'AT+PSWD={value}', batch_mode=batch_mode)
        elif key == "UART":
            self.send_at_command(f'AT+UART={value}', batch_mode=batch_mode)
        elif key == "CMODE":
            if value in ['0', '1', '2']:
                self.send_at_command(f'AT+CMODE={value}', batch_mode=batch_mode)
            else:
                if not batch_mode:
                    QMessageBox.warning(self, "Invalid CMODE", "CMODE must be 0, 1, or 2.")
        elif key == "RESET":
            self.send_at_command('AT+RESET', read_response=False, batch_mode=batch_mode)
            if not batch_mode:
                QMessageBox.information(self, "Reset", "AT+RESET sent. Module will reboot.")
        else:
            self.send_at_command(self._get_set_command_string(key, value), batch_mode=batch_mode)
        self.command_fields[key].clear()

    def _get_query_command_string(self, key):
        # Returns the correct AT command string for querying a parameter
        # Handles all commands, including custom/added ones
        for cmd in ALL_AT_COMMANDS:
            if cmd["key"] == key:
                # Prefer the first AT+... pattern ending with ?
                if "?" in cmd["label"]:
                    # Extract the first AT+...?
                    for part in cmd["label"].split("/"):
                        part = part.strip()
                        if part.endswith("?"):
                            return part
                # Fallback: AT+KEY?
                break
        return f"AT+{key}?"

    def clear_terminal(self):
        self.terminal_output.clear()

print('main.py starting...')

if __name__ == "__main__":
    print('Launching QApplication...')
    app = QApplication(sys.argv)
    window = HC05Configurator()
    sys.exit(app.exec_())
