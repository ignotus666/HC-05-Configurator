def validate_input(input_value, expected_type=str):
    if expected_type == str:
        return isinstance(input_value, str) and len(input_value) > 0
    elif expected_type == int:
        return isinstance(input_value, int) and input_value >= 0
    return False

def format_response(response):
    return response.strip().decode('utf-8') if isinstance(response, bytes) else str(response)

def manage_serial_connection(port, baudrate=9600):
    import serial
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def close_serial_connection(ser):
    if ser and ser.is_open:
        ser.close()