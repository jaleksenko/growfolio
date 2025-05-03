// frontend/src/context/WatchlistContext.jsx
import React, { createContext, useState, useEffect, useContext } from "react";
import { AuthContext } from "./AuthContext";

export const WatchlistContext = createContext();

export const WatchlistProvider = ({ children }) => {
  const { token, baseUrl } = useContext(AuthContext);

  const [watchlist, setWatchlist] = useState([]);
  const [allAssets, setAllAssets] = useState([]);
  const [assetType, setAssetType] = useState("stocks");
  const [isReady, setIsReady] = useState(false);

  // 🔁 Load user's watchlist
  useEffect(() => {
    if (!token) {
      setIsReady(true);
      return;
    }

    const loadWatchlist = async () => {
      setIsReady(false);
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        };

        // 1. Check token validity
        const resId = await fetch(`${baseUrl}/watchlists/me/`, { headers });
        if (resId.status === 401) {
          console.warn("Unauthorized: watchlist ID");
          return;
        }
        if (!resId.ok) throw new Error("Failed to fetch watchlist ID");

        // 2. Get assets
        const resAssets = await fetch(`${baseUrl}/watchlists/me/assets/`, {
          headers,
        });
        if (!resAssets.ok) throw new Error("Failed to fetch assets");

        const assets = await resAssets.json();
        setWatchlist(assets);
      } catch (err) {
        console.error("Error loading watchlist:", err);
      } finally {
        setIsReady(true);
      }
    };

    loadWatchlist();
  }, [token, baseUrl]);

  // 🔁 Fetch asset list by type
  useEffect(() => {
    if (!token) return;

    const headers = {
      Authorization: `Bearer ${token}`,
    };

    fetch(`${baseUrl}/assets/${assetType}/symbols`, { headers })
      .then((res) => res.json())
      .then((data) => setAllAssets(data))
      .catch((err) => console.error("Error loading asset symbols:", err));
  }, [assetType, baseUrl, token]);

  // ➕ Add asset
  const addToWatchlist = async ({ id, asset_type }) => {
    if (!id || !asset_type || !token) return;

    try {
      const res = await fetch(
        `${baseUrl}/watchlists/me/assets/?asset_id=${id}&asset_type=${asset_type}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) throw new Error("Failed to add asset");

      const added = await res.json();
      setWatchlist((prev) => [...prev, added]);
    } catch (err) {
      console.error("Error adding to watchlist:", err);
    }
  };

  // ❌ Remove asset
  const removeFromWatchlist = async (asset_id, asset_type) => {
    if (!asset_id || !asset_type || !token) return;

    const map = {
      stocks: "Stock",
      etfs: "Etf",
      indices: "Index",
      cryptocurrencies: "Cryptocurrency",
    };

    const normalized = map[asset_type] || asset_type;

    try {
      const res = await fetch(
        `${baseUrl}/watchlists/me/assets/${asset_id}/${normalized}/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) throw new Error("Failed to remove asset");

      setWatchlist((prev) => prev.filter((item) => item.asset_id !== asset_id));
    } catch (err) {
      console.error("Error removing from watchlist:", err);
    }
  };

  return (
    <WatchlistContext.Provider
      value={{
        watchlist,
        allAssets,
        isReady,
        assetType,
        setAssetType,
        addToWatchlist,
        removeFromWatchlist,
      }}
    >
      {children}
    </WatchlistContext.Provider>
  );
};
