import { motion } from 'framer-motion';

const typeConfig = {
  bug: { 
    label: '🐛 Bug', 
    bg: 'bg-red-500/20', 
    border: 'border-red-500/50',
    text: 'text-red-400'
  },
  feature: { 
    label: '✨ Feature', 
    bg: 'bg-purple-500/20', 
    border: 'border-purple-500/50',
    text: 'text-purple-400'
  },
  question: { 
    label: '❓ Question', 
    bg: 'bg-blue-500/20', 
    border: 'border-blue-500/50',
    text: 'text-blue-400'
  },
};

const priorityConfig = {
  critical: { 
    label: '🔴 Critical', 
    bg: 'bg-red-600/20', 
    border: 'border-red-600/50',
    text: 'text-red-500'
  },
  high: { 
    label: '🟠 High', 
    bg: 'bg-orange-500/20', 
    border: 'border-orange-500/50',
    text: 'text-orange-400'
  },
  medium: { 
    label: '🟡 Medium', 
    bg: 'bg-yellow-500/20', 
    border: 'border-yellow-500/50',
    text: 'text-yellow-400'
  },
  low: { 
    label: '🟢 Low', 
    bg: 'bg-green-500/20', 
    border: 'border-green-500/50',
    text: 'text-green-400'
  },
};

function Badge({ config }) {
  return (
    <span className={`px-3 py-1.5 rounded-full text-sm font-medium border ${config.bg} ${config.border} ${config.text}`}>
      {config.label}
    </span>
  );
}

function ConfidenceBar({ confidence }) {
  return (
    <div className="w-full">
      <div className="flex justify-between mb-1">
        <span className="text-sm text-gray-400">Confidence</span>
        <span className="text-sm font-medium text-gray-300">{Math.round(confidence * 100)}%</span>
      </div>
      <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-purple-500 to-cyan-400 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${confidence * 100}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

function SimilarIssueCard({ issue, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 * index }}
      className="p-3 rounded-lg bg-gray-800/50 border border-gray-700/50 hover:border-gray-600/50 transition-colors"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-cyan-400">#{issue.id}</span>
            <span className={`text-xs px-1.5 py-0.5 rounded ${typeConfig[issue.type]?.bg || 'bg-gray-600/50'} ${typeConfig[issue.type]?.text || 'text-gray-400'}`}>
              {issue.type}
            </span>
          </div>
          <p className="mt-1 text-sm text-gray-300 truncate">{issue.title}</p>
        </div>
        <div className="flex-shrink-0">
          <span className="text-sm font-medium text-green-400">
            {Math.round(issue.similarity * 100)}%
          </span>
        </div>
      </div>
    </motion.div>
  );
}

function ExplanationList({ explanations }) {
  return (
    <ul className="space-y-2">
      {explanations.map((item, index) => (
        <motion.li
          key={index}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 * index }}
          className="flex items-start gap-2 text-sm text-gray-300"
        >
          <span className="text-cyan-400 mt-0.5">•</span>
          <span dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>') }} />
        </motion.li>
      ))}
    </ul>
  );
}

function SuggestedReply({ reply }) {
  const copyToClipboard = () => {
    navigator.clipboard.writeText(reply);
  };

  return (
    <div className="relative">
      <pre className="p-4 rounded-lg bg-gray-900/80 border border-gray-700/50 text-sm text-gray-300 whitespace-pre-wrap font-mono overflow-x-auto">
        {reply}
      </pre>
      <button
        onClick={copyToClipboard}
        className="absolute top-2 right-2 px-2 py-1 text-xs rounded bg-gray-700/50 hover:bg-gray-600/50 text-gray-400 hover:text-white transition-colors"
      >
        Copy
      </button>
    </div>
  );
}

export default function ResultPanel({ result }) {
  const type = typeConfig[result.type] || typeConfig.question;
  const priority = priorityConfig[result.priority] || priorityConfig.medium;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header with badges */}
      <div className="flex flex-wrap gap-3 items-center">
        <Badge config={type} />
        <Badge config={priority} />
      </div>

      {/* Confidence bar */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <ConfidenceBar confidence={result.confidence} />
      </motion.div>

      {/* Similar Issues */}
      {result.similar_issues && result.similar_issues.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
            <span>🔁</span> Similar Issues
          </h3>
          <div className="space-y-2">
            {result.similar_issues.map((issue, index) => (
              <SimilarIssueCard key={issue.id} issue={issue} index={index} />
            ))}
          </div>
        </motion.div>
      )}

      {/* Explanation */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
          <span>🧠</span> Analysis Reasoning
        </h3>
        <ExplanationList explanations={result.explanation} />
      </motion.div>

      {/* Suggested Reply */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <h3 className="text-sm font-medium text-gray-400 mb-3 flex items-center gap-2">
          <span>💬</span> Suggested GitHub Reply
        </h3>
        <SuggestedReply reply={result.suggested_reply} />
      </motion.div>
    </motion.div>
  );
}
