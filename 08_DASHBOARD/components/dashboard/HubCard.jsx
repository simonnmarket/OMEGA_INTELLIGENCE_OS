import React from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, TrendingUp, TrendingDown, AlertTriangle, Shield, Zap } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const toxicityColors = {
  LOW: "bg-green-500/20 text-green-400 border-green-500/50",
  MEDIUM: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
  HIGH: "bg-orange-500/20 text-orange-400 border-orange-500/50",
  CRITICAL: "bg-red-500/20 text-red-400 border-red-500/50"
};

const statusColors = {
  ACTIVE: "bg-cyan-500/20 text-cyan-400 border-cyan-500/50",
  STANDBY: "bg-slate-500/20 text-slate-400 border-slate-500/50",
  LOCKED: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
  EMERGENCY_SHUTDOWN: "bg-red-500/20 text-red-400 border-red-500/50"
};

export default function HubCard({ hub, onClick }) {
  const pnlPositive = (hub.current_pnl || 0) >= 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02, transition: { duration: 0.2 } }}
      onClick={() => onClick?.(hub)}
      className="cursor-pointer"
    >
      <Card className="relative overflow-hidden bg-black/40 backdrop-blur-xl border-cyan-500/20 hover:border-cyan-500/40 transition-all">
        {/* Efeito de brilho animado */}
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent" />
        
        {/* Linha superior colorida */}
        <div className={cn(
          "h-1 w-full",
          hub.status === "ACTIVE" ? "bg-gradient-to-r from-cyan-500 to-blue-500" : "bg-gradient-to-r from-slate-500 to-slate-700"
        )} />
        
        <div className="p-6 relative">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                {hub.name}
                {hub.status === "ACTIVE" && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  >
                    <Activity className="w-4 h-4 text-cyan-400" />
                  </motion.div>
                )}
              </h3>
              <p className="text-sm text-slate-400 mt-1">{hub.segment}</p>
            </div>
            <Badge className={cn("border", statusColors[hub.status])}>
              {hub.status}
            </Badge>
          </div>

          {/* Métricas principais */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-black/40 rounded-lg p-3 border border-slate-800/50">
              <div className="text-xs text-slate-400 mb-1">Capital Alocado</div>
              <div className="text-lg font-bold text-white">
                ${(hub.allocated_capital || 0).toLocaleString()}
              </div>
            </div>
            <div className="bg-black/40 rounded-lg p-3 border border-slate-800/50">
              <div className="text-xs text-slate-400 mb-1">PnL Atual</div>
              <div className={cn(
                "text-lg font-bold flex items-center gap-1",
                pnlPositive ? "text-green-400" : "text-red-400"
              )}>
                {pnlPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                ${Math.abs(hub.current_pnl || 0).toLocaleString()}
              </div>
            </div>
          </div>

          {/* Volatilidade e Toxicidade */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-yellow-400" />
              <span className="text-xs text-slate-400">Volatilidade:</span>
              <span className="text-sm font-semibold text-white">{hub.volatility_profile?.toFixed(2)}</span>
            </div>
            <Badge className={cn("border text-xs", toxicityColors[hub.toxicity_level || "LOW"])}>
              <Shield className="w-3 h-3 mr-1" />
              {hub.toxicity_level || "LOW"}
            </Badge>
          </div>

          {/* Agentes ativos */}
          <div>
            <div className="text-xs text-slate-400 mb-2">Agentes Ativos:</div>
            <div className="flex flex-wrap gap-1">
              {hub.active_agents?.map((agent, idx) => (
                <Badge key={idx} variant="outline" className="text-xs border-cyan-500/30 text-cyan-400">
                  {agent}
                </Badge>
              ))}
            </div>
          </div>

          {/* Alerta de latência */}
          {hub.latency_p99 > 50 && (
            <div className="mt-4 flex items-center gap-2 text-xs text-orange-400 bg-orange-500/10 rounded px-2 py-1 border border-orange-500/30">
              <AlertTriangle className="w-3 h-3" />
              <span>High Latency: {hub.latency_p99}ms</span>
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}
