import sys; sys.path.insert(0, "scripts")
from datetime import datetime
from recolectar import parse_shn_csv, parse_rss, AR
csv_txt = """Fecha y hora;Martín García;San Fernando;Buenos Aires;Pilote Norden;La Plata;Atalaya;Oyarvide
17/10/2026 16:45;1.54;1.24;1.15;1.17;1.15;1.35;1.53
17/10/2026 15:45;S/D;1.34;1.24;1.19;1.13;1.14;1.38
17/10/2026 14:45;1.61;1.37;1.34;1.24;1.18;1.05;1.20
"""
r = parse_shn_csv(csv_txt, ahora=datetime(2026,10,17,17,0,tzinfo=AR))
assert r["San Fernando"]["actual"] == 1.24 and len(r["San Fernando"]["serie"]) == 3
assert r["Martín García"]["actual"] == 1.54 and len(r["Martín García"]["serie"]) == 2  # S/D omitido
assert r["San Fernando"]["serie"][0][1] == 1.37  # orden cronológico
try:
    parse_shn_csv("<html>error</html>"); raise SystemExit("debía fallar")
except ValueError: pass
rss = "<rss><channel><item><title>Alerta por crecida</title><link>http://x</link><pubDate>hoy</pubDate><description>&lt;b&gt;San Fernando 2,9 m&lt;/b&gt;</description></item></channel></rss>"
assert parse_rss(rss)[0]["texto"] == "San Fernando 2,9 m"
print("OK")
