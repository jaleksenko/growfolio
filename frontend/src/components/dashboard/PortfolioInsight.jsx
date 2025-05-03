// src/components/dashboard/PortfolioInsight.jsx
import { useContext, useMemo } from "react";
import { PortfolioContext } from "../../context/PortfolioContext";

const PortfolioInsight = () => {
  const { portfolio } = useContext(PortfolioContext);

  const summary = useMemo(() => {
    if (!portfolio || portfolio.length === 0) return null;

    const grouped = {};
    portfolio.forEach((item) => {
      const type = item.type || "Other";
      grouped[type] = (grouped[type] || 0) + item.sum;
    });

    const total = Object.values(grouped).reduce((a, b) => a + b, 0);
    const sorted = Object.entries(grouped).sort((a, b) => b[1] - a[1]);

    const primary = sorted[0];
    const topAssets = portfolio
      .sort((a, b) => b.sum - a.sum)
      .slice(0, 2)
      .map((a) => a.symbol);

    const suggestions = [];
    if (sorted.length < 3) {
      suggestions.push("Your portfolio is focused. Consider exploring other asset classes.");
    }
    if (primary[1] / total > 0.7) {
      suggestions.push("Most of your value is concentrated. Adding balance may reduce risk.");
    }

    return {
      topType: primary[0],
      topPercent: Math.round((primary[1] / total) * 100),
      topAssets,
      suggestions,
    };
  }, [portfolio]);

  if (!summary) return null;

  return (
    <div className="portfolio-insight">
      <div className="portfolio-insight__block">
        <p>Your portfolio is {summary.topPercent}% concentrated in {summary.topType.toLowerCase()}.</p>
        <p>Main holdings include {summary.topAssets.join(" and ")}.</p>
      </div>

      <div className="portfolio-insight__divider" />

      <div className="portfolio-insight__block">
        {summary.suggestions.map((text, idx) => (
          <p key={idx}>{text}</p>
        ))}
      </div>

      <div className="portfolio-insight__footer">
        This is a general overview and not a financial recommendation.
      </div>
    </div>
  );
};

export default PortfolioInsight;

