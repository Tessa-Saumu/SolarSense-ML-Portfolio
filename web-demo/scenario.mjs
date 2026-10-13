export const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const DAYS = [31,28,31,30,31,30,31,31,30,31,30,31];
export function calculate(input, evidence) {
  if (!input || Array.isArray(input) || typeof input!=='object') throw Error('Provide scenario inputs.');
  if (evidence.contract_version!=='solarsense-scenario-v1') throw Error('Evidence contract mismatch.');
  if (Object.keys(input).some(k=>!(k in evidence.defaults))) throw Error('Unknown scenario field.');
  const business=input.business_type ?? 'bakery';
  if (!Object.hasOwn(evidence.business_profiles,business)) throw Error('Choose bakery, grocery or butchery.');
  const x={...evidence.defaults,...evidence.business_profiles[business],...input};
  if (x.country!=='Kenya'||x.city!=='Nairobi') throw Error('This demonstration supports Nairobi, Kenya only.');
  if (!['formula','measured'].includes(x.consumption_mode)) throw Error('Choose a consumption method.');
  if (!['baseline','xgboost'].includes(x.solar_profile)) throw Error('Choose a supported solar profile.');
  for(const [key,[lo,hi]] of Object.entries(evidence.input_limits)) if(typeof x[key]!=='number'||!Number.isFinite(x[key])||x[key]<lo||x[key]>hi) throw Error(`${key.replaceAll('_',' ')} must be between ${lo} and ${hi}.`);
  const profiles=evidence.solar_profiles, predictions=profiles?.[x.solar_profile];
  if (!Array.isArray(predictions)||predictions.length!==12||predictions.some(v=>!Number.isFinite(v)||v<0)||!evidence.model_sha256) throw Error('Verified model evidence is unavailable.');
  const consumption=x.consumption_mode==='measured'?x.monthly_consumption_kwh:x.average_load_kw*x.hours_per_day*x.days_per_month;
  const factor=x.panel_area_m2/evidence.reference_system.panel_area_m2*x.efficiency/evidence.reference_system.efficiency;
  const monthly=DAYS.map((days,i)=>{const generation=predictions[i]*factor*days;return {month:i+1,days,reference_kwh_day:predictions[i],generation_kwh:generation,offset_kwh:Math.min(consumption,generation*x.self_consumption_fraction)};});
  const annual=consumption*12,generation=monthly.reduce((a,m)=>a+m.generation_kwh,0),offset=monthly.reduce((a,m)=>a+m.offset_kwh,0);
  const avoided=offset*x.tariff_kes_per_kwh,net=avoided-x.annual_maintenance_kes,grid=annual*x.tariff_kes_per_kwh,pv=(annual-offset)*x.tariff_kes_per_kwh;
  return {contract_version:evidence.contract_version,input:x,location:evidence.location,consumption:{method:x.consumption_mode,monthly_kwh:consumption,annual_kwh:annual},solar:{method:x.solar_profile==='baseline'?'training-city monthly mean baseline':'held-out evaluated XGBoost artifact, derived solar target',selected_profile:x.solar_profile,reference_profiles_kwh_day:profiles,model_sha256:evidence.model_sha256,monthly,annual_generation_kwh:generation,annual_offset_kwh:offset,coverage_percent:annual?offset/annual*100:0},comparison:{grid_only_annual_cost_kes:grid,pv_annual_grid_cost_kes:pv,pv_annual_operating_cost_kes:pv+x.annual_maintenance_kes,annual_avoided_grid_cost_kes:avoided,net_annual_saving_kes:net,simple_payback_years:net>0?x.installed_cost_kes/net:null},sensitivity:[0.8,1,1.2].map(f=>({tariff_kes_per_kwh:x.tariff_kes_per_kwh*f,annual_avoided_grid_cost_kes:offset*x.tariff_kes_per_kwh*f,net_annual_saving_kes:offset*x.tariff_kes_per_kwh*f-x.annual_maintenance_kes})),assumptions:evidence.assumptions,limitations:evidence.limitations};
}
export function csv(result) {
  return 'month,days,consumption_kwh,generation_kwh,usable_offset_kwh,solar_profile,model_sha256\n'+result.solar.monthly.map(m=>[m.month,m.days,result.consumption.monthly_kwh,m.generation_kwh,m.offset_kwh,result.solar.selected_profile,result.solar.model_sha256].join(',')).join('\n')+'\n';
}
export const escapeHTML = value => String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function report(result) {
  const e=escapeHTML, n=v=>Number(v).toFixed(2);
  return `<!doctype html><html lang="en"><meta charset="utf-8"><title>SolarSense scenario report</title><style>body{font:16px system-ui;max-width:900px;margin:40px auto;padding:20px;color:#17304a}table{border-collapse:collapse;width:100%}td,th{padding:10px;text-align:left;border-bottom:1px solid #ccd}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media print{button{display:none}}</style><h1>SolarSense · Nairobi scenario</h1><p>Illustrative calculation, not measured savings or an installation quotation.</p><button onclick="window.print()">Print / save PDF</button><h2>Comparison</h2><p>Grid-only annual energy cost: KES ${n(result.comparison.grid_only_annual_cost_kes)}<br>PV annual operating cost: KES ${n(result.comparison.pv_annual_operating_cost_kes)}<br>Net annual cost difference: KES ${n(result.comparison.net_annual_saving_kes)}</p><h2>Monthly energy</h2><table><tr><th>Month</th><th>Consumption kWh</th><th>Generation kWh</th><th>Usable offset kWh</th></tr>${result.solar.monthly.map(m=>`<tr><td>${MONTHS[m.month-1]}</td><td>${n(result.consumption.monthly_kwh)}</td><td>${n(m.generation_kwh)}</td><td>${n(m.offset_kwh)}</td></tr>`).join('')}</table><h2>Inputs</h2><pre>${e(JSON.stringify(result.input,null,2))}</pre><h2>Assumptions and limitations</h2><ul>${[...result.assumptions,...result.limitations].map(a=>`<li>${e(a)}</li>`).join('')}</ul><p>Model SHA256: ${e(result.solar.model_sha256)}</p></html>`;
}
