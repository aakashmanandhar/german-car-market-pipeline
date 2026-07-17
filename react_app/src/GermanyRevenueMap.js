import { useState, useEffect } from 'react';
import axios from 'axios';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';

const GERMAN_TO_ENGLISH = {
  "Bayern": "Bavaria",
  "Hessen": "Hesse",
  "Niedersachsen": "Lower Saxony",
  "Nordrhein-Westfalen": "North Rhine-Westphalia",
  "Rheinland-Pfalz": "Rhineland-Palatinate",
  "Sachsen-Anhalt": "Saxony-Anhalt",
  "Sachsen": "Saxony",
  "Thüringen": "Thuringia",
};

function GermanyRevenueMap() {
  const [regionData, setRegionData] = useState({});
  const [maxRevenue, setMaxRevenue] = useState(0);

  useEffect(() => {
    axios.get('http://localhost:8000/api/revenue-by-region/')
      .then(response => {
        const dataByRegion = {};
        let max = 0;
        response.data.forEach(row => {
          dataByRegion[row.region_name] = row;
          if (row.total_revenue > max) max = row.total_revenue;
        });
        setRegionData(dataByRegion);
        console.log("Region names from API:", Object.keys(dataByRegion));
        setMaxRevenue(max);
      })
      .catch(error => console.error('Error fetching revenue by region:', error));
  }, []);

  const colorScale = scaleLinear()
    .domain([0, maxRevenue])
    .range(['#DCEBFF', '#0B4A8F']);

  return (
    <div style={{ width: '100%', maxWidth: 500, margin: '0 auto' }}>
      <h2>Revenue by Bundesland</h2>
      <ComposableMap projection="geoMercator" projectionConfig={{ center: [10.4, 51.2], scale: 2000 }}>
        <Geographies geography="/germany-states.json">
          {({ geographies }) =>
            geographies.map(geo => {
              const englishName = GERMAN_TO_ENGLISH[geo.properties.name] || geo.properties.name;
              const region = regionData[englishName];
              const fillColor = region ? colorScale(region.total_revenue) : '#EEE';
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={fillColor}
                  stroke="#FFF"
                  strokeWidth={0.5}
                  title={region ? `${englishName}: €${region.total_revenue.toLocaleString()}` : geo.properties.name}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>
    </div>
  );
}

export default GermanyRevenueMap;