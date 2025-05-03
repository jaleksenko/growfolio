import React, { useState, useEffect, useRef, useContext } from 'react';
import { Link } from 'react-router-dom';
import { WatchlistContext } from '../context/WatchlistContext';
import { PortfolioContext } from '../context/PortfolioContext';

const assetTypes = ['stocks', 'etfs', 'indices', 'cryptocurrencies'];

const Search = ({ onSelect, mode = 'watchlist' }) => {
  const context =
    mode === 'portfolio' ? useContext(PortfolioContext) : useContext(WatchlistContext);

  const { allAssets, setAssetType, assetType, addToWatchlist, triggerReload } = context;

  const [searchTerm, setSearchTerm] = useState('');
  const [filteredAssets, setFilteredAssets] = useState([]);
  const searchRef = useRef(null);

  useEffect(() => {
    if (!assetType) setAssetType('stocks');
  }, [assetType, setAssetType]);

  useEffect(() => {
    setSearchTerm('');
    setFilteredAssets([]);
  }, [assetType]);

  useEffect(() => {
    if (!searchTerm || !Array.isArray(allAssets)) return;

    const term = searchTerm.toLowerCase();
    const filtered = allAssets.filter((a) => {
      if (assetType === 'cryptocurrencies') {
        return (
          a.symbol.toLowerCase().includes(term) ||
          `${a.currency_base}/${a.currency_quote}`.toLowerCase().includes(term)
        );
      }
      return (
        a.symbol.toLowerCase().includes(term) ||
        a.name?.toLowerCase().includes(term)
      );
    });

    setFilteredAssets(filtered.slice(0, 10));
  }, [searchTerm, allAssets, assetType]);

  useEffect(() => {
    const handler = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setFilteredAssets([]);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSelect = async (asset) => {
    const id = asset.asset_id || asset.id;
    let type = asset.asset_type || asset.group || asset.type || assetType;

    const map = {
      stocks: 'stock',
      etfs: 'etf',
      indices: 'index',
      cryptocurrencies: 'cryptocurrency',
    };
    type = map[type?.toLowerCase()] || type?.toLowerCase();

    if (!id || !type) return;

    if (mode === 'portfolio') {
      onSelect?.({ ...asset, asset_type: type });
    } else {
      await addToWatchlist({ id, asset_type: type });
      await triggerReload?.();
      onSelect?.(asset);
    }

    setSearchTerm('');
    setFilteredAssets([]);
  };

  return (
    <div className="search" ref={searchRef}>
      <div className="search__tabs">
        {assetTypes.map((type) => (
          <Link
            key={type}
            to="#"
            className={`search__tab ${type === assetType ? 'active' : ''}`}
            onClick={() => {
              setAssetType(type);
              setSearchTerm('');
              setFilteredAssets([]);
            }}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </Link>
        ))}
      </div>

      <input
        type="text"
        className="search__input"
        placeholder={`Search ${assetType}...`}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />

      {filteredAssets.length > 0 && searchTerm && (
        <ul className="search__dropdown">
          {filteredAssets.map((asset) => (
            <li
              key={asset.asset_id || asset.id}
              className="search__dropdown-item"
              onClick={() => handleSelect(asset)}
            >
              <strong>{asset.symbol}</strong> –{' '}
              {assetType === 'cryptocurrencies'
                ? `${asset.currency_base} / ${asset.currency_quote}`
                : asset.name}{' '}
              ({asset.exchange || 'N/A'})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Search;
