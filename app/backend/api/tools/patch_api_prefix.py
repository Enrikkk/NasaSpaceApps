"""Parche aditivo usado para construir la imagen v9 sobre integracion f964717 (que no tenia el alias /api): anade a main.py el bloque
que repite las rutas bajo /api/*. Es el MISMO cambio que main bfab7ce; se conserva solo para reproducibilidad de la v9.
Uso: python3 patch_api_prefix.py <raiz del arbol de integracion>"""
import sys
p = sys.argv[1] + "/app/backend/api/main.py"
s = open(p, encoding="utf-8").read()
if "alias /api" in s:
    print("ya parcheado"); sys.exit(0)
marca = "    # La app estatica va AL FINAL"
assert marca in s, "no encuentro el punto de montaje de la app estatica"
bloque = '''    # alias /api: las mismas rutas tambien bajo /api/* (la app estatica vive en /; el cliente puede usar VITE_API_BASE=<url>/api).
    # Se mantienen las rutas sin prefijo por compatibilidad (QA, gates, /docs).
    from fastapi.routing import APIRoute
    for _r in list(app.routes):
        if isinstance(_r, APIRoute) and not _r.path.startswith("/api"):
            app.add_api_route("/api" + _r.path, _r.endpoint, methods=sorted(_r.methods or []), response_model=_r.response_model,
                              include_in_schema=False, response_class=_r.response_class)
'''
s = s.replace(marca, bloque + marca, 1)
open(p, "w", encoding="utf-8").write(s)
print("parcheado")
