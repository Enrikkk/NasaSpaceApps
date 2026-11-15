# Field Shift: Adapting Farms with NASA Data — textos del formulario (Agrockham)

> Textos para pegar en el formulario del proyecto. La sección "Notas internas" NO se pega.

## Summary

Farmers make decisions about climate, soil and water with data scattered across dozens of sources, and most of it is hard to read or hard to trust. Agrockham puts it on one map. Click a farm plot and see the climate history from NASA satellites and models, the soil underneath, and a clear comparison of crop options: how often each one held up in past years, its risks, and what we still don't know. Field Shift asks how farms can adapt to a changing climate. Agrockham turns NASA's Earth data into a question a farmer can answer on Monday morning, and sends them to their agronomist with better questions, not to a black box.

## Project Details

**What it does.** Agrockham is a decision tool for farmers. The user searches a place on a map, zooms in to the official plot boundaries, and clicks one plot. The analysis arrives in blocks, each labelled *real*, *precalculated*, *simulated* or *loading*, so a demo is never mistaken for a fact. Each block shows:

- **Climate:** about 20 years of daily rainfall and temperature from NASA POWER and GPM IMERG.
- **Soil:** texture and organic matter from SoilGrids, plus reference evapotranspiration (how much water the crops lose).
- **Crop rotations:** a transparent engine (explicit rules and physics, no black box) simulates each rotation year by year, pairing climate and prices by year. Results show how often a rotation held up in past years, with a confidence interval, never a yield promise. The AI explains the results; the engine computes them.
- **Rules check:** a traffic light based on the applicable regulation, citing the article.
- **Honesty by design:** every card lists "what we do not know" and "ask your technician."

The current demo runs on real plot and climate data for one region of Spain, and the rotation numbers come from one reference plot. The method applies to any plot with the same kind of data; extending it to more regions and plots is our next step.

**Benefits and intended impact.** A comparison that normally takes an agronomist a week and a stack of reports becomes a few clicks. The aim is fewer costly rotation mistakes, better water planning, and earlier warning of climate risks, for farms under increasing heat and water stress. The long-term model is an annual subscription per managed hectare, plus a discount plan for farmers who share harvest results to improve the model.

**Tools and technology.** Python with FastAPI for the backend; a cached data pipeline, so the demo does not depend on venue Wi-Fi; Docker; Google Cloud Run for the live API; a web map frontend. Hardware: none in the demo. A low-cost soil-moisture sensor (ESP32) is on the roadmap.

**Creativity and what we considered.** Instead of another dashboard, we show uncertainty on purpose. Satellite and model rainfall sources disagree by about 40% on the same plot, so we show wide intervals instead of a fake precise number. The design goal is the simplest tool that works for a farmer with no technical background, which is where the name comes from: Ockham's razor. We also considered data licences (every source is cited), offline operation, clear labels on simulated content, and not giving legal advice.

## NASA Data

- NASA POWER (daily temperature, rainfall, radiation; API v2.10.3, accessed 2026-11-14): https://power.larc.nasa.gov/
- GPM IMERG rainfall, used through NASA POWER: https://gpm.nasa.gov/data
- *[pendiente de confirmar]* NASA GIBS imagery: https://nasa-gibs.github.io/gibs-api-docs/

## Space Agency Partner & Other Data

- SIGPAC agricultural plot boundaries, FEGA (CC BY 4.0): https://www.fega.gob.es/
- ISRIC SoilGrids 2.0 (CC BY 4.0): https://soilgrids.org/
- Open-Meteo ET0 (CC BY 4.0 data): https://open-meteo.com/
- Regional regulation text, BOE (public legislation): https://www.boe.es/buscar/doc.php?id=BOE-A-2020-9793
- Regional weather station data, SIAM-IMIDA (reuse allowed, owner credited): https://datosabiertos.regiondemurcia.es/
- Agricultural price indices, MAPA (reuse with source cited): https://www.mapa.gob.es/
- *[pendiente de confirmar]* PNOA aerial orthophoto, IGN/SCNE (CC BY 4.0): https://pnoa.ign.es/
- *[pendiente de completar]* Open-source libraries: listar desde el fichero de requisitos del backend

---

## Notas internas (NO pegar)

Antes de enviar, decidir:

1. **Precios regionales CARM/ESAM (D-010).** El `torre-pacheco.json` publicado los usa; licencia no comercial y permiso por pedir. Opciones: conseguir permiso, cambiar al fichero abierto (`torre-pacheco.abierto.json`) o declarar "permiso pendiente".
2. **Open-Meteo.** API gratuita solo no comercial. No presentar Agrockham como producto comercial sobre ella.
3. **Rotaciones.** Mantener que los números salen de una parcela de referencia hasta que exista el motor por parcela.
4. **SIGPAC.** Verificar el endpoint `recinfobypoint` y sus límites de uso antes de afirmar consultas en vivo a escala.
5. **GIBS y PNOA.** Incluir solo si la capa aparece realmente en el mapa.
6. **Licencia y URL del repo.** Hacen falta antes de enviar (T-017).
