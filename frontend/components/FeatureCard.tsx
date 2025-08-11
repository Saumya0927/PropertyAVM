'use client'

import { motion } from 'framer-motion'

interface FeatureCardProps {
  icon: React.ElementType
  title: string
  description: string
  color: string
  index: number
}

export default function FeatureCard({ icon: Icon, title, description, color, index }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
      className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow duration-300 group"
    >
      <div className={`inline-flex p-3 rounded-lg bg-gray-50 group-hover:bg-gray-100 transition-colors mb-4`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  )
}