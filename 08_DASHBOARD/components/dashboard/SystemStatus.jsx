import React from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, AlertTriangle, CheckCircle, DollarSign, TrendingUp, Activity } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export default function SystemStatus({ riskMetrics }) {
    const deploymentPercentage = riskMetrics?.global_aum > 0
        ? ((riskMetrics.deployed_capital / riskMetrics.global_aum) * 100).toFixed(1)
        : 0;

    const toxicityConfig = {
        SAFE: { icon: CheckCircle, color: "text-green-400", bg: "bg-green-500/20", border: "border-green-500/50" },
        ELEVATED: { icon: Activity, color: "text-yellow-400", bg: "bg-yellow-500/20", border: "border-yellow-500/50" },
        HIGH: { icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-500/20", border: "border-orange-500/50" },
        CRITICAL: { icon: Shield, color: "text-red-400", bg: "bg-red-500/20", border: "border-red-500/50" }
    };

    const currentToxicity = toxicityConfig[riskMetrics?.system_toxicity || "SAFE"];
    const ToxicityIcon = currentToxicity.icon;

    return (
        <Card className="bg-black/40 backdrop-blur-xl border-cyan-500/20">
            <div className="h-1 w-full bg-gradient-to-r from-purple-500 via-cyan-500 to-blue-500" />

            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <Shield className="w-6 h-6 text-cyan-400" />
                        NUMEIA TREASURY SECURED
                    </h2>
                    {riskMetrics?.emergency_mode && (
                        <motion.div
                            animate={{ scale: [1, 1.1, 1] }}
                            transition={{ repeat: Infinity, duration: 1 }}
                        >
                            <Badge className="bg-red-500/20 text-red-400 border-red-500/50">
                                EMERGENCY MODE
                            </Badge>
                        </motion.div>
                    )}
                </div>

                {/* Grid de métricas */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {/* Global AUM */}
                    <div className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 rounded-lg p-4 border border-cyan-500/20">
                        <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                            <DollarSign className="w-4 h-4" />
                            <span>Global AUM</span>
                        </div>
                        <div className="text-3xl font-bold text-white">
                            ${(riskMetrics?.global_aum || 0).toLocaleString()}
                        </div>
                    </div>

                    {/* Capital Deployed */}
                    <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 rounded-lg p-4 border border-green-500/20">
                        <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                            <Activity className="w-4 h-4" />
                            <span>Deployed</span>
                        </div>
                        <div className="text-3xl font-bold text-white">
                            ${(riskMetrics?.deployed_capital || 0).toLocaleString()}
                        </div>
                        <div className="text-xs text-green-400 mt-1">{deploymentPercentage}% of AUM</div>
                    </div>

                    {/* Global PnL */}
                    <div className={cn(
                        "rounded-lg p-4 border",
                        (riskMetrics?.global_pnl || 0) >= 0
                            ? "bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20"
                            : "bg-gradient-to-br from-red-500/10 to-rose-500/10 border-red-500/20"
                    )}>
                        <div className="flex items-center gap-2 text-slate-400 text-sm mb-2">
                            <TrendingUp className="w-4 h-4" />
                            <span>Global PnL</span>
                        </div>
                        <div className={cn(
                            "text-3xl font-bold",
                            (riskMetrics?.global_pnl || 0) >= 0 ? "text-green-400" : "text-red-400"
                        )}>
                            ${Math.abs(riskMetrics?.global_pnl || 0).toLocaleString()}
                        </div>
                    </div>
                </div>

                {/* Status e controles */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* System Toxicity */}
                    <div className={cn(
                        "rounded-lg p-4 border",
                        currentToxicity.bg,
                        currentToxicity.border
                    )}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <ToxicityIcon className={cn("w-6 h-6", currentToxicity.color)} />
                                <div>
                                    <div className="text-sm text-slate-400">System Toxicity</div>
                                    <div className={cn("text-xl font-bold", currentToxicity.color)}>
                                        {riskMetrics?.system_toxicity || "SAFE"}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Variance Cap */}
                    <div className="bg-black/40 rounded-lg p-4 border border-slate-700/50">
                        <div className="text-sm text-slate-400 mb-1">Dynamic Variance Cap</div>
                        <div className="text-xl font-bold text-white mb-2">
                            {riskMetrics?.variance_cap_current?.toFixed(2) || "5.00"}%
                        </div>
                        <div className="text-xs text-slate-500">
                            VIX Level: {riskMetrics?.vix_level?.toFixed(2) || "N/A"}
                        </div>
                    </div>
                </div>
            </div>
        </Card>
    );
}
