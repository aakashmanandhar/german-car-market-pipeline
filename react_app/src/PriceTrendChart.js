import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { grid: '#232B3D', axis: '#8B93A7', tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7' },
  light: { grid: '#E2E4E9', axis: '#5C6272', tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21' },
};

function PriceTrendChart({ selectedRegion, theme = 'dark' }) {
  const [data, setData] = useState([]);
  const c = THEMES[theme];

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/price-trend/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/price-trend/';
    axios.get(url).then(response => setData(response.data)).catch(error => console.error(error));
  }, [selectedRegion]);

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
          <XAxis dataKey="year" stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <YAxis stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} tickFormatter={(v) => `€${(v / 1000).toFixed(0)}k`} />
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} formatter={(v) => `€${v.toLocaleString()}`} />
          <Line type="monotone" dataKey="avg_net_price" stroke="#4C8DFF" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PriceTrendChart;