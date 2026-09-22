"""
config.py
EP-TSP / Early Injury-Risk Signal Pipeline

Objetivo: probar si declives de velocidad/spin y aumento de variabilidad
de release point, medidos en las semanas previas a una colocacion real en
el IL por lesion de codo/hombro, son estadisticamente distinguibles de una
ventana equivalente en pitchers sanos.

IMPORTANTE — alcance y limites:
Este es un analisis EXPLORATORIO / generador de hipotesis con un cohorte
pequeno (n declarado explicitamente en cada resultado). NO es una
herramienta de diagnostico medico ni un modelo de produccion. Todas las
fechas de lesion provienen de fuentes publicas (MLB.com Transactions,
reportes de prensa); se documentan con su fuente y se marca la confianza
de la fecha. Ningun hallazgo aqui debe usarse para decisiones medicas
reales sin la participacion de personal medico certificado del equipo.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT_DIR / "data" / "raw"
DATA_PROCESSED = ROOT_DIR / "data" / "processed"
OUTPUTS_FIGURES = ROOT_DIR / "outputs" / "figures"
OUTPUTS_REPORTS = ROOT_DIR / "outputs" / "reports"

for _dir in [DATA_RAW, DATA_PROCESSED, OUTPUTS_FIGURES, OUTPUTS_REPORTS]:
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Estilo visual EP
# ---------------------------------------------------------------------------
EP_NAVY = "#0B1B33"
EP_GOLD = "#D4A53A"
EP_OFFWHITE = "#F5F3EC"
EP_PALETTE = [EP_NAVY, EP_GOLD, "#5B7A9D", "#B5482A", "#3D6B4F"]

# ---------------------------------------------------------------------------
# Ventana de analisis pre-evento
# ---------------------------------------------------------------------------
PRE_EVENT_WINDOW_DAYS = 42       # 6 semanas antes de la fecha de IL
MIN_PITCHES_REQUIRED = 100       # umbral minimo para no descartar el caso
MIN_DAYS_ACTIVE_REQUIRED = 5     # minimo de salidas/apariciones distintas antes del evento
# Nota de calibracion: en una ventana de 42 dias, un abridor tipico (~cada 5
# dias) alcanza como maximo ~8 salidas, y un relevista de alto uso ~16-17.
# Un umbral de 21 (usado en una version anterior de este archivo) era
# matematicamente inalcanzable para CUALQUIER pitcher y habria marcado el
# 100% de los casos como sufficient_data=False. 5 salidas distintas es un
# minimo razonable para calcular una pendiente con algo de estabilidad.

# ---------------------------------------------------------------------------
# Cohorte de lesion (elbow/shoulder), curado desde fuentes publicas
# Cada entrada: (last, first, team, il_date, injury_type, source, date_confidence)
# date_confidence: "exact" (fecha confirmada en transaccion oficial) o
# "approx" (fecha estimada desde reporte de prensa, no transaccion oficial)
# ---------------------------------------------------------------------------
INJURY_COHORT = [
    {"last": "Hollowell", "first": "Gavin", "team": "CHC", "il_date": "2026-07-31",
     "injury_type": "shoulder inflammation", "source": "MLB.com Cubs injury report", "date_confidence": "exact"},
    {"last": "Steele", "first": "Justin", "team": "CHC", "il_date": "2026-03-25",
     "injury_type": "elbow flexor strain", "source": "MLB.com Cubs injury report", "date_confidence": "exact"},
    {"last": "Horton", "first": "Cade", "team": "CHC", "il_date": "2026-04-05",
     "injury_type": "UCL damage (elbow)", "source": "MLB.com Cubs injury report", "date_confidence": "exact"},
    {"last": "Kittredge", "first": "Andrew", "team": "BAL", "il_date": "2026-03-22",
     "injury_type": "shoulder inflammation", "source": "MLB.com Transactions", "date_confidence": "exact"},
    {"last": "Cortes", "first": "Nestor", "team": "MIL", "il_date": "2025-04-04",
     "injury_type": "elbow flexor strain", "source": "MLB.com Transactions", "date_confidence": "exact"},
    {"last": "Snell", "first": "Blake", "team": "LAD", "il_date": "2025-04-03",
     "injury_type": "shoulder inflammation", "source": "MLB.com Transactions", "date_confidence": "exact"},
    {"last": "Bradford", "first": "Cody", "team": "TEX", "il_date": "2025-03-24",
     "injury_type": "elbow sprain", "source": "MLB.com Transactions", "date_confidence": "exact"},
    {"last": "Lopez", "first": "Pablo", "team": "MIN", "il_date": "2025-06-05",
     "injury_type": "shoulder (teres major strain)", "source": "Sports Injury Central press report", "date_confidence": "approx"},
    {"last": "Mahle", "first": "Tyler", "team": "TEX", "il_date": "2025-06-10",
     "injury_type": "shoulder (rotator cuff strain)", "source": "Sports Injury Central press report", "date_confidence": "approx"},
    {"last": "Eovaldi", "first": "Nathan", "team": "TEX", "il_date": "2026-08-17",
     "injury_type": "elbow inflammation", "source": "FOX Sports MLB buzz report", "date_confidence": "approx"},
    {"last": "Whitlock", "first": "Garrett", "team": "BOS", "il_date": "2026-08-20",
     "injury_type": "elbow inflammation", "source": "FOX Sports MLB buzz report", "date_confidence": "approx"},
]

# ---------------------------------------------------------------------------
# Cohorte de control (pitchers "sanos" de referencia)
# Fechas de referencia repartidas para emparejar el momento de temporada de
# cada caso de lesion (evita el sesgo de comparar todo contra un solo punto
# del calendario, donde fatiga de fin de temporada afectaria por igual a
# lesionados y sanos). Sigue siendo un cohorte de arranque pequeno — antes
# de sacar conclusiones firmes, expandir con una muestra aleatoria mas
# grande de pitchers con temporada completa sin IL.
# ---------------------------------------------------------------------------
CONTROL_COHORT = [
    {"last": "Skenes", "first": "Paul", "team": "PIT", "reference_date": "2026-07-31"},   # empareja con Hollowell
    {"last": "Wheeler", "first": "Zack", "team": "PHI", "reference_date": "2026-03-25"},   # empareja con Steele
    {"last": "Skenes", "first": "Paul", "team": "PIT", "reference_date": "2026-04-05"},    # empareja con Horton
    {"last": "Wheeler", "first": "Zack", "team": "PHI", "reference_date": "2026-03-22"},   # empareja con Kittredge
    {"last": "Skenes", "first": "Paul", "team": "PIT", "reference_date": "2026-08-17"},    # empareja con Eovaldi
    {"last": "Wheeler", "first": "Zack", "team": "PHI", "reference_date": "2026-08-20"},   # empareja con Whitlock
]
