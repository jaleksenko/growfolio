// frontend/src/components/pages/Watchlist.jsx
import React, { useState, useContext } from "react";
import { WatchlistContext } from "../../context/WatchlistContext";
import { PortfolioContext } from "../../context/PortfolioContext";
import Search from "../Search";
import ChartPanel from "./ChartPanel";
import { LineChart, Plus, Trash } from "lucide-react";

const Watchlist = () => {
  const {
    watchlist,
    removeFromWatchlist,
    isReady: watchlistReady,
  } = useContext(WatchlistContext);

  const {
    addToPortfolio,
    triggerReload: reloadPortfolio,
    isReady: portfolioReady,
  } = useContext(PortfolioContext);

  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [showModal, setShowModal] = useState(false);

  const isReady = watchlistReady && portfolioReady;
  if (!isReady) return null;

  const grouped = watchlist.reduce((acc, asset) => {
    const typeMap = {
      stock: "Stocks",
      etf: "Etfs",
      index: "Indices",
      cryptocurrency: "Cryptocurrencies",
    };
    const key = asset.asset_type?.toLowerCase();
    const group = typeMap[key] || "Other";

    acc[group] = acc[group] || [];
    acc[group].push(asset);
    return acc;
  }, {});

  const openAddModal = (asset) => {
    setSelectedAsset(asset);
    setQuantity(1);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedAsset(null);
    setQuantity(1);
  };

  const handleConfirm = async () => {
    if (!selectedAsset || quantity <= 0) return;

    try {
      await addToPortfolio({
        id: selectedAsset.asset_id,
        asset_type: selectedAsset.asset_type,
        quantity: Number(quantity),
      });
      await reloadPortfolio();
      await removeFromWatchlist(selectedAsset.asset_id, selectedAsset.asset_type);
    } catch (err) {
      console.error("Error adding to portfolio:", err);
    } finally {
      closeModal();
    }
  };

  const handleRemove = (id, type, symbol) => {
    removeFromWatchlist(id, type);
    if (symbol === selectedSymbol) setSelectedSymbol(null);
  };

  return (
    <div className="watchlist">
      <h2 className="watchlist__title">Watchlist</h2>

      <div className="watchlist__search">
        <Search mode="watchlist" />
      </div>

      {selectedSymbol && (
        <div className="watchlist__chart-container">
          <ChartPanel symbol={selectedSymbol} onClose={() => setSelectedSymbol(null)} />
        </div>
      )}

      {Object.keys(grouped).length === 0 ? (
        <p className="watchlist__empty">Your watchlist is empty.</p>
      ) : (
        Object.entries(grouped).map(([group, items]) => (
          <div key={group} className="watchlist__group">
            <h3>{group}</h3>
            <table className="watchlist__table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Exchange</th>
                  <th className="watchlist__actions-header">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.symbol}>
                    <td>{item.symbol}</td>
                    <td>
                      {item.name && item.name !== "N/A"
                        ? item.name
                        : item.currency_base && item.currency_quote
                        ? `${item.currency_base} / ${item.currency_quote}`
                        : "Unknown"}
                    </td>
                    <td>{item.exchange || "N/A"}</td>
                    <td className="watchlist__table-actions">
                      <button
                        className="watchlist__button watchlist__button--icon"
                        title="View Chart"
                        onClick={() => setSelectedSymbol(item.symbol)}
                      >
                        <LineChart size={18} />
                      </button>
                      <button
                        className="watchlist__button watchlist__button--icon watchlist__button--portfolio"
                        title="Add to Portfolio"
                        onClick={() => openAddModal(item)}
                      >
                        <Plus size={18} />
                      </button>
                      <button
                        className="watchlist__button watchlist__button--icon watchlist__button--remove"
                        title="Remove from Watchlist"
                        onClick={() =>
                          handleRemove(item.asset_id, item.asset_type, item.symbol)
                        }
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

      {showModal && selectedAsset && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Add to Portfolio</h3>
            <p>{selectedAsset.symbol}</p>
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

export default Watchlist;
