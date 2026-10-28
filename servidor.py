import socket
import json
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

# Configuracion del servidor
HOST = "127.0.0.1"
PUERTO = 5000

# Cola donde se guardan las tareas pendientes
cola_tareas = queue.Queue()

# Creamos dos grupos de trabajadores.
# Cada grupo puede ejecutar hasta dos tareas al mismo tiempo.
workers = [
    ThreadPoolExecutor(max_workers=2),
    ThreadPoolExecutor(max_workers=2)
]

# Control para repartir las tareas entre los trabajadores
contador_workers = 0
lock_workers = threading.Lock()


def procesar_tarea(tarea, numero_worker):
    """Procesa una tarea recibida del cliente."""

    print(f"Worker {numero_worker}: procesando la tarea '{tarea}'")

    # Simulamos una tarea que tarda un poco en ejecutarse.
    # Esto permite observar el trabajo simultaneo de los workers.
    time.sleep(1)

    try:
        partes = tarea.split("+")

        if len(partes) != 2:
            return "Error: ingrese una suma. Ejemplo: 10+5"

        numero1 = float(partes[0].strip())
        numero2 = float(partes[1].strip())

        resultado = numero1 + numero2

        return f"Resultado de {tarea}: {resultado}"

    except ValueError:
        return "Error: debe ingresar dos numeros validos."


def distribuir_tareas():
    """Asigna las tareas pendientes a los grupos de trabajadores."""

    global contador_workers

    while True:
        tarea, cola_respuesta = cola_tareas.get()

        try:
            # Elegimos el grupo de trabajadores por turnos.
            with lock_workers:
                numero_worker = contador_workers % len(workers)
                contador_workers += 1

            # Enviamos la tarea al grupo seleccionado.
            trabajo = workers[numero_worker].submit(
                procesar_tarea,
                tarea,
                numero_worker + 1
            )

            # Esta funcion se ejecuta cuando termina el procesamiento.
            # El parametro por defecto conserva la cola de respuesta
            # correspondiente a esta tarea.
            def completar_respuesta(
                trabajo_terminado,
                cola=cola_respuesta
            ):
                try:
                    resultado = trabajo_terminado.result()
                except Exception as error:
                    resultado = f"Error al procesar la tarea: {error}"

                cola.put(resultado)

            trabajo.add_done_callback(completar_respuesta)

        except Exception as error:
            cola_respuesta.put(
                f"Error al distribuir la tarea: {error}"
            )

        finally:
            cola_tareas.task_done()


def atender_cliente(conexion, direccion):
    """Atiende las tareas enviadas por un cliente."""

    print(f"Cliente conectado: {direccion}")

    try:
        # Usamos mensajes terminados en salto de linea.
        with conexion.makefile("rwb") as comunicacion:

            while True:
                linea = comunicacion.readline()

                if not linea:
                    break

                try:
                    mensaje = json.loads(linea.decode("utf-8"))

                    if not isinstance(mensaje, dict):
                        respuesta = {
                            "resultado": "Error: mensaje no valido."
                        }

                    else:
                        tarea = mensaje.get("tarea", "")

                        if not isinstance(tarea, str):
                            respuesta = {
                                "resultado": "Error: la tarea debe ser texto."
                            }

                        else:
                            tarea = tarea.strip()

                            if not tarea:
                                respuesta = {
                                    "resultado": "Error: la tarea esta vacia."
                                }

                            elif tarea.upper() == "SALIR":
                                respuesta = {
                                    "resultado": "Conexion finalizada."
                                }

                                comunicacion.write(
                                    (json.dumps(respuesta) + "\n").encode("utf-8")
                                )
                                comunicacion.flush()
                                break

                            else:
                                # Creamos una cola para recibir el resultado
                                # de esta tarea en particular.
                                cola_respuesta = queue.Queue(maxsize=1)

                                # Enviamos la tarea a la cola general.
                                cola_tareas.put((tarea, cola_respuesta))

                                # Esperamos el resultado de los workers.
                                resultado = cola_respuesta.get()

                                respuesta = {
                                    "resultado": resultado
                                }

                except (json.JSONDecodeError, UnicodeDecodeError):
                    respuesta = {
                        "resultado": "Error: el mensaje recibido no es valido."
                    }

                # Devolvemos la respuesta al cliente.
                comunicacion.write(
                    (json.dumps(respuesta, ensure_ascii=False) + "\n").encode("utf-8")
                )
                comunicacion.flush()

    except OSError as error:
        print(f"Error de comunicacion con {direccion}: {error}")

    finally:
        conexion.close()
        print(f"Cliente desconectado: {direccion}")


def iniciar_servidor():
    """Inicia el servidor y espera conexiones."""

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        servidor.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        servidor.bind((HOST, PUERTO))
        servidor.listen()
        servidor.settimeout(1)

        # Iniciamos el hilo que distribuye las tareas.
        hilo_distribuidor = threading.Thread(
            target=distribuir_tareas,
            daemon=True
        )
        hilo_distribuidor.start()

        print(f"Servidor iniciado en {HOST}:{PUERTO}")
        print("Esperando conexiones de clientes...")
        print("Para detener el servidor, presione Ctrl+C.")

        while True:
            try:
                conexion, direccion = servidor.accept()

                # Cada cliente es atendido en un hilo independiente.
                hilo_cliente = threading.Thread(
                    target=atender_cliente,
                    args=(conexion, direccion),
                    daemon=True
                )
                hilo_cliente.start()

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")

    except OSError as error:
        print(f"Error al iniciar o ejecutar el servidor: {error}")

    finally:
        servidor.close()

        # Esperamos que terminen las tareas que ya estan ejecutandose.
        for worker in workers:
            worker.shutdown(wait=True)

        print("Servidor detenido.")


if __name__ == "__main__":
    iniciar_servidor()