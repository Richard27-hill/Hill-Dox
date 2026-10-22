#!/usr/bin/python

import json
import requests
import time
import os
import sys
import concurrent.futures
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from urllib.parse import quote_plus
import re
from bs4 import BeautifulSoup

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

Bl = '\033[30m'
Re = '\033[1;31m'
Gr = '\033[1;32m'
Ye = '\033[1;33m'
Blu = '\033[1;34m'
Mage = '\033[1;35m'
Cy = '\033[1;36m'
Wh = '\033[1;37m'

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 10

SESION = requests.Session()
SESION.headers.update(HEADERS)


def is_option(func):
    def wrapper(*args, **kwargs):
        run_banner()
        return func(*args, **kwargs)
    return wrapper


@is_option
def rastrear_ip():
    ip = input(f"{Wh}\n Ingresa la IP objetivo : {Gr}").strip()
    
    if not ip:
        print(f"{Re}\n [-] No ingresaste ninguna IP. Inténtalo de nuevo.")
        return

    print()
    print(f' {Wh}============= {Gr}INFORMACIÓN DE LA DIRECCIÓN IP | Richard-Hill {Wh}=============')

    try:
        req_api = SESION.get(f"http://ipwho.is/{ip}", timeout=TIMEOUT)
        ip_data = req_api.json()
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"{Re}\n No se pudo conectar con el servicio de geolocalización: {e}")
        return

    if not ip_data.get('success', True):
        print(f"{Re}\n No se pudo geolocalizar la IP: {ip_data.get('message', 'IP inválida')}")
        return

    time.sleep(1)
    latitud = ip_data.get('latitude')
    longitud = ip_data.get('longitude')
    conexion = ip_data.get('connection') or {}
    zona_horaria = ip_data.get('timezone') or {}
    bandera = ip_data.get('flag') or {}
    emoji_bandera = bandera.get('emoji', 'N/D')
    unicode_bandera = bandera.get('emoji_unicode', 'N/D')

    print(f"{Wh}\n IP objetivo          :{Gr}", ip)
    print(f"{Wh} Tipo de IP           :{Gr}", ip_data.get('type', 'N/D'))
    print(f"{Wh} País                 :{Gr}", ip_data.get('country', 'N/D'))
    print(f"{Wh} Código de país       :{Gr}", ip_data.get('country_code', 'N/D'))
    print(f"{Wh} Ciudad               :{Gr}", ip_data.get('city', 'N/D'))
    print(f"{Wh} Continente           :{Gr}", ip_data.get('continent', 'N/D'))
    print(f"{Wh} Código de continente :{Gr}", ip_data.get('continent_code', 'N/D'))
    print(f"{Wh} Región               :{Gr}", ip_data.get('region', 'N/D'))
    print(f"{Wh} Código de región     :{Gr}", ip_data.get('region_code', 'N/D'))
    print(f"{Wh} Latitud              :{Gr}", latitud)
    print(f"{Wh} Longitud             :{Gr}", longitud)
    if latitud is not None and longitud is not None:
        print(f"{Wh} Mapa                 :{Gr}", f"https://www.google.com/maps/@{latitud},{longitud},8z")
    print(f"{Wh} Unión Europea        :{Gr}", ip_data.get('is_eu', 'N/D'))
    print(f"{Wh} Código postal        :{Gr}", ip_data.get('postal', 'N/D'))
    print(f"{Wh} Código de llamada    :{Gr}", ip_data.get('calling_code', 'N/D'))
    print(f"{Wh} Capital              :{Gr}", ip_data.get('capital', 'N/D'))
    print(f"{Wh} Fronteras            :{Gr}", ip_data.get('borders', 'N/D'))
    try:
        print(f"{Wh} Bandera del país     :{Gr}", emoji_bandera, f"({unicode_bandera})")
    except UnicodeEncodeError:
        print(f"{Wh} Bandera del país     :{Gr}", f"{ip_data.get('country_code', 'N/D')} ({unicode_bandera})")
    print(f"{Wh} ASN                  :{Gr}", conexion.get('asn', 'N/D'))
    print(f"{Wh} Organización         :{Gr}", conexion.get('org', 'N/D'))
    print(f"{Wh} ISP                  :{Gr}", conexion.get('isp', 'N/D'))
    print(f"{Wh} Dominio              :{Gr}", conexion.get('domain', 'N/D'))
    print(f"{Wh} ID de zona horaria   :{Gr}", zona_horaria.get('id', 'N/D'))
    print(f"{Wh} Abreviatura          :{Gr}", zona_horaria.get('abbr', 'N/D'))
    print(f"{Wh} Horario de verano    :{Gr}", zona_horaria.get('is_dst', 'N/D'))
    print(f"{Wh} Desfase horario      :{Gr}", zona_horaria.get('offset', 'N/D'))
    print(f"{Wh} UTC                  :{Gr}", zona_horaria.get('utc', 'N/D'))
    print(f"{Wh} Hora actual          :{Gr}", zona_horaria.get('current_time', 'N/D'))


@is_option
def rastrear_telefono():
    numero_usuario = input(
        f"\n {Wh}Ingresa el número de teléfono objetivo {Gr}Ej [+521234567890] {Wh}: {Gr}")
    region_por_defecto = "MX"

    try:
        numero_analizado = phonenumbers.parse(numero_usuario, region_por_defecto)
    except phonenumbers.NumberParseException as e:
        print(f"{Re}\n No se pudo interpretar el número: {e}")
        return

    if not phonenumbers.is_possible_number(numero_analizado):
        print(f"{Re}\n El número ingresado no parece ser válido.")
        return

    codigo_region = phonenumbers.region_code_for_number(numero_analizado)
    operador = carrier.name_for_number(numero_analizado, "es") or "Desconocido"
    ubicacion = geocoder.description_for_number(numero_analizado, "es") or "Desconocida"
    es_valido = phonenumbers.is_valid_number(numero_analizado)
    es_posible = phonenumbers.is_possible_number(numero_analizado)
    numero_formateado = phonenumbers.format_number(numero_analizado, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    numero_formateado_movil = phonenumbers.format_number_for_mobile_dialing(
        numero_analizado, region_por_defecto, with_formatting=True)
    tipo_numero = phonenumbers.number_type(numero_analizado)
    zonas_horarias = timezone.time_zones_for_number(numero_analizado)
    zonas_horarias_texto = ', '.join(zonas_horarias) if zonas_horarias else 'N/D'

    print(f"\n {Wh}========== {Gr}INFORMACIÓN DEL NÚMERO DE TELÉFONO | Richard-Hill {Wh}==========")
    print(f"\n {Wh}Ubicación               :{Gr} {ubicacion}")
    print(f" {Wh}Código de región        :{Gr} {codigo_region}")
    print(f" {Wh}Zona horaria            :{Gr} {zonas_horarias_texto}")
    print(f" {Wh}Operador                :{Gr} {operador}")
    print(f" {Wh}Número válido           :{Gr} {es_valido}")
    print(f" {Wh}Número posible          :{Gr} {es_posible}")
    print(f" {Wh}Formato internacional   :{Gr} {numero_formateado}")
    print(f" {Wh}Formato móvil           :{Gr} {numero_formateado_movil}")
    print(f" {Wh}Número original         :{Gr} {numero_analizado.national_number}")
    print(f" {Wh}Formato E.164           :{Gr} "
          f"{phonenumbers.format_number(numero_analizado, phonenumbers.PhoneNumberFormat.E164)}")
    print(f" {Wh}Código de país          :{Gr} {numero_analizado.country_code}")
    print(f" {Wh}Número local            :{Gr} {numero_analizado.national_number}")
    if tipo_numero == phonenumbers.PhoneNumberType.MOBILE:
        print(f" {Wh}Tipo                    :{Gr} Es un número móvil")
    elif tipo_numero == phonenumbers.PhoneNumberType.FIXED_LINE:
        print(f" {Wh}Tipo                    :{Gr} Es un número fijo")
    else:
        print(f" {Wh}Tipo                    :{Gr} Es otro tipo de número")


def _verificar_sitio(sitio, usuario):
    url = sitio['url'].format(usuario)
    try:
        respuesta = SESION.get(url, timeout=6, allow_redirects=True)
        if respuesta.status_code == 200:
            return sitio['name'], url, True
        return sitio['name'], None, False
    except requests.RequestException:
        return sitio['name'], None, None


@is_option
def rastrear_usuario():
    usuario = input(f"\n {Wh}Ingresa el nombre de usuario : {Gr}")
    redes_sociales = [
        {"url": "https://www.facebook.com/{}", "name": "Facebook"},
        {"url": "https://twitter.com/{}", "name": "Twitter"},
        {"url": "https://www.instagram.com/{}", "name": "Instagram"},
        {"url": "https://www.linkedin.com/in/{}", "name": "LinkedIn"},
        {"url": "https://www.github.com/{}", "name": "GitHub"},
        {"url": "https://www.pinterest.com/{}", "name": "Pinterest"},
        {"url": "https://www.tumblr.com/{}", "name": "Tumblr"},
        {"url": "https://www.youtube.com/{}", "name": "YouTube"},
        {"url": "https://soundcloud.com/{}", "name": "SoundCloud"},
        {"url": "https://www.snapchat.com/add/{}", "name": "Snapchat"},
        {"url": "https://www.tiktok.com/@{}", "name": "TikTok"},
        {"url": "https://www.behance.net/{}", "name": "Behance"},
        {"url": "https://medium.com/@{}", "name": "Medium"},
        {"url": "https://www.quora.com/profile/{}", "name": "Quora"},
        {"url": "https://www.flickr.com/people/{}", "name": "Flickr"},
        {"url": "https://www.twitch.tv/{}", "name": "Twitch"},
        {"url": "https://dribbble.com/{}", "name": "Dribbble"},
        {"url": "https://www.ello.co/{}", "name": "Ello"},
        {"url": "https://www.producthunt.com/@{}", "name": "Product Hunt"},
        {"url": "https://t.me/{}", "name": "Telegram"},
        {"url": "https://www.reddit.com/user/{}", "name": "Reddit"},
        {"url": "https://steamcommunity.com/id/{}", "name": "Steam"},
        {"url": "https://vimeo.com/{}", "name": "Vimeo"},
        {"url": "https://about.me/{}", "name": "About.me"},
    ]

    print(f"\n {Wh}========== {Gr}INFORMACIÓN DEL NOMBRE DE USUARIO | Richard-Hill {Wh}==========\n")
    print(f" {Wh}Buscando en {len(redes_sociales)} plataformas (en paralelo), esto tarda unos segundos...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ejecutor:
        futuros = [ejecutor.submit(_verificar_sitio, sitio, usuario) for sitio in redes_sociales]
        for futuro in concurrent.futures.as_completed(futuros):
            nombre, url, encontrado = futuro.result()
            if encontrado is True:
                print(f" {Wh}[ {Gr}+ {Wh}] {nombre:<15}: {Gr}{url}")
            elif encontrado is False:
                print(f" {Wh}[ {Ye}- {Wh}] {nombre:<15}: {Ye}no encontrado")
            else:
                print(f" {Wh}[ {Re}! {Wh}] {nombre:<15}: {Re}no se pudo verificar")

    print(f"\n {Wh}Nota: un resultado \"encontrado\" solo indica que la página respondió; "
          f"algunas redes muestran una página genérica aunque el usuario no exista.")


@is_option
def buscar_nombre_apellido():
    nombre = input(f"\n {Wh}Nombre   : {Gr}")
    apellido = input(f" {Wh}Apellido : {Gr}")
    ubicacion = input(f" {Wh}Ciudad o país (opcional, Enter para omitir) : {Gr}")

    nombre_completo = f"{nombre} {apellido}".strip()
    if not nombre_completo:
        print(f"{Re}\n Debes ingresar al menos un nombre.")
        return

    consulta_texto = f'"{nombre_completo}" {ubicacion}'.strip()
    consulta = quote_plus(consulta_texto)
    consulta_simple = quote_plus(f"{nombre_completo} {ubicacion}".strip())

    buscadores = [
        ("Google", f"https://www.google.com/search?q={consulta}"),
        ("Bing", f"https://www.bing.com/search?q={consulta}"),
        ("DuckDuckGo", f"https://duckduckgo.com/?q={consulta}"),
    ]

    redes_por_nombre = [
        ("LinkedIn (búsqueda directa)", f"https://www.linkedin.com/search/results/people/?keywords={consulta_simple}"),
        ("LinkedIn (vía Google)", f"https://www.google.com/search?q=site:linkedin.com/in+{consulta}"),
        ("Facebook (búsqueda directa)", f"https://www.facebook.com/search/people/?q={consulta_simple}"),
        ("Instagram (vía Google)", f"https://www.google.com/search?q=site:instagram.com+{consulta}"),
        ("Twitter/X (vía Google)", f"https://www.google.com/search?q=site:twitter.com+{consulta}"),
        ("TikTok (vía Google)", f"https://www.google.com/search?q=site:tiktok.com+{consulta}"),
        ("Documentos públicos (PDF)", f"https://www.google.com/search?q={consulta}+filetype:pdf"),
    ]

    print(f"\n {Wh}========== {Gr}BÚSQUEDA OSINT POR NOMBRE Y APELLIDO | Richard-Hill {Wh}==========")
    print(f"\n {Wh}Nombre completo : {Gr}{nombre_completo}")
    if ubicacion:
        print(f" {Wh}Ubicación       : {Gr}{ubicacion}")

    print(f"\n {Wh}--- Buscadores generales ---")
    for nombre_sitio, url in buscadores:
        print(f" {Wh}[ {Gr}+ {Wh}] {nombre_sitio:<28}: {Gr}{url}")

    print(f"\n {Wh}--- Redes sociales y registros públicos ---")
    for nombre_sitio, url in redes_por_nombre:
        print(f" {Wh}[ {Gr}+ {Wh}] {nombre_sitio:<28}: {Gr}{url}")


@is_option
def mostrar_mi_ip():
    try:
        respuesta = SESION.get('https://api.ipify.org/', timeout=TIMEOUT)
        mi_ip = respuesta.text
    except requests.RequestException as e:
        print(f"{Re}\n No se pudo obtener tu IP: {e}")
        return

    print(f"\n {Wh}========== {Gr}INFORMACIÓN DE TU IP | Richard-Hill {Wh}==========")
    print(f"\n {Wh}[{Gr} + {Wh}] Tu dirección IP : {Gr}{mi_ip}")
    print(f"\n {Wh}==============================================")


@is_option
def buscar_por_cedula_ve():
    print(f" {Ye}[i] Aviso: Este sistema muestra únicamente resultados de personas mayores de edad.{Wh}")
    cedula_a_consultar = input(f"\n {Wh}Ingresa el número de cédula (VENEZUELA) : {Gr}").strip()

    if not cedula_a_consultar:
        print(f"{Re}\n [-] Debes ingresar un número de cédula válido.")
        return

    sesion_local = requests.Session()
    headers_local = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Referer": "https://www.sistemaspnp.com/cedula/",
        "Origin": "https://www.sistemaspnp.com",
    }
    
    try:
        print(f"\n {Wh}[{Gr}*{Wh}] {Ye}Obteniendo CAPTCHA del servidor...{Wh}")
        url_form = "https://www.sistemaspnp.com/cedula/"
        response_form = sesion_local.get(url_form, headers=headers_local, timeout=15)

        soup = BeautifulSoup(response_form.text, "html.parser")
        captcha_label = soup.find(string=re.compile(r"¿Cuánto es", re.IGNORECASE))
        
        captcha_respuesta = 8
        if captcha_label:
            numeros = re.findall(r"\d+", captcha_label)
            if len(numeros) >= 2:
                captcha_respuesta = int(numeros[0]) + int(numeros[1])

        print(f" {Wh}[{Gr}+{Wh}] {Gr}CAPTCHA resuelto automáticamente: {captcha_respuesta}{Wh}")

        url_resultado = "https://www.sistemaspnp.com/cedula/resultado.php"
        payload = {"cedula": cedula_a_consultar, "captcha": str(captcha_respuesta), "jeje": ""}

        print(f" {Wh}[{Gr}*{Wh}] {Ye}Enviando datos...{Wh}")
        response_post = sesion_local.post(url_resultado, data=payload, headers=headers_local, allow_redirects=True, timeout=15)

        if response_post.status_code == 200:
            soup_res = BeautifulSoup(response_post.text, "html.parser")
            texto_completo = soup_res.get_text(separator="\n", strip=True)

            def extraer_campo(etiqueta, lineas):
                for i, l in enumerate(lineas):
                    if etiqueta in l and i + 1 < len(lineas):
                        return lineas[i + 1]
                return "N/D"

            lineas = [l.strip() for l in texto_completo.split("\n") if l.strip()]

            cedula_val = extraer_campo("Cédula:", lineas)
            rif_val = extraer_campo("RIF:", lineas)
            primer_apellido = extraer_campo("Primer Apellido:", lineas)
            segundo_apellido = extraer_campo("Segundo Apellido:", lineas)
            nombres = extraer_campo("Nombres:", lineas)
            estado = extraer_campo("Estado:", lineas)
            municipio = extraer_campo("Municipio:", lineas)
            centro = extraer_campo("Centro Electoral:", lineas)

            if "Cédula:" not in texto_completo:
                print(f"\n {Re}[-] No se encontraron datos para esta cédula o el servicio falló.{Wh}")
            else:
                print(f"\n {Wh}" + "=" * 65)
                print(f" {Ye}🇻🇪  REPUBLICA BOLIVARIANA DE VENEZUELA - CEDULA DE IDENTIDAD | Richard-Hill 🇻🇪 {Wh}")
                print(f" {Wh}" + "=" * 65)
                print(f"  {Wh}Nro. CÉDULA   : {Gr}{cedula_val:<20} {Wh}| {Wh}RIF: {Gr}{rif_val}")
                print(f" {Wh}" + "-" * 65)
                print(f"  {Wh}APELLIDOS     : {Gr}{primer_apellido} {segundo_apellido}")
                print(f"  {Wh}NOMBRES       : {Gr}{nombres}")
                print(f" {Wh}" + "-" * 65)
                print(f"  {Wh}INFORMACIÓN ELECTORAL (CNE):")
                print(f"  {Wh}Estado        : {Gr}{estado}")
                print(f"  {Wh}Municipio     : {Gr}{municipio}")
                print(f"  {Wh}Centro        : {Gr}{centro}")
                print(f" {Wh}" + "=" * 65 + "\n")
        else:
            print(f"{Re}\n [-] Error en la petición: HTTP {response_post.status_code}")
            
    except requests.RequestException as e:
        print(f"{Re}\n [-] Error de conexión: {e}")
    except Exception as e:
        print(f"{Re}\n [-] Ocurrió un error inesperado al procesar los datos: {e}")


@is_option
def buscar_por_nombre_ve():
    print(f" {Ye}[i] Aviso: Este sistema muestra únicamente resultados de personas mayores de edad.{Wh}")
    nombre_a_buscar = input(f"\n {Wh}Ingresa el nombre completo a buscar (VENEZUELA) : {Gr}").strip()

    if not nombre_a_buscar:
        print(f"{Re}\n [-] Debes ingresar un término de búsqueda válido.")
        return

    sesion_local = requests.Session()
    headers_local = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) Gecko/20100101 Firefox/154.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://armandodata.com/Personas/Search",
    }

    query_format = nombre_a_buscar.replace(" ", "+")
    url_busqueda = f"https://armandodata.com/Personas/Search?exact=false&nombre={query_format}"

    try:
        print(f"\n {Wh}[{Gr}*{Wh}] {Ye}Consultando al servidor, por favor espera...{Wh}")
        response = sesion_local.get(url_busqueda, headers=headers_local, timeout=15)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            print(f"\n {Wh}┌" + "─" * 63 + "┐")
            print(f" {Wh}│ {Ye}🔍 RESULTADOS: {Gr}{nombre_a_buscar.upper():<43} {Wh}│")
            print(f" {Wh}└" + "─" * 63 + "┘\n")

            tablas = soup.find_all("table")
            registros = []
            
            if tablas:
                for tabla in tablas:
                    filas = tabla.find_all("tr")
                    for fila in filas:
                        celdas = fila.find_all(["th", "td"])
                        datos_limpios = [c.get_text(strip=True) for c in celdas if c.get_text(strip=True)]
                        if datos_limpios:
                            registros.append(datos_limpios)

            if not registros:
                resultados_texto = soup.get_text(separator="\n", strip=True)
                lineas = [l for l in resultados_texto.split("\n") if l.strip()]

                menu_basura = [
                    "armando", "data", "empresas", "personas", "sentencias", "gacetas",
                    "inicia sesión", "registrarse", "más", "obras de empresas",
                    "servicios de empresas", "r.n.c.", "sunbiz", "jueces", "importaciones",
                    "empresas turquia", "magistrados 2022", "aeronaves", "buscar",
                    "iniciar sesión", "regístrate", "buscar personas"
                ]

                resultados_utiles = [l for l in lineas if l.lower() not in menu_basura]
                
                persona_actual = []
                for linea in resultados_utiles:
                    if re.match(r"^(V-|E-)?\d{5,9}$", linea, re.IGNORECASE):
                        if persona_actual:
                            registros.append(persona_actual)
                        persona_actual = [linea]
                    else:
                        persona_actual.append(linea)
                if persona_actual:
                    registros.append(persona_actual)

            if not registros:
                print(f"  {Re}[-] No se encontraron coincidencias para la búsqueda.{Wh}\n")
            else:
                for idx, reg in enumerate(registros, 1):
                    print(f" {Wh}╭─[{Gr} Registro #{idx} {Wh}]" + "─" * 47)
                    for item in reg:
                        print(f" {Wh}│  {Cy}• {Wh}{item}")
                    print(f" {Wh}╰" + "─" * 59 + "\n")
        else:
            print(f"{Re}\n [-] Error en la petición: HTTP {response.status_code}")
            
    except requests.RequestException as e:
        print(f"{Re}\n [-] Error de conexión: {e}")
    except Exception as e:
        print(f"{Re}\n [-] Ocurrió un error inesperado: {e}")


options = [
    {'num': 1, 'text': 'Rastreador de IP', 'func': rastrear_ip},
    {'num': 2, 'text': 'Mostrar mi IP', 'func': mostrar_mi_ip},
    {'num': 3, 'text': 'Rastreador de número telefónico', 'func': rastrear_telefono},
    {'num': 4, 'text': 'Rastreador de nombre de usuario', 'func': rastrear_usuario},
    {'num': 5, 'text': 'Búsqueda OSINT por nombre y apellido general', 'func': buscar_nombre_apellido},
    {'num': 6, 'text': 'Buscar persona por cédula (Venezuela)', 'func': buscar_por_cedula_ve},
    {'num': 7, 'text': 'Buscar cédula por nombre de persona (Venezuela)', 'func': buscar_por_nombre_ve},
    {'num': 0, 'text': 'Salir', 'func': lambda: sys.exit()}
]


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def is_in_options(num):
    for opcion in options:
        if opcion['num'] == num:
            return True
    return False


def call_option(opt):
    if not is_in_options(opt):
        raise ValueError(f'{Re}\n [ ! ] Opción no encontrada')
    for opcion in options:
        if opcion['num'] == opt:
            if 'func' in opcion:
                opcion['func']()
            else:
                print('No se detectó ninguna función')


def execute_option(opt):
    try:
        call_option(opt)
        input(f'\n{Wh}[ {Gr}+ {Wh}] {Gr}Presiona Enter para continuar')
        main()
    except ValueError as e:
        print(e)
        time.sleep(2)
        main()
    except KeyboardInterrupt:
        print(f'\n{Wh}[ {Re}! {Wh}] {Re}Saliendo')
        time.sleep(2)
        sys.exit()


def option_text():
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80

    box_w = min(max(term_width - 6, 60), 92)
    inner_w = box_w - 4

    top_border = f"{Wh}┌" + "─" * (box_w - 2) + "┐"
    bottom_border = f"{Wh}└" + "─" * (box_w - 2) + "┘"
    sep_line = f"{Wh}├" + "─" * (box_w - 2) + "┤"

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def strip_ansi(text):
        return ansi_escape.sub('', text)

    def row(content_colored):
        vis_len = len(strip_ansi(content_colored))
        padding = max(0, inner_w - vis_len)
        return f"{Wh}│ {content_colored}" + " " * padding + f" {Wh}│"

    lines = []
    lines.append(top_border)
    
    title_str = "MENÚ PRINCIPAL DE HERRAMIENTAS"
    padded_title = f"{title_str:^{inner_w}}"
    lines.append(row(f"{Ye}{padded_title}{Wh}"))
    
    lines.append(sep_line)

    # Categoría 1: Redes e IP
    lines.append(row(f"{Blu}[ R E D  E  I P ]{Wh}"))
    lines.append(row(f"  {Gr}[ 1 ]{Wh}  Rastreador y Geolocalización de IP"))
    lines.append(row(f"  {Gr}[ 2 ]{Wh}  Ver la información de tu propia IP"))
    
    # Categoría 2: Global
    lines.append(row(f"{Blu}[ GLOBAL ]{Wh}"))
    lines.append(row(f"  {Gr}[ 3 ]{Wh}  Rastrear número telefónico (Carrier y Ubicación)"))
    lines.append(row(f"  {Gr}[ 4 ]{Wh}  Rastrear nombre de usuario en redes sociales"))
    lines.append(row(f"  {Gr}[ 5 ]{Wh}  Buscar persona por Nombre y Apellido (General)"))

    # Categoría 3: Venezuela
    lines.append(row(f"{Blu}[ VENEZUELA ]{Wh}"))
    lines.append(row(f"  {Gr}[ 6 ]{Wh}  Buscar persona por cédula"))
    lines.append(row(f"  {Gr}[ 7 ]{Wh}  Buscar información/cedula por Nombre "))

    # Salir
    lines.append(sep_line)
    lines.append(row(f"  {Re}[ 0 ]{Wh}  Salir del sistema"))
    lines.append(bottom_border)

    return "\n".join(lines)


def option():
    clear()
    sys.stderr.writelines(f"""



⠀⠀⢀⣠⣴⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣶⣤⣀⠀⠀
⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀
⠀⢸⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀
⠀⣿⡿⣿⡟⠛⠛⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠛⠛⢻⣿⣿⠀
⠀⣿⡿⠋⠉⠑⠒⠤⣉⠻⢿⣿⣿⡿⠋⠀⠀⠀⠁⠐⠳⢹⡇
⠀⣿⣷⣶⣦⣄⡀⠀⠀⠉⠺⡿⠿⠃⠀⠀⠀⣠⣴⣶⣶⣾⡇
⠀⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⣴⣇⠀⠀⣰⡿⠿⠿⢿⣿⢛⡇
⠀⣡⡌⠁⠀⠀⠀⠈⠉⠀⠈⣿⣷⠀⠀⠁⠀⠀⠀⠀⣠⣌⣿
⠀⢿⣿⣿⣶⣦⣴⣶⣾⣰⠄⣿⣿⠠⣸⣶⣶⣶⣶⣿⣿⣿⡇
⠀⠈⢿⣿⣿⣿⣿⣿⣿⣿⠃⣿⣿⠐⣿⢿⣿⣿⣟⣋⣠⡔⠀
⠀⠸⡀⠉⠉⣉⣍⣭⠹⢿⠁⣿⣿⡇⠿⠆⣭⣉⡉⠉⡁⢰⠀
⠀⠀⢷⡀⢀⠈⠻⠿⠶⠄⠀⠈⠉⠀⠠⠾⠿⠟⠁⠐⢠⠇⠀
⠀⠀⠈⢷⡀⠐⢤⣤⣀⡀⠀⠴⠷⠄⠀⣠⣤⡤⠌⠠⠋⠀⠀
⠀⠀⠀⠀⠱⣷⡄⢦⣍⣙⠛⠒⠒⠒⣉⣩⣤⠆⢔⠃⠀⠀⠀
⠀⠀⠀⠀⡀⠈⠛⣆⢻⣿⡇⠀⡄⠸⣿⿿⠣⡎⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣇⠀⠀⠈⠻⣿⣇⠀⠀⢸⣿⡤⠋⠀⢀⡆⠀⠀⠀
⠀⠀⠀⢘⣿⣦⣀⠀⠀⠈⠙⠀⠀⠟⠉⠀⠀⣠⣾⡿⠀⠀⠀ _   _ _ _ _       ____
⠀⠀⠀⠀⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⣀⣴⣿⣿⣿⡏⠀⠀⠀| | | (_) | |     |  _ \\  _____  __
⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⠗⠀⠀⠺⣿⣿⣿⣿⣿⠃⠀  | |_| | | | |_____| | | |/ _ \\ \\/ /
⠀⠀⠀⠀⠈⣿⣿⣿⡟⠁⠀⠀⠀⠀⠈⢿⣿⣿⡿⠀⠀⠀ |  _  | | | |_____| |_| | (_) >  <
⠀⠀⠀⠀⠀⠈⣿⠟⢠⣦⠀⠀⠀⠀⣴⡄⠻⣿⠃⠀⠀⠀⠀|_| |_|_|_|_|     |____/ \\___/_/\\_\\
⠀⠀⠀⠀⠀⢡⡌⣰⣿⣿⡇⠀⠀⢸⣿⣧⣆⢁⠆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣿⣿⣿⡟⠀⠀⠀⠀⢻⣿⣿⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢻⣿⣿⠁⠀⠀⠀⠀⠈⣿⣿⡏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⣿⣟⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⹹⠇⠀⠀⠀⠀⠀⠀
              {Wh}[ + ]  C O D E   B Y  Richard-Hill  [ + ]
    """)
    sys.stderr.writelines(f"\n\n\n{option_text()}")


def run_banner():
    clear()
    time.sleep(0.5)
    sys.stderr.writelines(f"""{Wh}

+------------------------------------------------------------------------------------------------------------------------------+
                                     Herramienta de rastreo 
+------------------------------------------------------------------------------------------------------------------------------+

   {Wh}-----------------------------------------|
   {Wh}| {Gr}- Hablale {Wh}                     |
   {Wh}| {Gr}@CODE BY Richard-Hill      {Wh}    |
   {Wh}-----------------------------------------|

        """)
    time.sleep(0.5)


def main():
    clear()
    option()
    time.sleep(1)
    try:
        opt = int(input(f"{Wh}\n [ + ] {Gr}Selecciona una opción : {Wh}"))
        execute_option(opt)
    except ValueError:
        print(f'\n{Wh}[ {Re}! {Wh}] {Re}Por favor ingresa un número')
        time.sleep(2)
        main()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n{Wh}[ {Re}! {Wh}] {Re}Saliendo')
        time.sleep(2)
        sys.exit()