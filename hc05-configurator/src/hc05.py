class HC05:
    def __init__(self, port):
        import serial
        self.port = port
        self.baudrate = 9600
        self.serial_connection = serial.Serial(self.port, self.baudrate, timeout=1)

    def send_command(self, command):
        self.serial_connection.write((command + '\r\n').encode())
        response = self.serial_connection.readline().decode().strip()
        return response

    def reset(self):
        return self.send_command('AT+RESET')

    def get_name(self):
        return self.send_command('AT+NAME?')

    def set_name(self, name):
        return self.send_command(f'AT+NAME={name}')

    def get_role(self):
        return self.send_command('AT+ROLE?')

    def set_role(self, role):
        return self.send_command(f'AT+ROLE={role}')

    def get_password(self):
        return self.send_command('AT+PSWD?')

    def set_password(self, password):
        return self.send_command(f'AT+PSWD={password}')

    def get_uart(self):
        return self.send_command('AT+UART?')

    def set_uart(self, params):
        return self.send_command(f'AT+UART={params}')

    def close(self):
        self.serial_connection.close()