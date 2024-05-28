# Instalación y Configuración de Apache Airflow para Integración CAPTURA - CIPE

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalados los siguientes programas:

- Python (versión 3.6 o superior)
- `pip` (gestor de paquetes de Python)
- `virtualenv` (puede instalarse con `pip install virtualenv` si no lo tienes)

## Pasos para la Instalación
# Crear la Carpeta "airflow", una Variable desde la Interfaz Web de Airflow

1. Desde la línea de comandos, crea la carpeta "airflow" y dentro "dags" en el directorio deseado. Por ejemplo:/home/tu-user/airflow/dags

```
mkdir /home/tu-user/airflow/dags
```
### clonar el siguiente repositorio
```
git clone https://github.com/Christian-Arce/Captura-Cipe-DataFlow.git
```

### Copiar el contenido clonado a dags
```
cp captura_data.env ~/airflow/dags
cp cipe_data.env ~/airflow/dags
cp test-airflow.py ~/airflow/dags
```

### Crear y Activar un Entorno Virtual
- Crear un nuevo entorno virtual llamado "airflow_env"
```
virtualenv airflow_env
```

### Activar el entorno virtual
```
source airflow_env/bin/activate
```
### Definir la variable de entorno AIRFLOW_HOME
```
export AIRFLOW_HOME=~/home/tu-user/airflow
```
### Instalar Apache Airflow
```
pip install apache-airflow
```
### Dentro de /airflow crear la carpeta dags
```
mkdir dags
```
### Inicializar la base de datos de Airflow
```
airflow db init
```
### Crear un usuario administrador para poder acceder a la interfaz web de Airflow
```
airflow users create \
    --username admin \
    --firstname Nombre \
    --lastname Apellido \
    --role Admin \
    --email admin@example.com \
    --password tu_contraseña
```
### Iniciar el servidor web de Airflow
```
airflow webserver -p 9090
```

### Dentro del entorno virtual, activar el scheduler
```
source airflow_env/bin/activate
```
```
airflow scheduler
```

### Crear Variable "processes_ids" desde la Interfaz Web de Airflow

1. Ve a la interfaz web de Airflow.

2. En el menú de navegación izquierdo, selecciona "Admin".

3. Selecciona "Variables" en el menú desplegable.

4. Haz clic en el botón "+".

5. Llena los campos requeridos:

   - **Key (Clave)**: Ingresa el nombre de la variable, "processes_ids".

   - **Value (Valor)**: Ingresa el valor inicial,`[]` (una lista vacía).

6. Haz clic en el botón "Save".
