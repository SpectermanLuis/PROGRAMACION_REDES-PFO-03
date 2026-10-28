

# PROGRAMACION SOBRE REDES

# PFO 3 - Sistema Distribuido Cliente-Servidor


## Alumno    :  SPECTERMAN LUIS OMAR
## Comision  :  E
## 1. Objetivo

El objetivo de este trabajo es adaptar el sistema cliente-servidor desarrollado en el PFO 1, que consiste en un chat implementado en Python mediante sockets TCP.

Para esta nueva versión, se incorporan mecanismos de concurrencia y distribución de tareas. El servidor recibe los mensajes enviados por los clientes, los almacena en una base de datos SQLite, los organiza en una cola y los distribuye entre grupos de trabajadores (*Workers*) para su procesamiento.

De esta manera, se busca demostrar cómo se pueden atender varios clientes y procesar sus mensajes utilizando conceptos de sistemas distribuidos.

## 2. Tecnologías utilizadas

- **Python:** lenguaje de programación utilizado.
- **Sockets TCP:** permiten la comunicación entre los clientes y el servidor.
- **JSON:** formato utilizado para intercambiar mensajes y respuestas.
- **threading:** permite atender conexiones de clientes mediante hilos separados.
- **queue:** organiza los mensajes pendientes de procesamiento.
- **ThreadPoolExecutor:** permite ejecutar tareas mediante grupos de hilos.
- **SQLite:** almacena los mensajes recibidos y los resultados de su procesamiento.
- **datetime:** permite registrar la fecha y hora de recepción de los mensajes.

## 3. Estructura de archivos

```text
PFO3/
|
|-- servidor.py ................. Recibe mensajes, los almacena
|                                  y distribuye las tareas.
|
|-- cliente.py .................. Permite enviar mensajes
|                                  y recibir respuestas.
|
|-- README.md ................... Documentación general del trabajo.
|
|-- diagrama.md ................. Explicación de la arquitectura propuesta.
|
|-- diagrama/
|   `-- diagrama.png ............. Imagen del diagrama de arquitectura.
|
|-- imagenes/
|   |-- pfo03-imagen01.png ....... Captura del servidor iniciado.
|   |-- pfo03-imagen02.png ....... Captura de los clientes conectados.
|   `-- pfo03-imagen03.png ....... Captura del procesamiento de mensajes.
|
`-- chat.db ..................... Base de datos SQLite generada
                                   automáticamente por el servidor.
```

**Nota:** el archivo `chat.db` se crea al iniciar el servidor si todavía no existe. Si no está incluido en el repositorio, se generará al ejecutar el programa.

## 4. Funcionamiento

El funcionamiento del sistema es el siguiente:

1. El cliente se conecta al servidor mediante un socket TCP.
2. El cliente envía un mensaje de texto en formato JSON.
3. El servidor recibe el mensaje y lo almacena en la base de datos SQLite, junto con la fecha, la hora y la dirección IP del cliente.
4. El mensaje se incorpora a una cola de tareas pendientes.
5. Un distribuidor asigna la tarea a uno de los grupos de Workers disponibles.
6. El Worker procesa el mensaje y registra el resultado en la base de datos.
7. El servidor devuelve al cliente una respuesta con la confirmación del procesamiento.
8. El cliente puede continuar enviando mensajes o finalizar la conexión escribiendo `SALIR`.

### Procesamiento de los mensajes

La tarea implementada consiste en recibir y procesar los mensajes del chat, manteniendo la funcionalidad principal del PFO 1.

Los Workers simulan el procesamiento de cada mensaje y generan una respuesta de confirmación. De esta forma, se puede observar el recorrido de una tarea desde que llega al servidor hasta que se devuelve el resultado al cliente.

## 5. Ejecución

Se necesita tener Python instalado. No es necesario instalar paquetes externos adicionales, ya que se utilizan módulos incluidos en Python.

### 5.1. Iniciar el servidor

Abrir una terminal en la carpeta del proyecto y ejecutar:

```bash
python servidor.py
```

El servidor inicializará la base de datos y quedará esperando conexiones de los clientes.

### 5.2. Iniciar un cliente

Abrir otra terminal en la misma carpeta y ejecutar:

```bash
python cliente.py
```

### 5.3. Probar el chat

Cuando el cliente lo solicite, escribir un mensaje de texto, por ejemplo:

```text
Hola, este es un mensaje de prueba.
```

El servidor recibirá el mensaje, lo almacenará, lo enviará a un Worker para su procesamiento y devolverá una respuesta.

Se pueden abrir varias terminales y ejecutar `cliente.py` en cada una para probar conexiones simultáneas.

### 5.4. Finalizar la conexión

Para cerrar la conexión del cliente, escribir:

```text
SALIR
```

Para detener el servidor, presionar `Ctrl+C` en la terminal donde se está ejecutando.

## 6. Arquitectura conceptual

El diseño de la arquitectura distribuida contempla los siguientes componentes:

- **Clientes web y móviles:** permiten enviar mensajes y recibir respuestas.
- **Balanceador de carga (Nginx o HAProxy):** distribuye las conexiones entre distintos servidores.
- **Servidores Workers:** procesan las tareas utilizando grupos de hilos.
- **Cola de mensajes (RabbitMQ):** permite organizar y distribuir tareas entre los servidores.
- **Base de datos PostgreSQL:** permite almacenar los datos del sistema en una arquitectura ampliada.
- **Almacenamiento de archivos (S3 o MinIO):** permite guardar archivos y otros recursos cuando sean necesarios.

Estos componentes se representan en el diagrama conceptual. No todos están implementados en esta entrega: el programa Python utiliza una cola local mediante `queue`, grupos de hilos mediante `ThreadPoolExecutor` y almacenamiento SQLite.

Por lo tanto, el diagrama representa una posible arquitectura distribuida ampliada, mientras que el código permite demostrar los mecanismos básicos de comunicación, concurrencia y procesamiento de mensajes.

## 7. Pruebas

Se realizarán pruebas para comprobar el funcionamiento del sistema:

- Inicio correcto del servidor.
- Conexión de uno o varios clientes.
- Envío y recepción de mensajes.
- Almacenamiento de los mensajes en SQLite.
- Distribución y procesamiento de los mensajes mediante los Workers.
- Manejo de mensajes vacíos o con formato incorrecto.
- Finalización de la conexión del cliente.

Se incorporarán capturas de pantalla para mostrar el funcionamiento de los programas.

### 7.1. Servidor iniciado y esperando conexiones

![Servidor iniciado](imagenes/pfo03-imagen01.png)

### 7.2. Clientes iniciados y conectados

![Clientes conectados](imagenes/pfo03-imagen02.png)

### 7.3. Servidor y clientes procesando mensajes

![Servidor y clientes procesando mensajes](imagenes/pfo03-imagen03.png)

## 8. Conclusión

El trabajo parte del chat desarrollado en el PFO 1 y lo amplía incorporando una cola de tareas, grupos de Workers y atención concurrente de clientes.

La implementación permite observar cómo se reciben, almacenan y procesan los mensajes, y cómo se devuelve una respuesta a cada cliente.

Además, el diagrama presenta una propuesta de arquitectura distribuida que podría ampliarse en el futuro mediante un balanceador de carga, RabbitMQ y sistemas de almacenamiento distribuidos.
