import { useContext, useEffect } from "react";
import { Link } from "react-router-dom";
import { PortfolioContext } from "../context/PortfolioContext";
import { WatchlistContext } from "../context/WatchlistContext";

import Portfolio from "../components/dashboard/Portfolio";
import AssetPieChart from "../components/dashboard/AssetPieChart";
import PortfolioInsight from "../components/dashboard/PortfolioInsight";

const Dashboard = () => {
  const { isReady: portfolioReady } = useContext(PortfolioContext);
  const { isReady: watchlistReady, triggerReload } = useContext(WatchlistContext);

  // Trigger watchlist reload once portfolio is ready
  useEffect(() => {
    if (portfolioReady && !watchlistReady) {
      triggerReload(); // Ensures watchlist gets fetched after dashboard mount
    }
  }, [portfolioReady, watchlistReady, triggerReload]);

  if (!portfolioReady) return null;

  return (
    <div className="dashboard">
      <h2 className="dashboard__title">Dashboard</h2>

      {/* Top row: Charts and Insight */}
      <div className="dashboard__row">
        <div className="dashboard__chart-wrapper" style={{ flex: "0 0 35%" }}>
          <h3 className="dashboard__section-title">Asset Distribution</h3>
          <div className="dashboard__chart-card">
            <div className="dashboard__chart dashboard__chart--left">
              <AssetPieChart />
            </div>
          </div>
        </div>

        <div className="dashboard__chart-wrapper" style={{ flex: "0 0 65%" }}>
          <h3 className="dashboard__section-title">Portfolio Overview</h3>
          <div className="dashboard__chart-card">
            <PortfolioInsight />
          </div>
        </div>
      </div>

      {/* Bottom row: Full-width portfolio block */}
      <div className="dashboard__row">
        <div className="dashboard__card dashboard__card--full">
          <div className="dashboard__portfolio-link">
            <Link to="/portfolio" className="dashboard__portfolio-link-text">
              Portfolio
            </Link>
          </div>
          <Portfolio compact />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
