
# PROGRAMACION SOBRE REDES
# PFO 3 - Adaptacion del chat del PFO 1
# Servidor con sockets, cola de tareas, Workers y SQLite.

import socket
import sqlite3
import json
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

HOST = "127.0.0.1"
PUERTO = 5000
NOMBRE_DB = "chat.db"

cola_tareas = queue.Queue()

# Dos grupos de Workers, cada uno con dos hilos.
workers = [
    ThreadPoolExecutor(max_workers=2),
    ThreadPoolExecutor(max_workers=2)
]

contador_workers = 0
lock_workers = threading.Lock()
lock_db = threading.Lock()


def inicializar_base_datos():
    """Crea la tabla de mensajes del chat."""

    try:
        conexion = sqlite3.connect(NOMBRE_DB)
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                fecha_envio TEXT NOT NULL,
                ip_cliente TEXT NOT NULL,
                resultado TEXT,
                estado TEXT
            )
        """)

        conexion.commit()
        conexion.close()

        print("Base de datos SQLite inicializada.")
        return True

    except sqlite3.Error as error:
        print("Error al inicializar SQLite:", error)
        return False


def guardar_mensaje(contenido, ip_cliente):
    """Guarda el mensaje y devuelve su identificador."""

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with lock_db:
            conexion = sqlite3.connect(NOMBRE_DB)
            cursor = conexion.cursor()

            cursor.execute("""
                INSERT INTO mensajes
                (contenido, fecha_envio, ip_cliente, resultado, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (contenido, fecha, ip_cliente, None, "RECIBIDO"))

            id_mensaje = cursor.lastrowid
            conexion.commit()
            conexion.close()

        return id_mensaje, fecha

    except sqlite3.Error as error:
        print("Error al guardar el mensaje:", error)
        return None, fecha


def actualizar_mensaje(id_mensaje, resultado):
    """Guarda el resultado del procesamiento del mensaje."""

    try:
        with lock_db:
            conexion = sqlite3.connect(NOMBRE_DB)
            cursor = conexion.cursor()

            cursor.execute("""
                UPDATE mensajes
                SET resultado = ?, estado = ?
                WHERE id = ?
            """, (resultado, "PROCESADO", id_mensaje))

            conexion.commit()
            conexion.close()

    except sqlite3.Error as error:
        print("Error al actualizar el mensaje:", error)


def procesar_mensaje(mensaje, numero_worker, id_mensaje):
    """Procesa un mensaje del chat."""

    print(
        f"[WORKER {numero_worker}] "
        f"Procesando mensaje #{id_mensaje}: {mensaje}"
    )

    # Pequeña demora para poder observar el trabajo de los Workers.
    time.sleep(1)

    resultado = f"Mensaje #{id_mensaje} procesado correctamente."
    actualizar_mensaje(id_mensaje, resultado)

    return resultado


def distribuir_tareas():
    """Extrae mensajes de la cola y los asigna a los Workers."""

    global contador_workers

    while True:
        elemento = cola_tareas.get()

        if elemento is None:
            cola_tareas.task_done()
            break

        mensaje, id_mensaje, cola_respuesta = elemento

        try:
            with lock_workers:
                numero_worker = contador_workers % len(workers)
                contador_workers += 1

            trabajo = workers[numero_worker].submit(
                procesar_mensaje,
                mensaje,
                numero_worker + 1,
                id_mensaje
            )

            def completar_respuesta(
                trabajo_terminado,
                respuesta_tarea=cola_respuesta
            ):
                try:
                    resultado = trabajo_terminado.result()
                except Exception as error:
                    resultado = f"Error al procesar el mensaje: {error}"

                respuesta_tarea.put(resultado)

            trabajo.add_done_callback(completar_respuesta)

        except Exception as error:
            cola_respuesta.put(
                f"Error al distribuir el mensaje: {error}"
            )

        finally:
            cola_tareas.task_done()


def enviar_respuesta(comunicacion, respuesta):
    """Envía una respuesta JSON al cliente."""

    datos = json.dumps(respuesta, ensure_ascii=False) + "\n"
    comunicacion.write(datos.encode("utf-8"))
    comunicacion.flush()


def atender_cliente(conexion, direccion):
    """Atiende a cada cliente en un hilo independiente."""

    ip_cliente = direccion[0]
    print(f"[CONEXION] Cliente conectado: {direccion}")

    try:
        with conexion.makefile("rwb") as comunicacion:

            while True:
                linea = comunicacion.readline()

                if not linea:
                    break

                try:
                    mensaje_recibido = json.loads(
                        linea.decode("utf-8")
                    )
                except (json.JSONDecodeError, UnicodeDecodeError):
                    enviar_respuesta(comunicacion, {
                        "resultado": "Error: mensaje no valido."
                    })
                    continue

                if not isinstance(mensaje_recibido, dict):
                    enviar_respuesta(comunicacion, {
                        "resultado": "Error: formato de mensaje incorrecto."
                    })
                    continue

                mensaje = mensaje_recibido.get("mensaje", "")

                if not isinstance(mensaje, str):
                    enviar_respuesta(comunicacion, {
                        "resultado": "Error: el mensaje debe ser texto."
                    })
                    continue

                mensaje = mensaje.strip()

                if not mensaje:
                    enviar_respuesta(comunicacion, {
                        "resultado": "El mensaje no puede estar vacio."
                    })
                    continue

                if mensaje.lower() in ("salir", "éxito", "exito"):
                    enviar_respuesta(comunicacion, {
                        "resultado": "Conexion finalizada."
                    })
                    break

                id_mensaje, fecha = guardar_mensaje(
                    mensaje, ip_cliente
                )

                if id_mensaje is None:
                    enviar_respuesta(comunicacion, {
                        "resultado": "Error al guardar el mensaje en SQLite."
                    })
                    continue

                print(
                    f"[RECIBIDO] Mensaje #{id_mensaje} "
                    f"de {ip_cliente}: {mensaje}"
                )

                cola_respuesta = queue.Queue(maxsize=1)

                cola_tareas.put((
                    mensaje,
                    id_mensaje,
                    cola_respuesta
                ))

                resultado = cola_respuesta.get()

                enviar_respuesta(comunicacion, {
                    "id": id_mensaje,
                    "fecha": fecha,
                    "mensaje": mensaje,
                    "resultado": resultado
                })

    except OSError as error:
        print(f"Error de comunicacion con {direccion}: {error}")

    finally:
        conexion.close()
        print(f"[CIERRE] Cliente desconectado: {direccion}")


def iniciar_servidor():
    if not inicializar_base_datos():
        return

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        servidor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        servidor.bind((HOST, PUERTO))
        servidor.listen()

        hilo_distribuidor = threading.Thread(
            target=distribuir_tareas,
            daemon=True
        )
        hilo_distribuidor.start()

        print("----------------------------------------")
        print(f"Servidor iniciado en {HOST}:{PUERTO}")
        print("Aplicacion: chat cliente-servidor")
        print("Workers: 2 grupos con 2 hilos cada uno")
        print("Cola: queue de Python")
        print("Base de datos: SQLite (chat.db)")
        print("Para detenerlo, presione Ctrl+C.")
        print("----------------------------------------")

        while True:
            conexion, direccion = servidor.accept()

            hilo_cliente = threading.Thread(
                target=atender_cliente,
                args=(conexion, direccion),
                daemon=True
            )
            hilo_cliente.start()

    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")

    except OSError as error:
        print("Error al iniciar el servidor:", error)

    finally:
        servidor.close()

        # Espera a que se vacíe la cola antes de cerrar los Workers.
        cola_tareas.join()

        for worker in workers:
            worker.shutdown(wait=True)

        print("Servidor detenido.")


if __name__ == "__main__":
    iniciar_servidor()
