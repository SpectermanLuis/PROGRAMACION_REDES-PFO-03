import socket
import json
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor

# ============================================================
# CONFIGURACION DEL SERVIDOR
# ============================================================

HOST = "127.0.0.1"
PUERTO = 5000

# Cola donde se guardan las tareas pendientes.
cola_tareas = queue.Queue()

# Creamos dos Workers.
# Cada Worker dispone de un pool de dos hilos.
workers = [
    ThreadPoolExecutor(max_workers=2),
    ThreadPoolExecutor(max_workers=2)
]

# Control para repartir las tareas por turnos.
contador_workers = 0
lock_workers = threading.Lock()

# Numeracion de las tareas y los clientes.
contador_tareas = 0
contador_clientes = 0
lock_contadores = threading.Lock()


def procesar_tarea(tarea, numero_worker, numero_tarea):
    """Procesa una tarea recibida de un cliente."""

    print(f"\n[WORKER {numero_worker}] Iniciando tarea N.° {numero_tarea}")
    print(f"[WORKER {numero_worker}] Operacion recibida: {tarea}")

    # Simulamos una tarea que tarda un segundo.
    time.sleep(1)

    try:
        partes = tarea.split("+")

        if len(partes) != 2:
            resultado = "Error: ingrese una suma. Ejemplo: 10+5"
        else:
            numero1 = float(partes[0].strip())
            numero2 = float(partes[1].strip())
            suma = numero1 + numero2

            # Evitamos mostrar .0 cuando el resultado es entero.
            if suma.is_integer():
                suma = int(suma)

            resultado = f"Resultado de {tarea}: {suma}"

    except ValueError:
        resultado = "Error: debe ingresar dos numeros validos."

    print(f"[WORKER {numero_worker}] Tarea N.° {numero_tarea} finalizada.")
    print(f"[RESULTADO] Tarea N.° {numero_tarea}: {resultado}")
    print("-" * 60)

    return resultado


def distribuir_tareas():
    """Asigna las tareas pendientes a los Workers."""

    global contador_workers

    while True:
        tarea, cola_respuesta, numero_tarea = cola_tareas.get()

        try:
            # Elegimos el Worker por turnos.
            with lock_workers:
                numero_worker = contador_workers % len(workers)
                contador_workers += 1

            numero_grupo = numero_worker + 1

            print(
                f"[ASIGNACION] Tarea N.° {numero_tarea} "
                f"asignada al Worker {numero_grupo}."
            )

            # Enviamos la tarea al pool de hilos del Worker seleccionado.
            trabajo = workers[numero_worker].submit(
                procesar_tarea,
                tarea,
                numero_grupo,
                numero_tarea
            )

            # Esta funcion se ejecuta cuando termina el procesamiento.
            def completar_respuesta(
                trabajo_terminado,
                cola=cola_respuesta,
                numero=numero_tarea
            ):
                try:
                    resultado = trabajo_terminado.result()
                except Exception as error:
                    resultado = f"Error al procesar la tarea: {error}"

                cola.put(resultado)

                print(
                    f"[RESPUESTA LISTA] Tarea N.° {numero}: "
                    "resultado preparado para el cliente."
                )

            trabajo.add_done_callback(completar_respuesta)

        except Exception as error:
            cola_respuesta.put(
                f"Error al distribuir la tarea: {error}"
            )

        finally:
            cola_tareas.task_done()


def atender_cliente(conexion, direccion, numero_cliente):
    """Atiende las tareas enviadas por un cliente."""

    identificador = f"Cliente {numero_cliente}"

    print(
        f"\n[CONEXION] {identificador} conectado desde "
        f"{direccion[0]}:{direccion[1]}"
    )

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
                                    (
                                        json.dumps(
                                            respuesta,
                                            ensure_ascii=False
                                        ) + "\n"
                                    ).encode("utf-8")
                                )
                                comunicacion.flush()

                                print(
                                    f"[CIERRE] {identificador} "
                                    "solicito finalizar la conexion."
                                )
                                break

                            else:
                                global contador_tareas

                                with lock_contadores:
                                    contador_tareas += 1
                                    numero_tarea = contador_tareas

                                print(
                                    f"\n[TAREA RECIBIDA] N.° {numero_tarea}"
                                )
                                print(f"[CLIENTE] {identificador}")
                                print(f"[OPERACION] {tarea}")

                                # Cola para recibir el resultado de esta tarea.
                                cola_respuesta = queue.Queue(maxsize=1)

                                # Agregamos la tarea a la cola general.
                                cola_tareas.put(
                                    (tarea, cola_respuesta, numero_tarea)
                                )

                                print(
                                    f"[COLA] Tarea N.° {numero_tarea} "
                                    "agregada a la cola de tareas."
                                )

                                # Esperamos el resultado del Worker.
                                resultado = cola_respuesta.get()

                                respuesta = {
                                    "resultado": resultado
                                }

                                print(
                                    f"[ENVIO] Resultado de la tarea "
                                    f"N.° {numero_tarea} enviado a {identificador}."
                                )

                except (json.JSONDecodeError, UnicodeDecodeError):
                    respuesta = {
                        "resultado": "Error: el mensaje recibido no es valido."
                    }

                # Devolvemos la respuesta al cliente.
                comunicacion.write(
                    (
                        json.dumps(
                            respuesta,
                            ensure_ascii=False
                        ) + "\n"
                    ).encode("utf-8")
                )
                comunicacion.flush()

    except OSError as error:
        print(f"[ERROR] Comunicacion con {identificador}: {error}")

    finally:
        conexion.close()
        print(f"[DESCONECTADO] {identificador} desconectado.")


def iniciar_servidor():
    """Inicia el servidor y espera conexiones."""

    global contador_clientes

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

        print("\n" + "=" * 60)
        print("                  SERVIDOR DE TAREAS")
        print("=" * 60)
        print(f"Direccion IP          : {HOST}")
        print(f"Puerto                : {PUERTO}")
        print(f"Cantidad de Workers   : {len(workers)}")
        print("Hilos por Worker      : 2")
        print("Total de hilos de procesamiento: 4")
        print("-" * 60)
        print("[ESTADO] Servidor iniciado correctamente.")
        print("[ESTADO] Esperando conexiones de clientes.")
        print("[AYUDA] Para detener el servidor, presione Ctrl+C.")
        print("=" * 60)

        while True:
            try:
                conexion, direccion = servidor.accept()

                with lock_contadores:
                    contador_clientes += 1
                    numero_cliente = contador_clientes

                # Cada cliente es atendido en un hilo independiente.
                hilo_cliente = threading.Thread(
                    target=atender_cliente,
                    args=(conexion, direccion, numero_cliente),
                    daemon=True
                )
                hilo_cliente.start()

            except socket.timeout:
                continue

    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("[CIERRE] Solicitud de detencion recibida.")
        print("[CIERRE] Cerrando el servidor...")
        print("=" * 60)

    except OSError as error:
        print(f"\n[ERROR] No se pudo iniciar o ejecutar el servidor: {error}")

    finally:
        servidor.close()

        # Esperamos que terminen las tareas que ya estan ejecutandose.
        for worker in workers:
            worker.shutdown(wait=True)

        print("[ESTADO] Servidor detenido.")


if __name__ == "__main__":
    iniciar_servidor()