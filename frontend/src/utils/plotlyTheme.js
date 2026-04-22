// Apply to EVERY Plotly figure config before rendering

export const darkLayout = (overrides={}) => ({
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor:  'rgba(0,0,0,0)',
  font: { family:'DM Sans,sans-serif', color:'#8899bb', size:11 },
  margin: { l:0, r:0, t:28, b:0, pad:4 },
  legend: {
    bgcolor:     'rgba(17,29,58,0.9)',
    bordercolor: 'rgba(255,255,255,0.08)',
    borderwidth: 1,
    font: { color:'#8899bb', size:11 },
  },
  xaxis: {
    gridcolor:     'rgba(255,255,255,0.04)',
    zerolinecolor: 'rgba(255,255,255,0.06)',
    tickfont:      { color:'#4a5a7a', size:10 },
    linecolor:     'rgba(255,255,255,0.06)',
  },
  yaxis: {
    gridcolor:     'rgba(255,255,255,0.04)',
    zerolinecolor: 'rgba(255,255,255,0.06)',
    tickfont:      { color:'#4a5a7a', size:10 },
    linecolor:     'rgba(255,255,255,0.06)',
  },
  hoverlabel: {
    bgcolor:     '#111d3a',
    bordercolor: 'rgba(255,255,255,0.10)',
    font:        { color:'#eef2ff', size:12 },
  },
  colorway: [
    '#06d2ff','#7c6fff','#00e096',
    '#ffb547','#ff4d6d','#38d9f5'
  ],
  ...overrides
})

export const darkConfig = {
  displayModeBar: false,
  responsive:     true,
}
