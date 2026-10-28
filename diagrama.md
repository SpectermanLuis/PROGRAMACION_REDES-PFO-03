
# Diagrama de arquitectura distribuida

El siguiente diagrama representa la arquitectura propuesta
para el sistema distribuido.

![Diagrama de arquitectura distribuida](diagrama/diagrama.png)

# Diagrama de arquitectura distribuida

## 1. Introducción

En este documento se presenta el diagrama de arquitectura propuesto para el sistema distribuido correspondiente al trabajo práctico.

La idea principal es mostrar cómo se podrían organizar los diferentes componentes de un sistema cliente-servidor para recibir solicitudes, distribuir las tareas entre distintos servidores y devolver los resultados a los clientes.

En un sistema distribuido, las tareas no tienen que ser realizadas necesariamente por un único programa o una sola computadora. Se pueden repartir entre diferentes componentes que trabajan de manera coordinada. Esto permite organizar mejor el procesamiento y facilita la posibilidad de ampliar el sistema si aumenta la cantidad de usuarios o de solicitudes.

## 2. Diagrama de arquitectura

El diagrama representa una arquitectura de referencia que incluye clientes, un balanceador de carga, servidores trabajadores, una cola de mensajes, una base de datos y un sistema para almacenar archivos.

Cada uno de estos componentes cumple una función determinada dentro del sistema. En conjunto, permiten representar una posible solución para procesar solicitudes de manera distribuida.

## 3. Descripción de los componentes

### 3.1. Clientes

Los clientes son los programas o dispositivos desde los cuales los usuarios realizan solicitudes al sistema. Pueden ser, por ejemplo, una computadora, una aplicación web o un celular.

El cliente envía una solicitud y espera recibir una respuesta con el resultado del procesamiento. En la implementación realizada para este trabajo, se utiliza un programa en Python que se conecta al servidor mediante sockets y envía una tarea para que sea procesada.

### 3.2. Balanceador de carga: Nginx o HAProxy

El balanceador de carga es un componente que permite distribuir las solicitudes recibidas entre diferentes servidores.

Por ejemplo, si existen varios servidores disponibles, el balanceador puede enviar una solicitud a uno de ellos y otra solicitud a otro. De esta manera, se busca evitar que todo el trabajo quede concentrado en un solo servidor.

En el diagrama se mencionan Nginx y HAProxy porque son herramientas que pueden utilizarse para cumplir esta función. Para este trabajo se muestran como parte de la arquitectura propuesta, pero no se instalaron ni se utilizaron en el programa desarrollado.

### 3.3. Servidores trabajadores

Los servidores trabajadores son los encargados de realizar las tareas que reciben del sistema. En una arquitectura distribuida se pueden utilizar varios servidores para repartir el procesamiento.

Cada servidor puede contar con un grupo de hilos que permita ejecutar más de una tarea. Los hilos son una forma de realizar diferentes trabajos dentro de un mismo programa, sin necesidad de iniciar un programa completamente separado para cada tarea.

En la implementación de Python se utiliza `ThreadPoolExecutor` para organizar la ejecución de las tareas mediante grupos de trabajadores. Para representar la arquitectura propuesta, el diagrama muestra dos servidores trabajadores. En el programa realizado, estos grupos de trabajadores se simulan dentro de un mismo servidor y no son dos computadoras independientes.

### 3.4. Cola de mensajes: RabbitMQ

Una cola de mensajes permite guardar solicitudes pendientes para que puedan ser procesadas cuando corresponda. Esto ayuda a separar la recepción de las tareas de su procesamiento.

Por ejemplo, si llegan varias solicitudes en poco tiempo, las tareas pueden quedar esperando en una cola hasta que los trabajadores estén disponibles. Así se puede organizar mejor el trabajo y evitar que las solicitudes se pierdan por intentar procesarlas todas al mismo tiempo.

En el diagrama se utiliza RabbitMQ como ejemplo de una herramienta que puede cumplir esta función. En el código desarrollado para este trabajo se utiliza la cola `queue` de Python. Por lo tanto, RabbitMQ forma parte del diseño conceptual y no de la implementación realizada.

### 3.5. Base de datos: PostgreSQL

Una base de datos permite guardar información para poder consultarla y utilizarla posteriormente. En un sistema de este tipo podría almacenar, por ejemplo, usuarios, solicitudes, resultados y otros datos necesarios para el funcionamiento de la aplicación.

PostgreSQL es un sistema de gestión de bases de datos que se puede utilizar para almacenar esa información de forma organizada.

En esta propuesta se incluye PostgreSQL como una posible solución para una versión más completa del sistema. Sin embargo, el programa de Python desarrollado para esta entrega no utiliza PostgreSQL ni necesita una base de datos para realizar las operaciones de prueba.

### 3.6. Almacenamiento de archivos: S3 o MinIO

En algunas aplicaciones es necesario guardar archivos, documentos, imágenes u otros elementos que no conviene manejar directamente como parte de los mensajes de las solicitudes.

Para esa función se puede utilizar un sistema de almacenamiento de objetos, como Amazon S3 o MinIO. Estos servicios permiten almacenar archivos y recuperarlos cuando sea necesario.

En el diagrama se incluyen como parte de la arquitectura propuesta, pero no se implementaron en el programa desarrollado para este trabajo práctico.

## 4. Funcionamiento general de la arquitectura

El funcionamiento propuesto puede explicarse de la siguiente manera:

1. El cliente genera una solicitud y la envía al sistema.
2. El balanceador de carga recibe la solicitud y la dirige hacia uno de los servidores trabajadores disponibles.
3. La tarea puede colocarse en una cola de mensajes para organizar su procesamiento.
4. Los trabajadores toman las tareas pendientes y realizan las operaciones correspondientes.
5. Si la tarea necesita consultar o guardar información, los componentes del sistema podrían utilizar la base de datos.
6. Si se necesita almacenar un archivo, se podría utilizar el sistema de almacenamiento correspondiente.
7. Una vez finalizado el procesamiento, el resultado debe regresar al cliente que realizó la solicitud.

Esta descripción representa el funcionamiento general que se busca con la arquitectura propuesta. La forma exacta de comunicación entre los componentes dependerá de cómo se implemente cada uno.

## 5. Relación con el programa desarrollado

Para realizar este trabajo práctico se desarrolló una versión simplificada en Python, utilizando sockets, hilos, colas y grupos de trabajadores.

El cliente se conecta al servidor mediante una conexión TCP y envía una tarea en formato JSON. El servidor recibe el mensaje, organiza la tarea en una cola y la asigna a un grupo de trabajadores para su procesamiento. Una vez obtenido el resultado, el servidor lo devuelve al cliente.

De esta manera, se ponen en práctica algunos conceptos importantes de los sistemas distribuidos, como la comunicación entre procesos, la atención de conexiones de clientes y la distribución de tareas entre trabajadores.

Es importante aclarar que el programa realizado no implementa todos los componentes que aparecen en el diagrama. El balanceador Nginx o HAProxy, RabbitMQ, PostgreSQL y S3 o MinIO se incluyen como parte del diseño conceptual de una posible arquitectura más completa. La implementación de esta entrega se concentra en los conceptos que se pueden demostrar con Python y sus herramientas de concurrencia y comunicación.

## 6. Conclusión

A partir de este trabajo se puede observar que un sistema distribuido requiere organizar la comunicación entre sus componentes y definir qué función cumple cada uno.

La utilización de varios trabajadores permite repartir el procesamiento, mientras que las colas ayudan a ordenar las tareas pendientes. Por otro lado, un balanceador de carga puede distribuir las solicitudes entre distintos servidores, y una base de datos y un sistema de almacenamiento permiten conservar la información necesaria.

La implementación desarrollada en Python representa una versión inicial y simplificada de esta idea. Aunque no incluye todas las herramientas mencionadas en el diagrama, permite comprender y poner en práctica algunos de los conceptos fundamentales para construir sistemas distribuidos.