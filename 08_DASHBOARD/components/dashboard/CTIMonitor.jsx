import React from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Target, Waves, AlertCircle, CheckCircle2 } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const mockCTIData = [
    { name: "Force Navis 1", category: "Exhaustion", status: "SAFE", value: 87.5 },
    { name: "Seal Defense 3", category: "Defense", status: "ALERT", value: 45.2 },
    { name: "Volume Delta", category: "Flow", status: "SAFE", value: 92.1 },
    { name: "Absorption Wall", category: "Exhaustion", status: "CRITICAL", value: 23.8 },
    { name: "HFT Toxicity", category: "Defense", status: "SAFE", value: 78.3 },
    { name: "Resonance Index", category: "Flow", status: "SAFE", value: 91.7 }
];

export default function CTIMonitor() {
    return (
        <Card className="bg-black/40 backdrop-blur-xl border-cyan-500/20">
            <div className="h-1 w-full bg-gradient-to-r from-green-500 via-cyan-500 to-purple-500" />

            <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Target className="w-5 h-5 text-cyan-400" />
                        CTI COMMAND CENTER
                    </h2>
                    <Badge className="bg-cyan-500/20 text-cyan-400 border-cyan-500/50">
                        80+ Indicators
                    </Badge>
                </div>

                <div className="space-y-3">
                    {mockCTIData.map((cti, idx) => {
                        const statusConfig = {
                            SAFE: { icon: CheckCircle2, color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30" },
                            ALERT: { icon: AlertCircle, color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30" },
                            CRITICAL: { icon: AlertCircle, color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30" }
                        };

                        const config = statusConfig[cti.status];
                        const StatusIcon = config.icon;

                        return (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                                className={cn(
                                    "rounded-lg p-3 border",
                                    config.bg,
                                    config.border
                                )}
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <StatusIcon className={cn("w-4 h-4", config.color)} />
                                        <span className="text-sm font-semibold text-white">{cti.name}</span>
                                    </div>
                                    <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                                        {cti.category}
                                    </Badge>
                                </div>

                                {/* Barra de progresso */}
                                <div className="relative h-2 bg-black/40 rounded-full overflow-hidden">
                                    <motion.div
                                        initial={{ width: 0 }}
                                        animate={{ width: `${cti.value}%` }}
                                        transition={{ duration: 0.8, delay: idx * 0.1 }}
                                        className={cn(
                                            "h-full rounded-full",
                                            cti.status === "SAFE" && "bg-gradient-to-r from-green-500 to-emerald-400",
                                            cti.status === "ALERT" && "bg-gradient-to-r from-yellow-500 to-orange-400",
                                            cti.status === "CRITICAL" && "bg-gradient-to-r from-red-500 to-rose-400"
                                        )}
                                    />
                                </div>

                                <div className="flex items-center justify-between mt-1">
                                    <span className="text-xs text-slate-500">Signal Strength</span>
                                    <span className={cn("text-xs font-semibold", config.color)}>
                                        {cti.value.toFixed(1)}%
                                    </span>
                                </div>
                            </motion.div>
                        );
                    })}
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                        <Waves className="w-3 h-3" />
                        <span>Next scan in 0.8 seconds • Impact Absorption Mode Active</span>
                    </div>
                </div>
            </div>
        </Card>
    );
}
