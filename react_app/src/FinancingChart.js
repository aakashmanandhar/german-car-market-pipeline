import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { grid: '#232B3D', axis: '#8B93A7', tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7' },
  light: { grid: '#E2E4E9', axis: '#5C6272', tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21' },
};

function FinancingChart({ selectedRegion, theme = 'dark' }) {
  const [data, setData] = useState([]);
  const c = THEMES[theme];

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/revenue-by-financing/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/revenue-by-financing/';
    axios.get(url).then(response => setData(response.data)).catch(error => console.error(error));
  }, [selectedRegion]);

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
          <XAxis dataKey="type_name" stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <YAxis stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`} />
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} cursor={{ fill: c.grid, opacity: 0.4 }} formatter={(v) => `€${v.toLocaleString()}`} />
          <Bar dataKey="total_revenue" fill="#4C8DFF" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FinancingChart;