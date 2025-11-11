// FrontendSvelte/src/lib/chart/growth-chart.js
// Single Chart Z-score (5 lines): Z-BB, Z-TB, Z-IMT, Z-LK, Z-LILA

import ApexCharts from 'apexcharts';

const PALETTE = ["#2d626a", "#428a91", "#6f9c97", "#aecdc7", "#f0f1c7"];

async function fetchGrafik(id_anak){
  const res = await fetch(`/api/pengukuran/${id_anak}/grafik`);
  if(!res.ok) throw new Error('Gagal memuat data grafik');
  return await res.json();
}

export async function renderGrowthCharts(container, id_anak){
  const el = (typeof container === 'string') ? document.querySelector(container) : container;
  if(!el) return;

  let data;
  try{
    data = await fetchGrafik(id_anak);
  }catch(err){
    el.innerHTML = '<p class="text-red-500">Gagal memuat grafik: '+err.message+'</p>';
    return;
  }

  const categories = data.monthly.categories;

  const series = [
    { name:'Z-BB',   data: data.monthly.z_bb },
    { name:'Z-TB',   data: data.monthly.z_tb },
    { name:'Z-IMT',  data: data.monthly.z_imt },
    { name:'Z-LK',   data: data.monthly.z_lk },
    { name:'Z-LILA', data: data.monthly.z_lila }
  ];

  const options = {
    chart:{ type:'line', height:330 },
    colors:PALETTE,
    stroke:{ width:3, curve:'smooth' },
    series,
    xaxis:{ categories, labels:{ rotate:-45 }},
    yaxis:{ title:{ text:'Z-Score' }},
    legend:{ position:'top' },
    title:{ text:'Grafik Perkembangan Z-Score', align:'left' },
  };

  const chart = new ApexCharts(el, options);
  await chart.render();
  
  return chart;
}
