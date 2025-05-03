// frontend/src/context/PortfolioContext.jsx
import React, { createContext, useState, useEffect, useContext } from "react";
import { AuthContext } from "./AuthContext";

export const PortfolioContext = createContext();

export const PortfolioProvider = ({ children }) => {
  const { token, baseUrl } = useContext(AuthContext);

  const [portfolio, setPortfolio] = useState([]);
  const [allAssets, setAllAssets] = useState([]);
  const [assetType, setAssetType] = useState("stocks");
  const [isReady, setIsReady] = useState(false);

  // 🔁 Fetch portfolio on load
  useEffect(() => {
    if (!token) {
      setIsReady(true);
      return;
    }

    const fetchPortfolio = async () => {
      setIsReady(false);
      try {
        const headers = {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        };

        const res = await fetch(`${baseUrl}/portfolio/me`, { headers });
        if (!res.ok) throw new Error("Failed to fetch portfolio");

        const data = await res.json();
        setPortfolio(data);
      } catch (err) {
        console.error("Error loading portfolio:", err);
      } finally {
        setIsReady(true);
      }
    };

    fetchPortfolio();
  }, [token, baseUrl]);

  // 🔁 Fetch all tradable assets
  useEffect(() => {
    if (!token) return;

    const headers = { Authorization: `Bearer ${token}` };

    fetch(`${baseUrl}/assets/${assetType}/symbols`, { headers })
      .then((res) => res.json())
      .then((data) => setAllAssets(data))
      .catch((err) => console.error("Error loading asset symbols:", err));
  }, [assetType, baseUrl, token]);

  // 🔄 Trigger full reload
  const triggerReload = () => {
    if (!token) return;
    setIsReady(false);

    fetch(`${baseUrl}/portfolio/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    })
      .then((res) => res.json())
      .then((data) => setPortfolio(data))
      .catch((err) => console.error("Error reloading portfolio:", err))
      .finally(() => setIsReady(true));
  };

  // ➕ Add asset
  const addToPortfolio = async ({ id, asset_type, quantity }) => {
    if (!id || !asset_type || !quantity || !token) return;

    try {
      const res = await fetch(
        `${baseUrl}/portfolio/me/assets/?asset_id=${id}&asset_type=${asset_type}&quantity=${quantity}`,
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

      setPortfolio((prev) => {
        const exists = prev.find((a) => a.asset_id === added.asset_id);
        return exists ? prev : [...prev, added];
      });
    } catch (err) {
      console.error("Error adding to portfolio:", err);
    }
  };

  // ❌ Remove asset
  const removeFromPortfolio = async (asset_id, asset_type) => {
    if (!asset_id || !asset_type || !token) return;

    try {
      const res = await fetch(
        `${baseUrl}/portfolio/me/assets/${asset_id}/${asset_type}/`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (!res.ok) throw new Error("Failed to remove asset");

      setPortfolio((prev) => prev.filter((a) => a.asset_id !== asset_id));
    } catch (err) {
      console.error("Error removing from portfolio:", err);
    }
  };

  return (
    <PortfolioContext.Provider
      value={{
        portfolio,
        allAssets,
        assetType,
        setAssetType,
        isReady,
        triggerReload,
        addToPortfolio,
        removeFromPortfolio,
      }}
    >
      {children}
    </PortfolioContext.Provider>
  );
};
