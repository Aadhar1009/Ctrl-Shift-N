import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export function CursorGlow() {
  const [mousePosition, setMousePosition] = useState({ x: -200, y: -200 });

  useEffect(() => {
    const updateMousePosition = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', updateMousePosition);

    return () => {
      window.removeEventListener('mousemove', updateMousePosition);
    };
  }, []);

  return (
    <motion.div
      className="pointer-events-none fixed left-0 top-0 z-50 h-[400px] w-[400px] rounded-full bg-white opacity-[0.02] blur-[100px]"
      animate={{
        x: mousePosition.x - 200, // half of 400px
        y: mousePosition.y - 200,
      }}
      transition={{
        type: 'spring',
        damping: 50,
        stiffness: 200,
        mass: 0.1,
      }}
    />
  );
}
