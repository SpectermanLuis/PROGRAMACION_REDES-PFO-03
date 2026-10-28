import socket
import json

# Configuracion del servidor
HOST = "127.0.0.1"
PUERTO = 5000


def iniciar_cliente():
    """Conecta con el servidor y envia tareas."""

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PUERTO))

        print("Conectado al servidor.")
        print("Ingrese una suma, por ejemplo: 10+5")
        print("Para finalizar, escriba SALIR.\n")

        # Usamos mensajes terminados en salto de linea.
        with cliente.makefile("rwb") as comunicacion:

            while True:
                tarea = input("Ingrese una tarea: ").strip()

                if not tarea:
                    print("Debe ingresar una tarea.")
                    continue

                # Enviamos la tarea en formato JSON.
                mensaje = {
                    "tarea": tarea
                }

                datos = json.dumps(mensaje, ensure_ascii=False) + "\n"

                comunicacion.write(datos.encode("utf-8"))
                comunicacion.flush()

                # Esperamos la respuesta del servidor.
                linea = comunicacion.readline()

                if not linea:
                    print("El servidor cerro la conexion.")
                    break

                respuesta = json.loads(linea.decode("utf-8"))

                print("Respuesta del servidor:", respuesta["resultado"])
                print()

                if tarea.upper() == "SALIR":
                    break

    except ConnectionRefusedError:
        print("No se pudo conectar con el servidor.")
        print("Verifique que servidor.py este ejecutandose.")

    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(f"Error de comunicacion: {error}")

    finally:
        cliente.close()
        print("Cliente finalizado.")


if __name__ == "__main__":
    iniciar_cliente()