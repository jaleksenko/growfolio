// frontend/src/components/pages/Portfolio.jsx
import React, { useContext, useState } from "react";
import { PortfolioContext } from "../../context/PortfolioContext";
import Search from "../Search";
import ChartPanel from "./ChartPanel";
import { LineChart, Trash } from "lucide-react";

const Portfolio = ({ compact = false }) => {
  const {
    portfolio,
    addToPortfolio,
    removeFromPortfolio,
    isReady,
    triggerReload,
  } = useContext(PortfolioContext);

  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [modalAsset, setModalAsset] = useState(null);
  const [quantity, setQuantity] = useState(1);

  if (!isReady) return null;

  const handleSearchSelect = (asset) => {
    const id = asset.asset_id || asset.id;
    const asset_type = asset.asset_type || asset.group || asset.type;

    setModalAsset({ ...asset, asset_id: id, asset_type });
    setQuantity(1);
  };

  const handleConfirm = async () => {
    if (!modalAsset || quantity <= 0) return;

    try {
      await addToPortfolio({
        id: modalAsset.asset_id,
        asset_type: modalAsset.asset_type,
        quantity: Number(quantity),
      });

      await triggerReload();
      closeModal();
    } catch (err) {
      console.error("Error adding to portfolio:", err);
    }
  };

  const handleRemove = (asset_id, asset_type) => {
    if (!asset_id || !asset_type) return;

    removeFromPortfolio(asset_id, asset_type);

    if (
      selectedSymbol &&
      portfolio.find((a) => a.asset_id === asset_id)?.symbol === selectedSymbol
    ) {
      setSelectedSymbol(null);
    }
  };

  const closeModal = () => {
    setModalAsset(null);
    setQuantity(1);
  };

  const groupedPortfolio = portfolio.reduce((acc, item) => {
    if (!item.type) {
      throw new Error("Missing asset type in portfolio item");
    }

    const typeMap = {
      stock: "Stocks",
      etf: "Etfs",
      index: "Indices",
      cryptocurrency: "Cryptocurrencies",
    };

    const key = item.type.toLowerCase();
    const group = typeMap[key] || "Other";

    acc[group] = acc[group] || [];
    acc[group].push(item);
    return acc;
  }, {});

  return (
    <div className="portfolio">
      {!compact && <h2 className="portfolio__title">Portfolio</h2>}

      {!compact && (
        <div className="portfolio__search">
          <Search onSelect={handleSearchSelect} mode="portfolio" />
        </div>
      )}

      {selectedSymbol && (
        <div className="portfolio__chart-container">
          <ChartPanel symbol={selectedSymbol} onClose={() => setSelectedSymbol(null)} />
        </div>
      )}

      {Object.keys(groupedPortfolio).length === 0 ? (
        <p>Your portfolio is empty.</p>
      ) : (
        Object.entries(groupedPortfolio).map(([group, items]) => (
          <div key={group} className="portfolio__group">
            <h3>{group}</h3>
            <table className="portfolio__table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Exchange</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Sum</th>
                  <th className="portfolio__actions-header">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.asset_id}>
                    <td>{item.symbol}</td>
                    <td>
                      {item.name && item.name !== "N/A"
                        ? item.name
                        : item.currency_base && item.currency_quote
                        ? `${item.currency_base} / ${item.currency_quote}`
                        : "Unknown"}
                    </td>
                    <td>{item.exchange || "N/A"}</td>
                    <td>{item.quantity}</td>
                    <td>{item.price}</td>
                    <td>{item.sum}</td>
                    <td className="portfolio__actions">
                      <button
                        className="portfolio__button portfolio__button--icon"
                        onClick={() => setSelectedSymbol(item.symbol)}
                        title="View Chart"
                      >
                        <LineChart size={18} />
                      </button>
                      <button
                        className="portfolio__button portfolio__button--icon portfolio__button--danger"
                        onClick={() => handleRemove(item.asset_id, item.type)}
                        title="Remove"
                      >
                        <Trash size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))
      )}

      {modalAsset && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add to Portfolio</h3>
            <p>{modalAsset.symbol}</p>
            <input
              type="number"
              value={quantity}
              min="0"
              step="any"
              onChange={(e) => setQuantity(e.target.value)}
              className="modal__input"
              placeholder="Quantity"
            />
            <div className="modal__actions">
              <button onClick={handleConfirm} className="confirm">
                Confirm
              </button>
              <button onClick={closeModal} className="cancel">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Portfolio;
