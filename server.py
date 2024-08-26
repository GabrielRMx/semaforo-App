import socket
import threading
import time

# Diccionario para almacenar el número de vehículos de cada semáforo
traffic_data = {"semaforo1": 0, "semaforo2": 0}
green_light = "semaforo1"  # Inicialmente, semáforo 1 está en verde
last_change_time = time.time()  # Tiempo del último cambio de semáforo
base_green_time = 7  # Tiempo base que un semáforo debe estar en verde (en segundos)
time_per_vehicle = 5  # Tiempo adicional por vehículo en cola (en segundos)

def calculate_green_time(vehicle_count):
    """
    Calcula el tiempo que un semáforo debería permanecer en verde
    en función del número de vehículos.
    """
    return base_green_time + (vehicle_count * time_per_vehicle)

def get_remaining_time(semaforo):
    """
    Calcula el tiempo restante antes de cambiar el semáforo actual.
    """
    current_green_time = calculate_green_time(traffic_data[semaforo])
    elapsed_time = time.time() - last_change_time
    remaining_time = max(0, current_green_time - elapsed_time)  # Evita tiempos negativos
    return remaining_time

def handle_client(client_socket):
    global traffic_data, green_light, last_change_time

    while True:
        # Recibir datos del cliente (número de vehículos)
        vehicle_data = client_socket.recv(1024).decode().strip()
        if not vehicle_data:
            break

        # Separar el identificador del semáforo y el número de vehículos
        try:
            client_id, vehicle_count = vehicle_data.split(':')
            vehicle_count = int(vehicle_count)  # Convertir a entero
        except ValueError:
            print(f"[ERROR] Formato de mensaje inválido: {vehicle_data}")
            continue
        
        # Actualizar el número de vehículos para el semáforo correspondiente
        traffic_data[client_id] = vehicle_count
        print(f"Received {vehicle_count} vehicles from {client_id}")
        
        # Imprimir el tiempo restante para cada semáforo
        remaining_time_semaforo1 = get_remaining_time("semaforo1")
        remaining_time_semaforo2 = get_remaining_time("semaforo2")
        print(f"Tiempo restante para semaforo1: {remaining_time_semaforo1:.2f} segundos")
        print(f"Tiempo restante para semaforo2: {remaining_time_semaforo2:.2f} segundos")
        
        # Calcular tiempo transcurrido desde el último cambio de semáforo
        elapsed_time = time.time() - last_change_time
        current_green_time = calculate_green_time(traffic_data[green_light])

        # Verificar si es tiempo de cambiar el semáforo
        if elapsed_time >= current_green_time:
            # Determinar el próximo semáforo a cambiar basado en la cola de vehículos
            if green_light == "semaforo1":
                green_light = "semaforo2"
            else:
                green_light = "semaforo1"

            # Reiniciar el tiempo del último cambio
            last_change_time = time.time()
            print(f"Changed green light to {green_light}")

        # Enviar la respuesta al cliente
        client_socket.send(green_light.encode())

    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("10.42.0.1", 9090))
    server.listen(2)
    print("Server listening on port 9090...")
    
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        # Crear un hilo para manejar el cliente
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
