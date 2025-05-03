import React from 'react';
import { VscGraphLine, VscPieChart, VscRocket } from 'react-icons/vsc';

const HomePage = () => {
  return (
    <div className="home-page">
      <div className="container">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <h1 className="hero-title">Manage Your Financial Future</h1>
            <p className="hero-subtitle">
              Get real-time insights on financial assets and make informed decisions to grow your wealth.
            </p>
          </div>
        </section>

        {/* Info Cards */}
        <section className="info-cards">
          <div className="card">
            <VscGraphLine className="card-icon" />
            <h2>Real-Time Data</h2>
            <p>
              Access the latest data on stocks, bonds, cryptocurrencies, and more to stay informed and make quick decisions.
            </p>
          </div>
          <div className="card">
            <VscPieChart className="card-icon" />
            <h2>Portfolio Management</h2>
            <p>
              Track and manage your portfolio with intuitive tools and personalized insights.
            </p>
          </div>
          <div className="card">
            <VscRocket className="card-icon" />
            <h2>Financial Insights</h2>
            <p>
              Receive expert insights and analysis tailored to your financial goals.
            </p>
          </div>
        </section>

        {/* Features */}
        <section className="features">
          <div className="feature">
            <h3>Customizable Dashboard</h3>
            <p>
              Growfolio is built to adapt to you. Add or remove asset blocks, change layouts, group by category or performance.
              Whether you want a clean overview or deep technical layers, your dashboard remains focused and distraction-free.
            </p>
          </div>
          <div className="feature">
            <h3>Alerts & Notifications</h3>
            <p>
              Stay updated with silent precision. Configure smart alerts based on price movement, portfolio weight shifts, or asset
              class changes. Growfolio will notify you only when your attention is truly needed — no spam, no clutter.
            </p>
          </div>
          <div className="feature">
            <h3>Advanced Analytics</h3>
            <p>
              Gain clarity with purpose-built visualizations. Compare historical patterns, spot volatility zones, and understand the
              true impact of your decisions over time. Built-in summaries surface key takeaways without data overwhelm.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HomePage;
