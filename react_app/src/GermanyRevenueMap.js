import { useState, useEffect } from 'react';
import axios from 'axios';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import * as d3 from 'd3-geo';

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

function GermanyRevenueMap({ selectedRegion, onSelectRegion, theme = 'dark' }) {
  const [regionData, setRegionData] = useState({});
  const [maxRevenue, setMaxRevenue] = useState(0);
  const [geoFeatures, setGeoFeatures] = useState([]);
  const [center, setCenter] = useState([10.4, 51.2]);
  const [zoom, setZoom] = useState(1);

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
        setMaxRevenue(max);
      })
      .catch(error => console.error('Error fetching revenue by region:', error));
  }, []);

  useEffect(() => {
    if (!selectedRegion || geoFeatures.length === 0) {
      setCenter([10.4, 51.2]);
      setZoom(1);
      return;
    }
    const feature = geoFeatures.find(
      geo => (GERMAN_TO_ENGLISH[geo.properties.name] || geo.properties.name) === selectedRegion
    );
    if (feature) {
      const centroid = d3.geoCentroid(feature);
      setCenter(centroid);
      setZoom(3);
    }
  }, [selectedRegion, geoFeatures]);

  const colorScale = scaleLinear().domain([0, maxRevenue]).range(['#1B2233', '#4C8DFF']);

  return (
    <div style={{ width: '100%', maxWidth: 500, margin: '0 auto' }}>
      <ComposableMap projection="geoMercator" projectionConfig={{ center: [10.4, 51.2], scale: 2000 }}>
        <ZoomableGroup center={center} zoom={zoom} minZoom={1} maxZoom={6}>
          <Geographies geography="/germany-states.json">
            {({ geographies }) => {
              if (geoFeatures.length === 0) setGeoFeatures(geographies);
              return geographies.map(geo => {
                const englishName = GERMAN_TO_ENGLISH[geo.properties.name] || geo.properties.name;
                const region = regionData[englishName];
                const isSelected = selectedRegion === englishName;
                const isDimmed = selectedRegion && !isSelected;
                const emptyFill = theme === 'light' ? '#E2E4E9' : '#232B3D';
                const fillColor = region ? colorScale(region.total_revenue) : emptyFill;

                return (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    onClick={() => onSelectRegion(isSelected ? null : englishName)}
                    fill={fillColor}
                    stroke={isSelected ? '#22D3EE' : '#0F1420'}
                    strokeWidth={isSelected ? 2 : 0.75}
                    opacity={isDimmed ? 0.35 : 1}
                    title={region ? `${englishName}: €${region.total_revenue.toLocaleString()}` : englishName}
                    style={{
                      default: { outline: 'none' },
                      hover: { outline: 'none', fill: '#22D3EE', cursor: 'pointer' },
                      pressed: { outline: 'none' },
                    }}
                  />
                );
              });
            }}
          </Geographies>
        </ZoomableGroup>
      </ComposableMap>
    </div>
  );
}

export default GermanyRevenueMap;