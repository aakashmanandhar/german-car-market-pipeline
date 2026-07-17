import { useState } from 'react';
import './App.css';
import BrandMarketShareChart from './BrandMarketShareChart';
import GermanyRevenueMap from './GermanyRevenueMap';
import KpiCards from './KpiCards';
import FinancingChart from './FinancingChart';
import ChannelShiftChart from './ChannelShiftChart';
import RegionSelector from './RegionSelector';
import FuelTypeTrendChart from './FuelTypeTrendChart';
import PriceTrendChart from './PriceTrendChart';
import NewVsUsedChart from './NewVsUsedChart';
import ChatPanel from './ChatPanel';

function App() {
  const [selectedRegion, setSelectedRegion] = useState(null);
  const [theme, setTheme] = useState('dark');

  return (
    <div className={`dashboard ${theme}`}>
      <div className="dashboard-inner">
        <div className="topbar">
          <h1>German Car Market — Overview</h1>
          <div className="sub">1990 – 2026 · live from BigQuery</div>
        </div>

        <div className="filter-bar">
          <span className="label">Filter by region</span>
          <RegionSelector selectedRegion={selectedRegion} onChange={setSelectedRegion} />
          <button className="theme-toggle" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>
            {theme === 'dark' ? '☀ Light mode' : '🌙 Dark mode'}
          </button>
        </div>

        <div className="layout">
          <div>
            <KpiCards selectedRegion={selectedRegion} />

            <div className="grid-2">
              <div className="panel">
                <h2>Revenue — {selectedRegion || 'All Germany'}</h2>
                <GermanyRevenueMap selectedRegion={selectedRegion} onSelectRegion={setSelectedRegion} theme={theme} />
              </div>
              <div className="panel">
                <h2>Brand Market Share, 1990–2026</h2>
                <BrandMarketShareChart selectedRegion={selectedRegion} theme={theme} />
              </div>
            </div>

            <div className="panel">
              <h2>Fuel Type Adoption, 1990–2026</h2>
              <FuelTypeTrendChart selectedRegion={selectedRegion} theme={theme} />
            </div>

            <div className="grid-charts">
              <div className="panel">
                <h2>Average Price Trend</h2>
                <PriceTrendChart selectedRegion={selectedRegion} theme={theme} />
              </div>
              <div className="panel">
                <h2>New vs. Used</h2>
                <NewVsUsedChart selectedRegion={selectedRegion} theme={theme} />
              </div>
            </div>

            <div className="grid-charts">
              <div className="panel">
                <h2>Revenue by Financing Type</h2>
                <FinancingChart selectedRegion={selectedRegion} theme={theme} />
              </div>
              <div className="panel">
                <h2>Sales Channel Shift</h2>
                <ChannelShiftChart selectedRegion={selectedRegion} theme={theme} />
              </div>
            </div>
          </div>

          <div className="chat-sticky">
            <ChatPanel theme={theme} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;