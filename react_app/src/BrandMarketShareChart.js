import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { grid: '#232B3D', axis: '#8B93A7', tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7' },
  light: { grid: '#E2E4E9', axis: '#5C6272', tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21' },
};

function BrandMarketShareChart({ selectedRegion, theme = 'dark' }) {
  const [chartData, setChartData] = useState([]);
  const c = THEMES[theme];

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/brand-market-share/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/brand-market-share/';
    axios.get(url)
      .then(response => {
        const grouped = {};
        response.data.forEach(row => {
          if (!grouped[row.year]) grouped[row.year] = { year: row.year };
          grouped[row.year][row.brand_name] = row.purchase_count;
        });
        setChartData(Object.values(grouped).sort((a, b) => a.year - b.year));
      })
      .catch(error => console.error('Error fetching brand market share:', error));
  }, [selectedRegion]);

  const brands = ["Volkswagen", "BMW", "Mercedes-Benz", "Audi", "Porsche", "Opel", "Toyota", "Renault", "Skoda", "Fiat"];
  const colors = ["#4C8DFF", "#43A047", "#E53935", "#FB8C00", "#A78BFA", "#00897B", "#D81B60", "#8D6E63", "#3949AB", "#C0CA33"];

  return (
    <div style={{ width: '100%', height: 400 }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
          <XAxis dataKey="year" stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <YAxis stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} label={{ value: 'Purchases', angle: -90, position: 'insideLeft', fill: c.axis }} />
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} cursor={{ fill: c.grid, opacity: 0.4 }} />
          <Legend wrapperStyle={{ fontSize: 11, color: c.axis }} />
          {brands.map((brand, i) => (
            <Line key={brand} type="monotone" dataKey={brand} stroke={colors[i]} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BrandMarketShareChart;