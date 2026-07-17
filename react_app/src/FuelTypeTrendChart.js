import { useState, useEffect } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { grid: '#232B3D', axis: '#8B93A7', tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7' },
  light: { grid: '#E2E4E9', axis: '#5C6272', tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21' },
};

function FuelTypeTrendChart({ selectedRegion, theme = 'dark' }) {
  const [chartData, setChartData] = useState([]);
  const c = THEMES[theme];

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/fuel-type-trend/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/fuel-type-trend/';
    axios.get(url)
      .then(response => {
        const grouped = {};
        response.data.forEach(row => {
          if (!grouped[row.year]) grouped[row.year] = { year: row.year, petrol: 0, diesel: 0, hybrid: 0, electric: 0 };
          grouped[row.year][row.fuel_type] = row.purchase_count;
        });
        setChartData(Object.values(grouped).sort((a, b) => a.year - b.year));
      })
      .catch(error => console.error('Error fetching fuel type trend:', error));
  }, [selectedRegion]);

  return (
    <div style={{ width: '100%', height: 320 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
          <XAxis dataKey="year" stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <YAxis stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} />
          <Legend wrapperStyle={{ fontSize: 11, color: c.axis }} />
          <Area type="monotone" dataKey="petrol" stackId="1" stroke="#FB8C00" fill="#FB8C00" fillOpacity={0.7} />
          <Area type="monotone" dataKey="diesel" stackId="1" stroke="#5C6272" fill="#5C6272" fillOpacity={0.7} />
          <Area type="monotone" dataKey="hybrid" stackId="1" stroke="#A78BFA" fill="#A78BFA" fillOpacity={0.7} />
          <Area type="monotone" dataKey="electric" stackId="1" stroke="#22D3EE" fill="#22D3EE" fillOpacity={0.7} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FuelTypeTrendChart;