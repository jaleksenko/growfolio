// frontend/src/components/dashboard/ChartPanel.jsx
import React, { useState } from "react";
import ChartHistoricalData from "./ChartHistoricalData";

const INTERVAL_OPTIONS = [
  { label: "1m", value: "1min" },
  { label: "5m", value: "5min" },
  { label: "15m", value: "15min" },
  { label: "30m", value: "30min" },
  { label: "1H", value: "1h" },
  { label: "4H", value: "4h" },
  { label: "1D", value: "1day" },
  { label: "1W", value: "1week" },
  { label: "1M", value: "1month" },
];

function ChartPanel({ symbol, onClose }) {
  const [interval, setInterval] = useState("1week");

  if (!symbol) return null;

  return (
    <div className="chart-panel">
      <div className="chart-panel__controls">
        <span className="chart-panel__symbol">{symbol.toLowerCase()}</span>

        <div className="chart-panel__intervals">
          {INTERVAL_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setInterval(option.value)}
              className={`chart-panel__interval-link ${
                interval === option.value ? "active" : ""
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>

        <button
          onClick={onClose}
          className="chart-panel__close"
          title="Close panel"
        >
          &times;
        </button>
      </div>

      <ChartHistoricalData
        key={`${symbol}-${interval}`}
        symbol={symbol}
        interval={interval}
        outputSize={250}
      />
    </div>
  );
}

export default ChartPanel;
