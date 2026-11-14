"""Semaforo legal de cada rotacion con legal.check() (vendor/legal.py, copia de legal_rules/legal.py).

Herramienta de apoyo, no es asesoria legal. Consulta a tu tecnico. Todas las reglas siguen `por_verificar` en el BOE.
"""
from vendor import legal as L

SUPUESTO_CICLOS = "ciclos_por_anio = 1 (el contrato v1 aun no lo lleva; cada ciclo listado cuenta como una campana anual)"


def canon_cultivo(nombre: str) -> str:
    """Nombre de un ciclo del motor ("Alcachofa (gorda)", "Lechuga iceberg") -> nombre que conoce legal.GRUPOS.

    Solo normaliza variantes obvias (parentesis, variedad detras del cultivo). Si no reconoce nada devuelve el nombre
    tal cual y legal.check() lo tratara como grupo desconocido (art. 51.4): nunca se inventa un grupo.
    """
    n = L._norm(nombre)
    if n in L.GRUPOS:
        return nombre
    sin_par = L._norm(n.split("(")[0])
    if sin_par in L.GRUPOS:
        return sin_par
    for clave in sorted(L.GRUPOS, key=len, reverse=True):
        if sin_par.startswith(clave + " "):
            return clave
    return nombre


def entrada_legal(rot: dict) -> tuple[dict, list[str]]:
    """Rotacion del contrato -> entrada de legal.check(); devuelve (entrada, supuestos aplicados)."""
    supuestos = []
    ent = {"es_actual": bool(rot.get("es_actual"))}
    if rot.get("anios"):
        anios = [[canon_cultivo(c) for c in a] for a in rot["anios"]]
        ent["anios"] = anios
        ent["ciclos"] = [c for a in anios for c in a]
    else:
        ent["ciclos"] = [canon_cultivo(c) for c in rot.get("ciclos", [])]
        ent["ciclos_por_anio"] = rot.get("ciclos_por_anio") or 1
        if not rot.get("ciclos_por_anio"):
            supuestos.append(SUPUESTO_CICLOS)
    for k in ("ciclo_dias", "suelo_desnudo_meses", "cobertera_invierno", "n_kg_ha_anio", "abonado"):
        if k in rot:
            ent[k] = rot[k]
    return ent, supuestos


def aplicar(rotaciones: list, parcela: dict, ndvi: dict, nivel_cobertura: str, zona: str) -> list:
    """Sustituye `semaforo_legal` de cada rotacion cargada por el calculado con legal.check() (vocabulario del esquema)."""
    ent_parcela = {"regadio": bool(parcela.get("regadio")), "ndvi": ndvi if ndvi and ndvi.get("_status") != "cargando" else None,
                   "cobertura": nivel_cobertura}
    for rot in rotaciones:
        if rot.get("_status") == "cargando":
            continue
        ent, supuestos = entrada_legal(rot)
        sem = L.check(ent, ent_parcela, zona, contrato=True)
        sem["_status"] = rot["_status"]  # hereda: el calculo es determinista, pero sus entradas son las de la rotacion
        sem["motor_legal"] = f"legal.check (reglas {L.VERSION_REGLAS}, todas por_verificar)"
        if supuestos:
            sem["supuestos"] = supuestos
        rot["semaforo_legal"] = sem
    return rotaciones
