const REGIONS = [
  "Bavaria", "North Rhine-Westphalia", "Baden-Württemberg", "Lower Saxony",
  "Hesse", "Saxony", "Rhineland-Palatinate", "Berlin", "Schleswig-Holstein",
  "Brandenburg", "Saxony-Anhalt", "Thuringia", "Hamburg", "Mecklenburg-Vorpommern",
  "Saarland", "Bremen"
];

function RegionSelector({ selectedRegion, onChange }) {
  return (
    <select
      className="region-select"
      value={selectedRegion || ""}
      onChange={(e) => onChange(e.target.value || null)}
    >
      <option value="">All Germany</option>
      {REGIONS.map(region => (
        <option key={region} value={region}>{region}</option>
      ))}
    </select>
  );
}

export default RegionSelector;