import { motion } from 'framer-motion';

export default function LoadingState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16"
    >
      {/* Animated rings */}
      <div className="relative w-20 h-20">
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-purple-500/30"
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.1, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
        <motion.div
          className="absolute inset-2 rounded-full border-2 border-cyan-400/40"
          animate={{ scale: [1, 1.15, 1], opacity: [0.4, 0.2, 0.4] }}
          transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
        />
        <motion.div
          className="absolute inset-4 rounded-full border-2 border-purple-400/50"
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.3, 0.5] }}
          transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
        />
        
        {/* Center spinner */}
        <motion.div
          className="absolute inset-6 rounded-full bg-gradient-to-br from-purple-500 to-cyan-400"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
        />
      </div>

      <motion.p
        className="mt-6 text-lg font-medium text-gray-300"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        Analyzing with AI…
      </motion.p>
      
      <motion.p
        className="mt-2 text-sm text-gray-500"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        Running semantic analysis and similarity search
      </motion.p>
    </motion.div>
  );
}
