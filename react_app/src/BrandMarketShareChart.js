import { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function BrandMarketShareChart() {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/api/brand-market-share/')
      .then(response => {
        // Reshape the flat API data into one row per year, one column per brand —
        // exactly the shape Recharts' LineChart expects for multiple lines.
        const grouped = {};
        response.data.forEach(row => {
          if (!grouped[row.year]) {
            grouped[row.year] = { year: row.year };
          }
          grouped[row.year][row.brand_name] = row.purchase_count;
        });
        setChartData(Object.values(grouped).sort((a, b) => a.year - b.year));
      })
      .catch(error => console.error('Error fetching brand market share:', error));
  }, []);

  const brands = ["Volkswagen", "BMW", "Mercedes-Benz", "Audi", "Porsche", "Opel", "Toyota", "Renault", "Skoda", "Fiat"];
  const colors = ["#1E88E5", "#43A047", "#E53935", "#FB8C00", "#8E24AA", "#00897B", "#D81B60", "#5D4037", "#3949AB", "#C0CA33"];

  return (
    <div style={{ width: '100%', height: 500, padding: '20px' }}>
      <h2>Brand Market Share, 1990–2026</h2>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis label={{ value: 'Purchases', angle: -90, position: 'insideLeft' }} />
          <Tooltip />
          <Legend />
          {brands.map((brand, i) => (
            <Line key={brand} type="monotone" dataKey={brand} stroke={colors[i]} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BrandMarketShareChart;