import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAnalysis } from './hooks/useAnalysis';
import LoadingState from './components/LoadingState';
import ResultPanel from './components/ResultPanel';
import HistoryPanel from './components/HistoryPanel';

function App() {
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const { isLoading, result, error, analyze, reset, setResult } = useAnalysis();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim() || !body.trim()) return;
    
    try {
      await analyze(title, body);
    } catch (err) {
      console.error('Analysis failed:', err);
    }
  };

  const handleReset = () => {
    setTitle('');
    setBody('');
    reset();
  };

  const handleHistorySelect = (historyResult) => {
    setResult(historyResult);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-12 max-w-5xl">
        {/* Hero Section */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
            OpenIssue AI
          </h1>
          <p className="mt-4 text-lg text-gray-400">
            Automate issue triage in seconds
          </p>
        </motion.header>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Panel */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 shadow-2xl"
            >
              {/* Input Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-400 mb-2">
                    Issue Title
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="e.g., Application crashes on startup"
                    disabled={isLoading}
                    className="w-full px-4 py-3 rounded-lg bg-gray-900/50 border border-gray-700/50 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all disabled:opacity-50"
                  />
                </div>

                <div>
                  <label htmlFor="body" className="block text-sm font-medium text-gray-400 mb-2">
                    Issue Body
                  </label>
                  <textarea
                    id="body"
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    placeholder="Describe the issue in detail. Include error messages, steps to reproduce, expected behavior, etc."
                    rows={6}
                    disabled={isLoading}
                    className="w-full px-4 py-3 rounded-lg bg-gray-900/50 border border-gray-700/50 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all resize-none disabled:opacity-50"
                  />
                </div>

                <div className="flex gap-3">
                  <motion.button
                    type="submit"
                    disabled={isLoading || !title.trim() || !body.trim()}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 px-6 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-medium shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-purple-500/20"
                  >
                    {isLoading ? 'Analyzing...' : 'Analyze Issue'}
                  </motion.button>

                  {result && (
                    <motion.button
                      type="button"
                      onClick={handleReset}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="px-4 py-3 rounded-lg border border-gray-600/50 text-gray-400 hover:text-white hover:border-gray-500/50 transition-all"
                    >
                      Reset
                    </motion.button>
                  )}
                </div>
              </form>

              {/* Error Message */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-4 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Loading State */}
              <AnimatePresence>
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <LoadingState />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Results */}
              <AnimatePresence>
                {result && !isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="mt-8 pt-6 border-t border-gray-700/50"
                  >
                    <ResultPanel result={result} />
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* History Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-1"
          >
            <div className="backdrop-blur-xl bg-white/5 rounded-2xl border border-white/10 p-6 sticky top-6">
              <h2 className="text-lg font-medium text-gray-300 mb-4 flex items-center gap-2">
                <span>📋</span> Recent Analyses
              </h2>
              <HistoryPanel onSelectItem={handleHistorySelect} />
            </div>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-16 text-center text-sm text-gray-600"
        >
          <p>Powered by sentence-transformers + FAISS • Built with ❤️</p>
        </motion.footer>
      </div>
    </div>
  );
}

export default App;
