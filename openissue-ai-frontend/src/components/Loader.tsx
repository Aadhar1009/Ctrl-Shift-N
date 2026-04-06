import { motion } from 'framer-motion';

export function Loader() {
  return (
    <div className="flex flex-col items-center justify-center gap-6">
      <div className="relative flex h-12 w-12 items-center justify-center">
        <motion.div
          className="absolute inset-0 rounded-md border border-zinc-700 bg-zinc-900"
          animate={{ rotate: 180 }}
          transition={{ duration: 1, repeat: Infinity, ease: "anticipate" }}
        />
        <motion.div
          className="h-4 w-4 rounded-[2px] bg-white z-10"
          animate={{ scale: [1, 0.5, 1], opacity: [1, 0.5, 1] }}
          transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>
      <motion.p
        className="text-sm font-medium text-zinc-400"
        animate={{ opacity: [0.4, 1, 0.4] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        Analyzing issue...
      </motion.p>
    </div>
  );
}
