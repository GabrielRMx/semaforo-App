import socket
import tkinter as tk
import random
import threading


class TrafficLightClient:
    def __init__(self, client_id):
        self.client_id = client_id
        self.root = tk.Tk()
        self.root.title(f"Semáforo {client_id}")

        self.canvas = tk.Canvas(self.root, width=200, height=400)
        self.canvas.pack()

        self.light = {
            "red": self.canvas.create_oval(50, 50, 150, 150, fill="gray"),
            "yellow": self.canvas.create_oval(50, 170, 150, 270, fill="gray"),
            "green": self.canvas.create_oval(50, 290, 150, 390, fill="gray")
        }

        self.vehicle_count = tk.IntVar(value=random.randint(0, 50))
        tk.Label(self.root, text="Número de vehículos:").pack()
        tk.Entry(self.root, textvariable=self.vehicle_count).pack()

        # Iniciar la conexión en un hilo separado
        threading.Thread(target=self.start_connection).start()

        # Comenzar la simulación del número de autos
        self.simulate_traffic()

        self.root.mainloop()

    def start_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            print(f"[INFO] Conectando al servidor...")
            self.socket.connect(("192.168.68.116", 9090))
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
            # Preparar el mensaje con el ID del semáforo y el número de vehículos
            message = f"{self.client_id}:{self.vehicle_count.get()}"
            
            # Enviar el mensaje al servidor
            self.socket.send(message.encode())

            # Recibir la respuesta del servidor
            response = self.socket.recv(1024).decode()

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

    def simulate_traffic(self):
        # Cambiar el número de vehículos cada 2 segundos
        new_count = self.vehicle_count.get() + random.randint(-5, 5)
        if new_count < 0:
            new_count = 0
        elif new_count > 10:
            new_count = 10
        self.vehicle_count.set(new_count)

        print(f"[INFO] Semáforo {self.client_id} - Vehículos: {new_count}")

        # Repetir la simulación cada 2 segundos
        self.root.after(2000, self.simulate_traffic)


if __name__ == "__main__":
    client1 = TrafficLightClient("semaforo2")  # Cambia a "semaforo2" para el segundo semáforo
