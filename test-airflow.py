from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import json
import random
import string
import os
from dotenv import load_dotenv
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Función para cargar variables de entorno desde un archivo específico
def load_env_file(file_path):
    load_dotenv(dotenv_path=file_path)

load_env_file(os.path.join(os.path.dirname(__file__), 'captura_data.env'))
CAPTURA_LOGIN = os.getenv("CAPTURA_LOGIN")
CAPTURA_LIST = os.getenv("CAPTURA_LIST")
FORM_ID = os.getenv("FORM_ID")
VERSION = os.getenv("VERSION")
ROW_ID = os.getenv("ROW_ID")
ROWS = os.getenv("ROWS")
CAPTURA_USER = os.getenv("CAPTURA_USER")
CAPTURA_PASSWORD = os.getenv("CAPTURA_PASSWORD")
load_env_file(os.path.join(os.path.dirname(__file__), 'cipe_data.env'))
CIPE_POST = os.getenv("CIPE_POST")
CIPE_TOKEN = os.getenv("CIPE_TOKEN")
CIPE_USER = os.getenv("CIPE_USER")
CIPE_PASSWORD = os.getenv("CIPE_PASSWORD")


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 4, 27),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

def login():

    url = CAPTURA_LOGIN
    print(CAPTURA_LOGIN)
    credentials = {"user": CAPTURA_USER, "password": CAPTURA_PASSWORD}
    try:
        response = requests.post(url, json=credentials)
        response.raise_for_status()
        success = response.json().get("success")
        if success:
            print("Autenticación exitosa.")
            print(credentials)
            # Convertir el objeto CookieJar a un diccionario de cookies
            cookie_value = response.cookies.get('JSESSIONID')
            print("value cookie", cookie_value)
            #cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
            return cookie_value
        else:
            print("Error de autenticación: El usuario no pudo iniciar sesión.")
            return None
    except requests.exceptions.RequestException as e:
        print("Error al autenticar:", e)
        return None

def obtener_datos(**kwargs):
    cookies = kwargs.get('cookies')
    if cookies:
        url = CAPTURA_LIST
        cookie_str = f"JSESSIONID={cookies};"
        try:
            response = requests.get(url, 
                                    params={"formId": FORM_ID, "version": VERSION, "rowId": ROW_ID, "rows": ROWS}, 
                                    headers={"Cookie": cookie_str})
            response.raise_for_status()
            data = response.json()
            print("Datos de captura obtenidos exitosamente:")
            print(data)

            return json.dumps({"forms": data})
        except requests.exceptions.RequestException as e:
            print("Error al obtener los datos de captura:", e)
            return None
    else:
        print("No se pudieron obtener los datos de captura debido a un error de autenticación o las cookies no son válidas.")
        return None
    
def obtener_token():
    try:
        response = requests.post(CIPE_TOKEN, 
                                 json={"username": CIPE_USER, "password": CIPE_PASSWORD})
        response.raise_for_status()
        token = response.json().get("token")
        print("Token obtenido exitosamente:", token)
        return token
    except requests.exceptions.RequestException as e:
        print("Error al obtener el token:", e)
        return None

def publicar_datos_cipe(**kwargs):
    captura_data_str = kwargs.get('captura_data')
    token = kwargs.get('token')  # Obtener el token del contexto
        # Convertir la cadena JSON en un diccionario
    try:
        captura_data = json.loads(captura_data_str)
        print("Tipo de captura_data:", type(captura_data))
        print("Contenido de captura_data:", captura_data)

    except json.JSONDecodeError as e:
        print("Error al decodificar captura_data:", e)
        return
    if captura_data and token:
        processed_ids = Variable.get("processed_ids", default_var=[], deserialize_json=True)
        new_processed_ids = []
        for form in captura_data["forms"]:
            form_id = form["id"]
            if form_id in processed_ids:
                print(f"Formulario con ID {form_id} ya ha sido procesado.")
                continue
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            dominio = random.choice(['example.com', 'test.com', 'domain.com'])
            email = f"{username}@{dominio}"
            print(email)
            first_name = form["data"]["element15"]
            last_name = form["data"]["element14"]
            ci = form["data"]["element13"]["altitude"]
            
            # Realizar la solicitud POST a CIPE
            
            # Construir el cuerpo de la solicitud
            payload = {
                "first_name": first_name,
                "last_name": last_name,
                "ci": ci,
                "email": email
            }

            # Realizar la solicitud POST a CIPE
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            response = requests.post(CIPE_POST, json=payload, headers=headers)

            # Verificar el estado de la solicitud
            print("code", response.status_code)
            if response.status_code == 200:
                new_processed_ids.append(form_id)
                print("Datos publicados exitosamente en CIPE.")
            else:
                print("No se pudieron publicar datos en CIPE:", response.text)
        # Actualizar la variable con los nuevos IDs procesados
        processed_ids.extend(new_processed_ids)
        Variable.set("processed_ids", processed_ids, serialize_json=True)
    else:
        print("No se pudieron obtener los datos de captura de la tarea anterior o el token de usuario.")

with DAG('obtener_datos_de_captura', default_args=default_args, schedule_interval=None) as dag:

    # Tarea para obtener las cookies de autenticación en Captura
    login_task = PythonOperator(
        task_id='captura_login',
        python_callable=login
    )

    # Tarea para obtener los datos de captura
    obtener_datos_task = PythonOperator(
        task_id='obtener_datos_captura',
        python_callable=obtener_datos,
        op_kwargs={'cookies': "{{ task_instance.xcom_pull(task_ids='captura_login') }}"}
    )

    # Tarea para obtener el token de CIPE
    obtener_token_task = PythonOperator(
        task_id='obtener_token_cipe',
        python_callable=obtener_token
    )
    
    # Tarea para publicar los datos en CIPE
    publicar_datos_cipe_task = PythonOperator(
        task_id='publicar_datos_cipe',
        python_callable=publicar_datos_cipe,
        op_kwargs={'captura_data': "{{ task_instance.xcom_pull(task_ids='obtener_datos_captura') }}",
                   'token': "{{ task_instance.xcom_pull(task_ids='obtener_token_cipe') }}"}
    )

    # Definición del flujo del DAG
    login_task >> obtener_datos_task >> obtener_token_task >> publicar_datos_cipe_task


