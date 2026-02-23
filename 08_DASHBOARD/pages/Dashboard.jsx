import React, { useState, useEffect } from 'react';
import { base44 } from "@/api/base44Client";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { RefreshCw, Settings, Shield, Cpu } from "lucide-react";
import { motion } from "framer-motion";
import HubCard from "../components/dashboard/HubCard";
import SystemStatus from "../components/dashboard/SystemStatus";
import CTIMonitor from "../components/dashboard/CTIMonitor";

export default function Dashboard() {
    const [selectedHub, setSelectedHub] = useState(null);

    const { data: hubs = [], isLoading: loadingHubs, refetch: refetchHubs } = useQuery({
        queryKey: ['hubs'],
        queryFn: () => base44.entities.Hub.list('-updated_date'),
        refetchInterval: 5000 // Atualiza a cada 5 segundos
    });

    const { data: riskMetrics = [], isLoading: loadingRisk } = useQuery({
        queryKey: ['riskMetrics'],
        queryFn: () => base44.entities.RiskMetrics.list('-timestamp', 1),
        refetchInterval: 3000
    });

    const latestRiskMetrics = riskMetrics[0];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-black">
            {/* Efeito de grid futurista no fundo */}
            <div className="fixed inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] opacity-20" />

            <div className="relative z-10 p-6 max-w-[1920px] mx-auto">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-8"
                >
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-3">
                                <motion.div
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                    className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center"
                                >
                                    <Cpu className="w-6 h-6 text-white" />
                                </motion.div>
                                <div>
                                    <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                                        OMEGA INTELLIGENCE OS
                                    </h1>
                                    <p className="text-sm text-slate-400">v2.5 • Defensive-Reactive Paradigm</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            <Button
                                onClick={() => {
                                    refetchHubs();
                                }}
                                variant="outline"
                                className="border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh
                            </Button>
                            <Button
                                variant="outline"
                                className="border-slate-700 text-slate-300 hover:bg-slate-800"
                            >
                                <Settings className="w-4 h-4 mr-2" />
                                Settings
                            </Button>
                        </div>
                    </div>
                </motion.div>

                {/* System Status */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="mb-6"
                >
                    <SystemStatus riskMetrics={latestRiskMetrics} />
                </motion.div>

                {/* Grid principal */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                    {/* Hubs (2/3 do espaço) */}
                    <div className="lg:col-span-2">
                        <div className="mb-4">
                            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                                <Shield className="w-5 h-5 text-cyan-400" />
                                OPERATIONAL HUBS
                            </h2>
                            <p className="text-sm text-slate-400">8 Independent Market Segments</p>
                        </div>

                        {loadingHubs ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {[1, 2, 3, 4].map(i => (
                                    <div key={i} className="h-64 bg-black/40 rounded-lg animate-pulse border border-slate-800" />
                                ))}
                            </div>
                        ) : hubs.length === 0 ? (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-black/40 backdrop-blur-xl border border-slate-800 rounded-lg p-12 text-center"
                            >
                                <Shield className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                                <p className="text-slate-400 mb-4">Nenhum hub configurado ainda</p>
                                <Button
                                    onClick={() => {
                                        // Criar hubs de exemplo
                                        const exampleHubs = [
                                            { name: "FOREX", segment: "Fiat", volatility_profile: 0.5, active_agents: ["ScoutPro_v2"], allocated_capital: 1500000, current_pnl: 45000, toxicity_level: "LOW", status: "ACTIVE", latency_p99: 12 },
                                            { name: "CRYPTO", segment: "Digital", volatility_profile: 2.5, active_agents: ["Apollo11"], allocated_capital: 800000, current_pnl: -15000, toxicity_level: "MEDIUM", status: "ACTIVE", latency_p99: 65 },
                                            { name: "METALS", segment: "Commodity", volatility_profile: 1.5, active_agents: ["ScoutPro_v2", "DALL_ELO"], allocated_capital: 1200000, current_pnl: 28000, toxicity_level: "LOW", status: "ACTIVE", latency_p99: 18 },
                                            { name: "INDICES", segment: "Index", volatility_profile: 1.2, active_agents: ["ScoutPro_v2"], allocated_capital: 2000000, current_pnl: 67000, toxicity_level: "LOW", status: "ACTIVE", latency_p99: 15 }
                                        ];

                                        base44.entities.Hub.bulkCreate(exampleHubs).then(() => {
                                            refetchHubs();
                                        });
                                    }}
                                    className="bg-cyan-600 hover:bg-cyan-700"
                                >
                                    Inicializar Hubs
                                </Button>
                            </motion.div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {hubs.map((hub, idx) => (
                                    <motion.div
                                        key={hub.id}
                                        initial={{ opacity: 0, y: 20 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                    >
                                        <HubCard hub={hub} onClick={setSelectedHub} />
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* CTI Monitor (1/3 do espaço) */}
                    <div className="lg:col-span-1">
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            <CTIMonitor />
                        </motion.div>
                    </div>
                </div>

                {/* Footer */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center text-xs text-slate-500 pt-4 border-t border-slate-800"
                >
                    <p>CLASSIFICATION: TIER-0 RESTRICTED • Defensive-Reactive (Impact Absorption) Paradigm</p>
                    <p className="mt-1">Last System Update: {new Date().toLocaleString()}</p>
                </motion.div>
            </div>
        </div>
    );
}
