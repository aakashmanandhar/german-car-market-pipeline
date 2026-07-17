import { useState, useEffect } from 'react';
import axios from 'axios';

function KpiCards({ selectedRegion }) {
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    const url = selectedRegion 
      ? `http://localhost:8000/api/kpi-summary/?region=${encodeURIComponent(selectedRegion)}`
      : 'http://localhost:8000/api/kpi-summary/';
    axios.get(url)
      .then(response => setKpis(response.data))
      .catch(error => console.error('Error fetching KPIs:', error));
  }, [selectedRegion]);

  if (!kpis) return <div>Loading KPIs...</div>;

  const cardStyle = {
    flex: 1,
    background: '#F7F8FA',
    border: '1px solid #E2E4E9',
    borderRadius: '12px',
    padding: '20px',
    textAlign: 'center',
  };

  const valueStyle = { fontSize: '28px', fontWeight: 700, marginTop: '8px' };
  const labelStyle = { fontSize: '12px', color: '#5C6272', textTransform: 'uppercase', letterSpacing: '0.05em' };

  return (
    <div className="kpi-row">
      <div className="kpi-card">
        <div className="label">Total Revenue</div>
        <div className="value">€{(kpis.total_revenue / 1_000_000_000).toFixed(2)}B</div>
      </div>
      <div className="kpi-card">
        <div className="label">Avg Net Price</div>
        <div className="value">€{kpis.avg_net_price.toLocaleString()}</div>
      </div>
      <div className="kpi-card">
        <div className="label">Total Purchases</div>
        <div className="value">{kpis.total_purchases.toLocaleString()}</div>
      </div>
      <div className="kpi-card">
        <div className="label">EV / Hybrid Share</div>
        <div className="value">{kpis.ev_hybrid_share_pct}%</div>
      </div>
    </div>
  );
}

export default KpiCards;