import { useState, useEffect } from 'react';
import axios from 'axios';

function KpiCards() {
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/kpi-summary/')
      .then(response => setKpis(response.data))
      .catch(error => console.error('Error fetching KPIs:', error));
  }, []);

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
    <div style={{ display: 'flex', gap: '16px', padding: '20px', maxWidth: 1000, margin: '0 auto' }}>
      <div style={cardStyle}>
        <div style={labelStyle}>Total Revenue</div>
        <div style={valueStyle}>€{(kpis.total_revenue / 1_000_000_000).toFixed(2)}B</div>
      </div>
      <div style={cardStyle}>
        <div style={labelStyle}>Avg Net Price</div>
        <div style={valueStyle}>€{kpis.avg_net_price.toLocaleString()}</div>
      </div>
      <div style={cardStyle}>
        <div style={labelStyle}>Total Purchases</div>
        <div style={valueStyle}>{kpis.total_purchases.toLocaleString()}</div>
      </div>
      <div style={cardStyle}>
        <div style={labelStyle}>EV / Hybrid Share</div>
        <div style={valueStyle}>{kpis.ev_hybrid_share_pct}%</div>
      </div>
    </div>
  );
}

export default KpiCards;