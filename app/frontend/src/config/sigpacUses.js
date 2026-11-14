// SIGPAC land-use codes (uso_sigpac) -> readable names. Source: FEGA official code table cod_usosigpac.csv in
// https://www.fega.gob.es/atom/2026/sigpac_codes_2026.zip (campaign 2026). Wording kept, case normalised.
export const SIGPAC_USES = {
  AG: 'Corrientes y superficies de agua',
  CA: 'Viales',
  CF: 'Asociación cítricos-frutales',
  CI: 'Cítricos',
  CS: 'Asociación cítricos-frutales de cáscara',
  CV: 'Asociación cítricos-viñedo',
  ED: 'Edificaciones',
  EP: 'Elemento del paisaje',
  FF: 'Asociación frutales-frutales de cáscara',
  FL: 'Frutos secos y olivar',
  FO: 'Forestal',
  FS: 'Frutos secos',
  FV: 'Frutos secos y viñedo',
  FY: 'Frutales',
  IM: 'Improductivos',
  IV: 'Invernaderos y cultivos bajo plástico',
  MT: 'Matorral',
  OC: 'Asociación olivar-cítricos',
  OF: 'Olivar-frutal',
  OP: 'Otros cultivos permanentes',
  OV: 'Olivar',
  PA: 'Pasto con arbolado',
  PR: 'Pasto arbustivo',
  PS: 'Pastizal',
  TA: 'Tierras arables',
  TH: 'Huerta',
  VF: 'Viñedo-frutal',
  VI: 'Viñedo',
  VO: 'Viñedo-olivar',
  ZC: 'Zona concentrada no incluida en la ortofoto',
  ZU: 'Zona urbana',
  ZV: 'Zona censurada',
}

/** "TA" -> "Tierras arables (TA)"; unknown codes are shown as they come. */
export function sigpacUseLabel(code) {
  if (!code) return '—'
  const name = SIGPAC_USES[String(code).toUpperCase()]
  return name ? `${name} (${code})` : String(code)
}
