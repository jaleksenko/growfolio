// src/components/dashboard/AssetPieChart.jsx

import { useContext, useMemo } from "react";
import { PortfolioContext } from "../../context/PortfolioContext";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Label,
} from "recharts";

const COLORS = ["#4caf50", "#007aff", "#ffb347", "#b39ddb", "#4dd0e1"];
const RADIAN = Math.PI / 180;

// Outer percentage labels with pointer lines
const renderPercentLabel = ({ cx, cy, midAngle, outerRadius, percent }) => {
  const radius = outerRadius + 10;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return percent > 0.05 ? (
    <text
      x={x}
      y={y}
      fill="#1c1c1e"
      textAnchor={x > cx ? "start" : "end"}
      dominantBaseline="central"
      fontSize={13}
    >
      {(percent * 100).toFixed(0)}%
    </text>
  ) : null;
};

const AssetPieChart = () => {
  const { portfolio } = useContext(PortfolioContext);

  const data = useMemo(() => {
    const grouped = {};
    portfolio.forEach((item) => {
      const type = item.type || "Other";
      grouped[type] = (grouped[type] || 0) + item.sum;
    });
    return Object.entries(grouped).map(([name, value]) => ({
      name,
      value: Math.round(value),
    }));
  }, [portfolio]);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  if (data.length === 0) {
    return <p style={{ textAlign: "center", width: "100%" }}>No data</p>;
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius="55%"
          outerRadius="75%"
          dataKey="value"
          startAngle={90}
          endAngle={-270}
          paddingAngle={1}
          cornerRadius={4}
          labelLine
          label={renderPercentLabel}
          isAnimationActive
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={COLORS[index % COLORS.length]}
            />
          ))}

          {/* 💡 Centered total label */}
          <Label
            value={`$${total.toLocaleString()}`}
            position="center"
            style={{
              fontSize: "18px",
              fontWeight: 400,
              fill: "#1c1c1e",
            }}
          />
        </Pie>

        <Tooltip
          formatter={(value, name) => [`$${value}`, name]}
          contentStyle={{
            borderRadius: "12px",
            boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
            fontSize: "14px",
            padding: "8px 12px",
          }}
        />

        <Legend
          verticalAlign="bottom"
          height={36}
          iconSize={10}
          iconType="square"
          formatter={(value) => (
            <span style={{ color: "#1c1c1e", fontSize: 13 }}>{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default AssetPieChart;
