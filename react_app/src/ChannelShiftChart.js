import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { grid: '#232B3D', axis: '#8B93A7', tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7' },
  light: { grid: '#E2E4E9', axis: '#5C6272', tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21' },
};

function ChannelShiftChart({ selectedRegion, theme = 'dark' }) {
  const [chartData, setChartData] = useState([]);
  const c = THEMES[theme];

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/channel-shift/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/channel-shift/';
    axios.get(url)
      .then(response => {
        const grouped = {};
        response.data.forEach(row => {
          if (!grouped[row.period]) grouped[row.period] = { period: row.period };
          grouped[row.period][row.channel_name] = row.purchase_count;
        });
        setChartData(Object.values(grouped));
      })
      .catch(error => console.error(error));
  }, [selectedRegion]);

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke={c.grid} />
          <XAxis dataKey="period" stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <YAxis stroke={c.axis} tick={{ fill: c.axis, fontSize: 11 }} />
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} cursor={{ fill: c.grid, opacity: 0.4 }} />
          <Legend wrapperStyle={{ fontSize: 11, color: c.axis }} />
          <Bar dataKey="In-person" fill="#4C8DFF" />
          <Bar dataKey="Phone" fill="#A78BFA" />
          <Bar dataKey="Online" fill="#22D3EE" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ChannelShiftChart;