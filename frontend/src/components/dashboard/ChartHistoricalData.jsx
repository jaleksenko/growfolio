// frontend/src/components/dashboard/ChartHistoricalData.jsx
import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';

function ChartHistoricalData({ symbol, interval = "1day", outputSize = 200 }) {
  const chartContainerRef = useRef(null);
  const chart = useRef(null);
  const series = useRef(null);
  const [error, setError] = useState(null);

  const API_KEY = import.meta.env.VITE_TWELVEDATA_API_KEY;
  const API_URL = import.meta.env.VITE_TWELVEDATA_API_URL;

  useEffect(() => {
    if (!symbol || !API_KEY || !API_URL) return;

    setError(null); // reset error on symbol change

    // Cleanup any previous chart
    chart.current?.remove();

    // Create chart
    chart.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        backgroundColor: '#ffffff',
        textColor: '#000',
      },
      grid: {
        vertLines: { color: '#e0e0e0' },
        horzLines: { color: '#e0e0e0' },
      },
      timeScale: {
        borderColor: '#485c7b',
        timeVisible: true,
      },
    });

    series.current = chart.current.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    chart.current.timeScale().fitContent();

    // Fetch chart data
    const url = `${API_URL}/time_series?symbol=${symbol}&interval=${interval}&outputsize=${outputSize}&apikey=${API_KEY}`;

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (data?.status === "error") {
          setError(data.message || "Unable to load chart data.");
          return;
        }

        if (!data?.values) {
          setError("No chart data available.");
          return;
        }

        const candles = data.values.map(item => ({
          time: Math.floor(new Date(item.datetime).getTime() / 1000),
          open: parseFloat(item.open),
          high: parseFloat(item.high),
          low: parseFloat(item.low),
          close: parseFloat(item.close),
        })).reverse();

        series.current.setData(candles);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setError("Error fetching chart data.");
      });

    return () => {
      chart.current?.remove();
    };
  }, [symbol, interval, outputSize]);

  return (
    <div style={{ width: '100%', height: '400px', position: 'relative' }}>
      {error ? (
        <div className="chart-panel__error">{error}</div>
      ) : (
        <div style={{ width: '100%', height: '100%' }} ref={chartContainerRef} />
      )}
    </div>
  );
}

export default ChartHistoricalData;
