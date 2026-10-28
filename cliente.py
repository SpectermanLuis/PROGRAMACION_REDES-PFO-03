
# PROGRAMACION SOBRE REDES
# PFO 3 - Cliente de chat basado en el PFO 1

import socket
import json

HOST = "127.0.0.1"
PUERTO = 5000


def conectar_servidor():
    """Crea el socket y se conecta al servidor."""

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        cliente.connect((HOST, PUERTO))

        print("Conectado al servidor.")
        print("Escriba sus mensajes.")
        print("Para finalizar, escriba: salir\n")

        return cliente

    except ConnectionRefusedError:
        print("No se pudo conectar con el servidor.")
        print("Verifique que servidor.py este ejecutandose.")
        cliente.close()
        return None

    except OSError as error:
        print("Error al conectar:", error)
        cliente.close()
        return None


def enviar_mensajes(cliente):
    """Envía mensajes de texto y recibe las respuestas."""

    try:
        with cliente.makefile("rwb") as comunicacion:

            while True:
                mensaje = input("Mensaje: ").strip()

                if not mensaje:
                    print("Escriba un mensaje.\n")
                    continue

                datos = json.dumps(
                    {"mensaje": mensaje},
                    ensure_ascii=False
                ) + "\n"

                comunicacion.write(datos.encode("utf-8"))
                comunicacion.flush()

                linea = comunicacion.readline()

                if not linea:
                    print("El servidor cerro la conexion.")
                    break

                try:
                    respuesta = json.loads(linea.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    print("Respuesta no valida del servidor.")
                    continue

                if "id" in respuesta:
                    print("Numero de mensaje:", respuesta["id"])
                    print("Fecha y hora:", respuesta["fecha"])
                    print("Mensaje recibido:", respuesta["mensaje"])

                print("Servidor:", respuesta.get("resultado", "Sin respuesta"))
                print()

                if mensaje.lower() in ("salir", "éxito", "exito"):
                    break

    except OSError as error:
        print("Error de comunicacion:", error)


def main():
    cliente = conectar_servidor()

    if cliente is not None:
        try:
            enviar_mensajes(cliente)
        finally:
            cliente.close()
            print("Cliente finalizado.")


if __name__ == "__main__":
    main()
