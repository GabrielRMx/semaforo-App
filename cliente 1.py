import socket
import tkinter as tk
import threading


class TrafficLightClient:
    def __init__(self, client_id, listen_port):
        self.client_id = client_id
        self.listen_port = listen_port
        self.vehicle_count = 100

        self.root = tk.Tk()
        self.root.title(f"Semáforo {client_id}")

        self.canvas = tk.Canvas(self.root, width=200, height=400)
        self.canvas.pack()

        self.light = {
            "red": self.canvas.create_oval(50, 50, 150, 150, fill="gray"),
            "yellow": self.canvas.create_oval(50, 170, 150, 270, fill="gray"),
            "green": self.canvas.create_oval(50, 290, 150, 390, fill="gray")
        }

        tk.Label(self.root, text="Número de vehículos:").pack()
        tk.Entry(self.root, textvariable=self.vehicle_count).pack()

        # Iniciar la conexión al servidor en un hilo separado
        threading.Thread(target=self.start_connection).start()

        # Iniciar la escucha para Cliente 1.2 en otro hilo separado
        threading.Thread(target=self.listen_for_vehicle_data).start()

        self.root.mainloop()

    def start_connection(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"[INFO] Conectando al servidor...")
            self.server_socket.connect(("10.42.0.1", 9090))
            self.server_socket.send(self.client_id.encode())
            print(f"[INFO] Conectado al servidor. Iniciando ciclo de luces...")
            self.cycle_lights()
        except Exception as e:
            print(f"[ERROR] Error de conexión: {e}")
            self.root.quit()  # Cerrar la aplicación si falla la conexión

    def change_light(self, color):
        for light in self.light:
            self.canvas.itemconfig(self.light[light], fill="gray")
        self.canvas.itemconfig(self.light[color], fill=color)

    def cycle_lights(self):
        try:
            # Enviar el número de vehículos al servidor
            message = f"{self.client_id}:{self.vehicle_count}"
            self.server_socket.send(message.encode())

            # Recibir la respuesta del servidor
            response = self.server_socket.recv(1024).decode()
            print(f"[INFO] Respuesta del servidor: {response}")

            if response == self.client_id:
                self.change_light("green")
            else:
                self.change_light("red")

            # Espera de 3 segundos antes de la siguiente actualización
            self.root.after(3000, self.cycle_lights)
        except Exception as e:
            print(f"[ERROR] Error de comunicación: {e}")
            self.root.quit()  # Cerrar la aplicación si falla la comunicación

    def listen_for_vehicle_data(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.bind(("0.0.0.0", self.listen_port))
        listen_socket.listen(1)
        print(f"[INFO] Esperando datos de Cliente 1.2 en el puerto {self.listen_port}...")

        while True:
            client_socket, addr = listen_socket.accept()
            print(f"[INFO] Conexión aceptada desde {addr}")

            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                print(f"[INFO] Datos recibidos de Cliente 1.2: {data}")
                self.vehicle_count = int(data.split(":")[1])

            client_socket.close()


if __name__ == "__main__":
    client1 = TrafficLightClient("semaforo1", 9091)
