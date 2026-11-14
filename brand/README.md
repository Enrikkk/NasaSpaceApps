# Agrockham · identidad visual

Todo lo necesario para que slides, vídeo, página del proyecto y app se vean igual. Owner: jaime.
La app aplica esto en `app/frontend/` (rama `t010-frontend-skeleton`); los valores exactos viven en
[`tokens.css`](tokens.css) y las reglas de contraste en `app/frontend/DESIGN.md`.

## Contenido de la carpeta

| Ruta | Qué es | Cuándo usarlo |
|---|---|---|
| `logo/agrockham-logo-on-dark.svg/.png` | AGRO verde + CKHAM crema, fondo transparente | **Versión principal**, sobre fondos oscuros o fotos de satélite |
| `logo/agrockham-logo-on-light.svg/.png` | AGRO verde + CKHAM verde oscuro, transparente | Sobre fondos claros (crema, blanco) |
| `logo/agrockham-logo-card.svg/.png` | Logo principal sobre tarjeta verde oscuro | Portada de slides, miniatura de vídeo, redes |
| `logo/agrockham-logo-cream.svg/.png` | Todo crema | Sobre fotos muy cargadas o fondos verdes |
| `logo/agrockham-logo-dark.svg/.png` | Todo verde oscuro | Impresión a una tinta, fondos muy claros |
| `logo/agrockham-icon.svg`, `-512.png`, `-180.png` | «A» rugosa sobre cuadrado verde oscuro | Favicon, icono de app, avatar |
| `color/agrockham-paleta.svg/.png` | Muestrario de la paleta | Referencia rápida |
| `fonts/` | Brunson y Brunson Rough (ver aviso de licencia) | Diseño en Figma/Keynote |
| `tokens.css` | Variables CSS (colores, tipos, espaciado, radios) | Cualquier página web nueva |

Los SVG del logo llevan las letras **convertidas en trazos**: se ven bien en cualquier programa sin instalar la fuente.
Los PNG son de 2400 px de ancho con fondo transparente (salvo la tarjeta y el icono).

## Logo

- Una sola palabra, en mayúsculas: **AGRO** en Brunson Rough (textura rugosa, «tierra») + **CKHAM** en Brunson.
- AGRO siempre en verde `#297847`. CKHAM en crema sobre oscuro y en verde oscuro sobre claro.
- En la app va sin caja, con un brillo verde suave debajo (`text-shadow: 0 6px 22px rgb(41 120 71 / 0.6)`).
- Margen libre alrededor: como mínimo la altura de la «O». Tamaño mínimo: 24 px de alto en pantalla.
- No: separar AGRO y CKHAM, cambiar el orden de colores, estirarlo, ponerle contorno o meterlo en una píldora
  de otro color, usar AGRO verde sobre fondo verde oscuro en tamaño pequeño (contraste 2,4:1, solo vale en grande).

## Paleta

| Nombre | Hex | Papel |
|---|---|---|
| Crema | `#F0EDE4` | Primario: texto, CKHAM, botón «Ver el mapa» |
| Verde AGRO | `#297847` | Secundario: AGRO, botón principal («Ir a mis parcelas») |
| Verde oscuro | `#1E3626` | Terciario: tarjetas de marca, fondo del icono |
| Gris carbón | `#2B2F2B` | Fondo de página |
| Superficie / hover / borde | `#373C36` / `#3D423C` / `#4B4F4A` | Paneles (Regiones, Filtros) |
| Texto secundario | `#B9BDB2` | Etiquetas, unidades |
| Verde claro | `#6BB383` | Títulos y texto verde sobre oscuro (REGIONES, FILTROS) |
| Ámbar / rojo | `#E0B04A` / `#E07A5F` | Semáforo legal (siempre con icono y palabra) |
| Espacio / atmósfera / mar | `#05070A` / `#8EC5FF` / `#1F4A86` | Escena del globo de inicio |

Contrastes comprobados (WCAG): crema sobre gris carbón 11,6:1 · crema sobre verde AGRO 4,6:1 (texto de botón)
· verde claro sobre gris carbón 5,4:1. El verde AGRO **no** se usa para texto pequeño sobre oscuro.

## Tipografía

| Rol | Fuente | Uso |
|---|---|---|
| Display rugosa | Brunson Rough | Solo «AGRO» del logo |
| Display | Brunson | «CKHAM», títulos grandes en mayúsculas (REGIONES, FILTROS) |
| Texto | Inter (OFL, Google Fonts) | Todo lo demás |

⚠️ **Licencia de Brunson pendiente.** Los ficheros dicen «© The Branded Quotes 2025. All Rights Reserved» y no
traen licencia (tienda: thebrandedquotes.sellfy.store). Las reglas de Space Apps piden material de terceros con
licencia abierta. jaime decidió usarlas mientras lo revisa; antes de la entrega hay que tener la licencia por
escrito o cambiar a **Anton** (OFL) con un efecto rugoso propio. Ver `submission/data-citations.md`.

## Estilo de la app y del mapa

- **Inicio:** vista cercana e inclinada del planeta (NASA Blue Marble con relieve y fondo marino), halo de
  atmósfera azul y estrellas sobre negro; España grande en el centro-derecha, el logo sobre el espacio.
  Botones abajo a la izquierda: «Ver el mapa» (crema, texto verde) e «Ir a mis parcelas» (verde, texto crema).
- **Mapa:** satélite (ortofoto PNOA del IGN) con nombres de pueblos y carreteras en blanco con halo oscuro, y los
  recintos SIGPAC siempre dibujados en líneas crema finas.
- **Paneles:** gris carbón translúcido, esquinas redondeadas (24 px paneles, 12 px tarjetas, píldora para
  botones y etiquetas), sin sombras duras. Títulos en Brunson verde claro.
- **Movimiento:** transiciones lentas y suaves (`cubic-bezier(0.22, 1, 0.36, 1)`, 600-900 ms): el zoom del globo
  a la parcela es el momento estrella de la demo.

## Voz

Castellano llano, para agricultores: frases cortas, de tú, cifras con su unidad («7.746 € por hectárea y año»),
y siempre la salvedad cuando algo es provisional o no lo sabemos. Nunca prometer resultados ni dar consejo legal.

## Créditos que tienen que verse

Cuando se muestre el mapa (capturas en slides o vídeo), los créditos de la esquina deben seguir legibles:
NASA GIBS Blue Marble, IGN (CC BY 4.0 scne.es), Recintos SIGPAC © FEGA (CC BY 4.0).

## Cómo se generó el logo

Texto convertido en trazos con [opentype.js](https://opentype.js.org/) (MIT) a partir de `fonts/` y exportado a
PNG con `rsvg-convert` (librsvg). Para regenerarlo con otra fuente basta con repetir ese proceso.
