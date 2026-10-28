import socket
import json

# ============================================================
# CONFIGURACION DEL CLIENTE
# ============================================================

HOST = "127.0.0.1"
PUERTO = 5000


def iniciar_cliente():
    """Conecta con el servidor y envia tareas."""

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PUERTO))

        print("\n" + "=" * 50)
        print("               CLIENTE DE TAREAS")
        print("=" * 50)
        print(f"[CONEXION] Servidor: {HOST}:{PUERTO}")
        print("[AYUDA] Ingrese una suma, por ejemplo: 10+5")
        print("[AYUDA] Para finalizar, escriba SALIR.")
        print("=" * 50)

        # Usamos mensajes terminados en salto de linea.
        with cliente.makefile("rwb") as comunicacion:

            while True:
                tarea = input("\n[TAREA] Ingrese una operacion: ").strip()

                if not tarea:
                    print("[AVISO] Debe ingresar una tarea.")
                    continue

                # Enviamos la tarea en formato JSON.
                mensaje = {
                    "tarea": tarea
                }

                datos = json.dumps(
                    mensaje,
                    ensure_ascii=False
                ) + "\n"

                print(f"[ENVIO] Enviando al servidor: {tarea}")

                comunicacion.write(datos.encode("utf-8"))
                comunicacion.flush()

                # Esperamos la respuesta del servidor.
                linea = comunicacion.readline()

                if not linea:
                    print("[AVISO] El servidor cerro la conexion.")
                    break

                respuesta = json.loads(linea.decode("utf-8"))

                print("-" * 50)
                print("[RESPUESTA] Mensaje recibido del servidor:")
                print(f"            {respuesta.get('resultado', 'Sin resultado')}")
                print("-" * 50)

                if tarea.upper() == "SALIR":
                    print("[CIERRE] Finalizando el cliente.")
                    break

    except ConnectionRefusedError:
        print("\n[ERROR] No se pudo conectar con el servidor.")
        print("        Verifique que servidor.py este ejecutandose.")

    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(f"\n[ERROR DE COMUNICACION] {error}")

    finally:
        cliente.close()
        print("[ESTADO] Cliente finalizado.\n")


if __name__ == "__main__":
    iniciar_cliente()