import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';
import { getHistory, getHistoryItem } from '../api';

const typeColors = {
  bug: 'text-red-400',
  feature: 'text-purple-400',
  question: 'text-blue-400',
};

const priorityColors = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-green-500',
};

export default function HistoryPanel({ onSelectItem }) {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await getHistory(5);
      setHistory(data.history || []);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = async (item) => {
    try {
      const fullItem = await getHistoryItem(item.id);
      if (fullItem && fullItem.result) {
        onSelectItem(fullItem.result);
      }
    } catch (err) {
      console.error('Failed to load history item:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-4 text-gray-500 text-sm">
        Loading history...
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500 text-sm">
        No previous analyses yet
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {history.map((item, index) => (
        <motion.button
          key={item.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
          onClick={() => handleSelect(item)}
          className="w-full text-left p-3 rounded-lg bg-gray-800/30 border border-gray-700/30 hover:bg-gray-800/50 hover:border-gray-600/50 transition-all group"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-300 truncate group-hover:text-white transition-colors">
                {item.title}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs ${typeColors[item.type] || 'text-gray-400'}`}>
                  {item.type}
                </span>
                <span className={`w-2 h-2 rounded-full ${priorityColors[item.priority] || 'bg-gray-500'}`} />
                <span className="text-xs text-gray-500">
                  {Math.round(item.confidence * 100)}%
                </span>
              </div>
            </div>
            <span className="text-gray-600 group-hover:text-gray-400 transition-colors">
              →
            </span>
          </div>
        </motion.button>
      ))}
    </div>
  );
}
