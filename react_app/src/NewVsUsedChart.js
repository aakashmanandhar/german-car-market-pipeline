import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const THEMES = {
  dark: { tooltipBg: '#1B2233', tooltipBorder: '#232B3D', tooltipText: '#F4F5F7', axis: '#8B93A7' },
  light: { tooltipBg: '#FFFFFF', tooltipBorder: '#E2E4E9', tooltipText: '#171A21', axis: '#5C6272' },
};

function NewVsUsedChart({ selectedRegion, theme = 'dark' }) {
  const [data, setData] = useState([]);
  const c = THEMES[theme];
  const colors = { New: '#4C8DFF', Used: '#22D3EE' };

  useEffect(() => {
    const url = selectedRegion
      ? `http://localhost:8000/api/new-vs-used/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/new-vs-used/';
    axios.get(url).then(response => setData(response.data)).catch(error => console.error(error));
  }, [selectedRegion]);

  return (
    <div style={{ width: '100%', height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="purchase_count" nameKey="new_or_used" innerRadius={55} outerRadius={85} paddingAngle={3}>
            {data.map((entry) => <Cell key={entry.new_or_used} fill={colors[entry.new_or_used]} />)}
          </Pie>
          <Tooltip contentStyle={{ background: c.tooltipBg, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} />
          <Legend wrapperStyle={{ fontSize: 11, color: c.axis }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default NewVsUsedChart;