# Agrockham: líneas de diseño

Owner: jaime. Fuente de verdad del aspecto visual del frontend. Los valores viven en
[`design/tokens.css`](design/tokens.css); este documento explica cuándo usar cada uno.

## Marca

- Logo: palabra **AGRO** en verde `#297847` con la versión *rough* de la tipografía display,
  **CKHAM** en crema `#F0EDE4` con la versión limpia. Todo en mayúsculas, sin espacio.
- El logo va siempre sobre fondo oscuro (`--bg` o `--brand-dark`), nunca sobre crema.

## Paleta (decidida por jaime, 2026-11-14)

| Token | Hex | Papel |
|---|---|---|
| `--cream` | `#F0EDE4` | Primario. Texto principal y CKHAM del logo |
| `--green` | `#297847` | Secundario. AGRO del logo, relleno de botones principales |
| `--brand-dark` | `#1E3626` | Terciario. Cabecera, bandas de marca, chips |
| `--bg` | `#2B2F2B` | Fondo de la página (gris carbón verdoso, opción B) |

Derivados (calculados para que se lean sobre el fondo oscuro):

| Token | Hex | Papel |
|---|---|---|
| `--surface-1` | `#373C36` | Tarjetas (parcela, rotaciones) |
| `--surface-2` | `#3D423C` | Hover o tarjeta seleccionada |
| `--border` | `#4B4F4A` | Bordes finos de tarjetas e inputs |
| `--text-muted` | `#B9BDB2` | Texto secundario, etiquetas, unidades |
| `--green-light` | `#6BB383` | Texto, iconos y enlaces verdes sobre oscuro |
| `--warn` | `#E0B04A` | Semáforo ámbar |
| `--danger` | `#E07A5F` | Semáforo rojo |

## Contraste (WCAG, comprobado)

| Combinación | Ratio | Uso permitido |
|---|---|---|
| crema sobre `--bg` / `--surface-1` / `--brand-dark` | 11.6 / 9.6 / 11.1 | Todo |
| `--text-muted` sobre `--bg` / `--surface-1` | 7.1 / 5.9 | Todo |
| crema sobre `--green` (botón) | 4.6 | Texto de botón (AA) |
| `--green-light` sobre `--bg` / `--surface-1` | 5.4 / 4.5 | Texto verde, iconos |
| `--green` sobre `--bg` o `--brand-dark` | 2.5 / 2.4 | **Solo logo y rellenos grandes, nunca texto** |
| `--brand-dark` sobre `--bg` | 1.04 | No se distinguen: si una superficie `--brand-dark` va sobre `--bg`, lleva borde `--border` |
| `--danger` sobre `--surface-1` | 3.8 | Iconos y texto ≥ 18 px; acompañar siempre de icono + palabra |

Reglas:

1. Las tarjetas suben de luminosidad para separarse del fondo (`--bg` → `--surface-1` → `--surface-2`),
   sin sombras.
2. El color nunca es el único portador de información: el semáforo legal lleva icono y palabra
   ("Permitido", "Revisar", "No permitido").
3. Un solo botón relleno `--green` por pantalla; el resto, contorno `--border` con texto crema.

## Tipografía

| Rol | Fuente | Uso |
|---|---|---|
| Display rough | Brunson Rough | Solo "AGRO" del logo |
| Display | Brunson | "CKHAM" del logo y titulares grandes (≥ 28 px), en mayúsculas |
| Texto | Inter (propuesta, OFL) | Todo lo demás: tarjetas, cifras, etiquetas |

Ficheros: `design/fonts/Brunson.ttf` y `design/fonts/Brunson-Rough.ttf`, declarados con `@font-face`
en `tokens.css`. Si no cargan, el respaldo es **Anton** (OFL, Google Fonts).

**⚠️ PENDIENTE antes del deploy público y de la entrega:** los ficheros dicen
"© The Branded Quotes 2025. All Rights Reserved" (tienda: thebrandedquotes.sellfy.store) y no traen
licencia. jaime decidió usarlos ya en desarrollo mientras revisa la licencia. Las reglas de Space Apps
(`context/official-rules.md` §2) exigen que el material de terceros sea libre o de licencia abierta e
identificada, así que antes del deploy (T-017) y del envío (T-015) hay que: (a) tener una licencia que
permita uso público + webfont + redistribución y citarla en `submission/`, o (b) cambiar a Anton +
filtro SVG propio para el efecto *rough* (dos líneas de `tokens.css`) y borrar `design/fonts/`.

## Escala

- Texto: 12 / 14 / 16 (cuerpo) / 20 / 28 / 40 / 64 (display) px.
- Espaciado: múltiplos de 4 px (4, 8, 12, 16, 24, 32, 48).
- Radios: 6 px controles, 12 px tarjetas.
