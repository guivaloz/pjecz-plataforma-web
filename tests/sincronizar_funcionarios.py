"""
Sinconizar funcionarios con la API de RRHH Personal
"""
from datetime import datetime, date
import logging
import os

from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
import requests
from tabulate import tabulate

from lib.safe_string import safe_clave, safe_email, safe_string

from plataforma_web.app import create_app
from plataforma_web.extensions import db
from plataforma_web.blueprints.centros_trabajos.models import CentroTrabajo
from plataforma_web.blueprints.funcionarios.models import Funcionario

load_dotenv()  # Take environment variables from .env

LLAMADOS_CANTIDAD = 12
CUATRO_SEGUNDOS = 4


class ConfigurationError(Exception):
    """Error de configuración"""


class StatusCodeNot200Error(Exception):
    """Error de status code"""


class ResponseJSONError(Exception):
    """Error de respuesta JSON"""


def get_token(base_url, username, password):
    """Iniciar sesion y obtener token"""
    if base_url is None or username is None or password is None:
        raise ConfigurationError("Falta configurar las variables de entorno")
    response = requests.post(
        url=f"{base_url}/token",
        data={"username": username, "password": password},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "access_token" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el token")
    return respuesta["access_token"]


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_personas(base_url, token, limit, offset):
    """Consultar personas"""
    response = requests.get(
        url=f"{base_url}/v1/personas",
        headers={"authorization": f"Bearer {token}"},
        params={"limit": limit, "offset": offset},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    return respuesta["total"], respuesta["items"]


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_historial_puestos(base_url, token, persona_id):
    """Consultar historial de puestos, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/historial_puestos",
        headers={"authorization": f"Bearer {token}"},
        params={"persona_id": persona_id, "limit": 1, "offset": 0},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    if respuesta["total"] > 0:
        return respuesta["items"][0]  # Entrega el unico elemento del listado
    return None


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_puesto_funcion(base_url, token, puesto_funcion_id):
    """Consultar un puesto funcion"""
    response = requests.get(
        url=f"{base_url}/v1/puestos_funciones/{puesto_funcion_id}",
        headers={"authorization": f"Bearer {token}"},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    return response.json()


@sleep_and_retry
@limits(calls=LLAMADOS_CANTIDAD, period=CUATRO_SEGUNDOS)
def get_personas_fotografias(base_url, token, persona_id):
    """Consultar fotografias de las personas, entrega un elemento (el mas reciente) de encontrarse"""
    response = requests.get(
        url=f"{base_url}/v1/personas_fotografias",
        headers={"authorization": f"Bearer {token}"},
        params={"persona_id": persona_id, "limit": 1, "offset": 0},
    )
    if response.status_code != 200:
        raise StatusCodeNot200Error(f"Error de status code: {response.status_code}")
    respuesta = response.json()
    if "total" not in respuesta or "items" not in respuesta:
        raise ResponseJSONError("Error en la respuesta, falta el total o el items")
    if respuesta["total"] > 0:
        return respuesta["items"][0]  # Entrega el unico elemento del listado
    return None


def main():
    """Procedimiento principal"""
    # Logging
    bitacora = logging.getLogger(__name__)
    bitacora.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
    empunadura = logging.FileHandler("sincronizar_funcionarios.log")
    empunadura.setFormatter(formato)
    bitacora.addHandler(empunadura)
    bitacora.info("Inicia")
    # Iniciar SQLAlchemy
    app = create_app()
    app.app_context().push()
    db.app = app
    # Consultar el centro de trabajo NO DEFINIDO
    centro_trabajo_no_definido = CentroTrabajo.query.filter_by(nombre="NO DEFINIDO").first()
    if centro_trabajo_no_definido is None:
        mensaje_error = "No se encontro el centro de trabajo NO DEFINIDO"
        bitacora.error(mensaje_error)
        print(mensaje_error)
        return
    # Obtener variables de entorno
    base_url = os.getenv("RRHH_PERSONAL_API_URL", None)
    username = os.getenv("RRHH_PERSONAL_API_USERNAME", None)
    password = os.getenv("RRHH_PERSONAL_API_PASSWORD", None)
    # Bloque try/except para manejar errores
    try:
        token = get_token(base_url, username, password)
        limit = 10
        offset = 0
        total = None
        insertados_contador = 0
        actualizados_contador = 0
        while True:
            total, personas = get_personas(base_url, token, limit, offset)
            print(f"Voy en el offset {offset} de {total}...")
            datos = []
            for persona in personas:
                accion = ""
                # Datos de personas
                persona_id = int(persona["id"])
                nombres = safe_string(persona["nombres"])
                apellido_paterno = safe_string(persona["apellido_primero"])
                apellido_materno = safe_string(persona["apellido_segundo"])
                if nombres == "" or apellido_paterno == "":
                    bitacora.warning("Se omite la persona %d porque falta el nombre o el primer apellido", persona_id)
                    continue
                nombre = f"{nombres} {apellido_paterno} {apellido_materno}"
                curp = safe_string(persona["curp"], max_len=18)
                if curp == "":
                    bitacora.warning("Se omite la persona %d porque falta o es incorrecto el CURP", persona_id)
                    continue
                email = safe_email(persona["email"])
                if email == "":
                    bitacora.warning("Se omite la persona %d porque falta el email", persona_id)
                    continue
                if not email.endswith("@coahuila.gob.mx"):
                    bitacora.warning("Se omite la persona %d porque el email %s no es de coahuila", persona_id, email)
                    continue
                if persona["fecha_ingreso_pj"] is not None:
                    ingreso_fecha = datetime.strptime(persona["fecha_ingreso_pj"], "%Y-%m-%d").date()
                else:
                    bitacora.warning("A la persona %d se le define una fecha de ingreso por defecto", persona_id)
                    ingreso_fecha = date(1900, 1, 1)
                # Datos de historial de puestos
                puesto = ""
                puesto_clave = ""
                centro_trabajo_clave = ""
                historial_puesto = get_historial_puestos(base_url, token, persona_id)
                if historial_puesto is None:
                    bitacora.warning("Se omite la persona %d porque no tiene historial de puestos", persona_id)
                    continue
                en_funciones = False
                if historial_puesto["fecha_termino"] is None:  # La fecha de termino vacia significa que esta en funciones
                    en_funciones = True
                    puesto = safe_string(historial_puesto["puesto_funcion_nombre"])
                    centro_trabajo_clave = safe_clave(historial_puesto["centro_trabajo"])
                    # Datos del puesto
                    puesto_funcion = get_puesto_funcion(base_url, token, historial_puesto["puesto_funcion_id"])
                    puesto_clave = safe_clave(puesto_funcion["puesto_clave"])
                # Datos de fotografias
                fotografia_url = ""
                fotografia = get_personas_fotografias(base_url, token, persona_id)
                if fotografia and (fotografia["url"] is not None or fotografia["url"] != ""):
                    fotografia_url = fotografia["url"]
                # Decidir entre insertar o actualizar
                accion = ""
                funcionario = Funcionario.query.filter_by(curp=curp).first()
                if funcionario is None:
                    funcionario_con_mismo_email = Funcionario.query.filter_by(email=email).first()
                    if funcionario_con_mismo_email is not None:
                        bitacora.warning("Se omite insertar la persona %d porque el email %s ya esta registrado", persona_id, email)
                        continue
                    accion = "Insertado"
                    centro_trabajo = CentroTrabajo.query.filter_by(clave=centro_trabajo_clave).first()
                    if centro_trabajo is None:
                        centro_trabajo = centro_trabajo_no_definido
                    Funcionario(
                        centro_trabajo=centro_trabajo,
                        nombres=nombres,
                        apellido_paterno=apellido_paterno,
                        apellido_materno=apellido_materno,
                        curp=curp,
                        email=email,
                        puesto=puesto,
                        puesto_clave=puesto_clave,
                        ingreso_fecha=ingreso_fecha,
                        fotografia_url=fotografia_url,
                        en_funciones=en_funciones,
                    ).save()
                    insertados_contador += 1
                else:
                    ha_cambiado = False
                    if email != funcionario.email:
                        funcionario_con_mismo_email = Funcionario.query.filter_by(email=email).first()
                        if funcionario_con_mismo_email is not None:
                            bitacora.warning("Se omite actualizar la persona %d porque el email %s ya esta registrado", persona_id, email)
                            continue
                        ha_cambiado = True
                        funcionario.email = email
                    if nombres != funcionario.nombres:
                        ha_cambiado = True
                        funcionario.nombres = nombres
                    if apellido_paterno != funcionario.apellido_paterno:
                        ha_cambiado = True
                        funcionario.apellido_paterno = apellido_paterno
                    if apellido_materno != funcionario.apellido_materno:
                        ha_cambiado = True
                        funcionario.apellido_materno = apellido_materno
                    if puesto != funcionario.puesto:
                        ha_cambiado = True
                        funcionario.puesto = puesto
                    if puesto_clave != funcionario.puesto_clave:
                        ha_cambiado = True
                        funcionario.puesto_clave = puesto_clave
                    if ingreso_fecha != funcionario.ingreso_fecha:
                        ha_cambiado = True
                        funcionario.ingreso_fecha = ingreso_fecha
                    if fotografia_url != funcionario.fotografia_url:
                        ha_cambiado = True
                        funcionario.fotografia_url = fotografia_url
                    if en_funciones != funcionario.en_funciones:
                        ha_cambiado = True
                        funcionario.en_funciones = en_funciones
                    if ha_cambiado:
                        accion = "Actualizado"
                        funcionario.save()
                        actualizados_contador += 1
                # Acumular datos para tabulate
                datos.append([nombre[:24], curp, email[:16], ingreso_fecha, centro_trabajo_clave, puesto_clave, puesto[:24], fotografia_url[-24:], en_funciones, accion])
            print(tabulate(datos, headers=["Nombre", "CURP", "Email", "Ingreso", "C. de T.", "C. del Puesto", "Puesto", "Fotografia URL", "EF", "Accion"]))
            print()
            offset += limit
            if offset >= total:
                break
        mensaje_final = f"Se insertaron {insertados_contador} y se actualizaron {actualizados_contador} funcionarios"
        bitacora.info("Termina. %s", mensaje_final)
        print(mensaje_final)
    except requests.ConnectionError as error:
        print(f"Error de conexion: {error}")
    except requests.Timeout as error:
        print(f"Error de falta de respuesta a tiempo: {error}")
    except (ConfigurationError, ResponseJSONError, StatusCodeNot200Error) as error:
        print(error)
    return


if __name__ == "__main__":
    main()