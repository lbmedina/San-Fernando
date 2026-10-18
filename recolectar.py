#!/usr/bin/env python3
"""Consulta fuentes oficiales y escribe docs/datos.json (solo biblioteca estándar)."""
import csv, io, json, re, sys, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

AR = timezone(timedelta(hours=-3))
SHN_CSV = "https://www.hidro.gov.ar/oceanografia/AlturasHorarias.asp?export=csv"
SHN_RSS = "https://www.hidro.gov.ar/rss/rss.asp"
INA_RSS = "https://www.ina.gov.ar/alerta/rss/index.php"
ESTACIONES = ["San Fernando", "Buenos Aires", "La Plata", "Martín García"]
UA = {"User-Agent": "alerta-crecidas-personal/1.0 (uso personal, consulta cada 30 min)"}


def bajar(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        cs = r.headers.get_content_charset() or "windows-1252"
    return raw.decode(cs, errors="replace")


def num(s):
    try:
        return float(s.replace(",", "."))
    except (ValueError, AttributeError):
        return None


def parse_shn_csv(texto, ahora=None, horas=48):
    """Devuelve {estacion: {actual, fecha, serie:[[fecha,altura],...]}} (serie cronológica)."""
    ahora = ahora or datetime.now(AR)
    filas = list(csv.reader(io.StringIO(texto), delimiter=";"))
    if not filas or "Fecha" not in filas[0][0]:
        raise ValueError("Formato inesperado: falta la cabecera 'Fecha y hora'")
    cab = [c.strip() for c in filas[0]]
    salida = {}
    for est in ESTACIONES:
        if est not in cab:
            continue
        i = cab.index(est)
        serie = []
        for f in filas[1:]:
            if len(f) <= i:
                continue
            try:
                dt = datetime.strptime(f[0].strip(), "%d/%m/%Y %H:%M").replace(tzinfo=AR)
            except ValueError:
                continue
            v = num(f[i].strip())
            if v is None:
                continue
            serie.append((dt, v))
        serie.sort()
        serie = [s for s in serie if s[0] >= ahora - timedelta(hours=horas)] or serie[-horas:]
        if not serie:
            continue
        ult = serie[-1]
        salida[est] = {
            "actual": ult[1],
            "fecha": ult[0].isoformat(),
            "serie": [[d.isoformat(), v] for d, v in serie],
        }
    if not salida:
        raise ValueError("Sin datos utilizables en el CSV")
    return salida


def parse_rss(texto, limite=8):
    raiz = ET.fromstring(texto.strip())
    items = []
    for it in raiz.iter("item"):
        g = lambda t: (it.findtext(t) or "").strip()
        items.append({"titulo": g("title"), "enlace": g("link"), "fecha": g("pubDate"),
                      "texto": re.sub(r"<[^>]+>", " ", g("description"))[:400].strip()})
        if len(items) >= limite:
            break
    return items


def fuente(nombre, fn):
    ahora = datetime.now(AR).isoformat()
    try:
        return {"ok": True, "consultado": ahora, "datos": fn()}
    except Exception as e:  # una fuente caída no debe romper a las demás
        return {"ok": False, "consultado": ahora, "error": f"{type(e).__name__}: {e}"}


def main(destino="docs/datos.json"):
    ahora = datetime.now(AR)
    shn = fuente("shn", lambda: parse_shn_csv(bajar(SHN_CSV), ahora))
    avisos = fuente("shn_rss", lambda: parse_rss(bajar(SHN_RSS)))
    ina = fuente("ina_rss", lambda: parse_rss(bajar(INA_RSS)))
    out = {"generado": ahora.isoformat(), "shn_alturas": shn, "shn_avisos": avisos, "ina": ina}
    # Conservar la última lectura buena si hoy falló la fuente
    try:
        previo = json.load(open(destino, encoding="utf-8"))
        for k in ("shn_alturas", "shn_avisos", "ina"):
            if not out[k]["ok"] and previo.get(k, {}).get("ok"):
                out[k]["ultimo_ok"] = previo[k].get("ultimo_ok") or {
                    "consultado": previo[k]["consultado"], "datos": previo[k]["datos"]}
    except (OSError, ValueError):
        pass
    json.dump(out, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("shn:", shn["ok"], "| shn_rss:", avisos["ok"], "| ina_rss:", ina["ok"])
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
