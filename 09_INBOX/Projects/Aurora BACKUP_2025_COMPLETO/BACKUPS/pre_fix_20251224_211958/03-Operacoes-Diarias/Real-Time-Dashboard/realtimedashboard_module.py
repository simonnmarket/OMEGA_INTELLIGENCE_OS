#!/usr/bin/env python3
"""
RealTimeDashboardModule - Módulo NCNT
Extraído do sistema completo NCNT v2.0
"""

import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.ncnt_base import (
    ModuleType,
    AssetClass,
    TransmissionPriority,
    NCNTTransmission,
    NCNTBaseModule
)
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml
import hashlib
import uuid
from pathlib import Path
import logging
import asyncio
from abc import ABC, abstractmethod
import pickle
import csv
from decimal import Decimal

class RealTimeDashboardModule(NCNTBaseModule):
    """📊 DASHBOARD EM TEMPO REAL - Monitoramento e KPIs"""
    
    def __init__(self):
        super().__init__("realtime_dashboard", ModuleType.OPERATION)
        self.dashboard_config = self._initialize_dashboard_config()
        self.widgets = {}
        self.kpi_history = {}
        self.alert_rules = {}
        
    def _initialize_dashboard_config(self) -> Dict:
        """Inicializar configuração do dashboard"""
        return {
            "refresh_interval_seconds": 5,
            "retention_hours": 24,
            "max_data_points": 10000,
            "widgets_per_page": 12,
            "themes": ["light", "dark", "system"],
            "default_theme": "dark",
            "export_formats": ["json", "csv", "pdf"],
            "auto_refresh": True
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar widgets
        self.widgets = config.get("widgets", {
            "system_health": {
                "type": "gauge",
                "title": "System Health",
                "position": {"row": 0, "col": 0, "width": 2, "height": 2},
                "data_source": "system_metrics",
                "refresh_rate": 10,
                "thresholds": {"green": 90, "yellow": 70, "red": 50}
            },
            "performance_metrics": {
                "type": "line_chart",
                "title": "Performance Metrics",
                "position": {"row": 0, "col": 2, "width": 4, "height": 2},
                "data_source": "performance_data",
                "refresh_rate": 5,
                "metrics": ["latency", "throughput", "error_rate"]
            },
            "risk_overview": {
                "type": "table",
                "title": "Risk Overview",
                "position": {"row": 2, "col": 0, "width": 3, "height": 3},
                "data_source": "risk_metrics",
                "refresh_rate": 15,
                "columns": ["metric", "value", "limit", "status"]
            },
            "trading_activity": {
                "type": "bar_chart",
                "title": "Trading Activity",
                "position": {"row": 2, "col": 3, "width": 3, "height": 3},
                "data_source": "trading_data",
                "refresh_rate": 5,
                "metrics": ["trades", "volume", "pnl"]
            },
            "compliance_status": {
                "type": "status_grid",
                "title": "Compliance Status",
                "position": {"row": 5, "col": 0, "width": 6, "height": 2},
                "data_source": "compliance_checks",
                "refresh_rate": 30,
                "checks": ["kyc", "aml", "reporting", "limits"]
            }
        })
        
        # Configurar regras de alerta
        self.alert_rules = config.get("alert_rules", {
            "system_health_below_70": {
                "metric": "system_health",
                "condition": "<",
                "threshold": 70,
                "severity": "warning",
                "notification_channels": ["slack", "email"]
            },
            "latency_above_100ms": {
                "metric": "latency",
                "condition": ">",
                "threshold": 100,
                "severity": "critical",
                "notification_channels": ["slack", "email", "sms"]
            },
            "error_rate_above_1%": {
                "metric": "error_rate",
                "condition": ">",
                "threshold": 0.01,
                "severity": "warning",
                "notification_channels": ["slack"]
            }
        })
        
        # Inicializar histórico
        self._initialize_kpi_history()
        
        self.status = "ACTIVE"
        return True
    
    async def update_dashboard(self, force_refresh: bool = False) -> Dict:
        """Atualizar dashboard com dados atuais"""
        dashboard_id = f"DASH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        dashboard_data = {
            "dashboard_id": dashboard_id,
            "timestamp": datetime.now().isoformat(),
            "widgets": {},
            "summary": {},
            "alerts": []
        }
        
        # Coletar dados para cada widget
        for widget_id, widget_config in self.widgets.items():
            widget_data = await self._collect_widget_data(widget_id, widget_config)
            dashboard_data["widgets"][widget_id] = widget_data
            
            # Verificar alertas
            widget_alerts = await self._check_widget_alerts(widget_id, widget_data)
            if widget_alerts:
                dashboard_data["alerts"].extend(widget_alerts)
        
        # Calcular resumo
        dashboard_data["summary"] = await self._calculate_dashboard_summary(dashboard_data)
        
        # Atualizar histórico
        await self._update_kpi_history(dashboard_data)
        
        return dashboard_data
    
    async def get_widget_data(self, widget_id: str, timeframe: str = "realtime") -> Dict:
        """Obter dados específicos de widget"""
        if widget_id not in self.widgets:
            return {"error": f"Widget {widget_id} not found", "status": "NOT_FOUND"}
        
        widget_config = self.widgets[widget_id]
        
        if timeframe == "realtime":
            # Dados em tempo real
            data = await self._collect_widget_data(widget_id, widget_config)
        else:
            # Dados históricos
            data = await self._get_historical_widget_data(widget_id, timeframe)
        
        return {
            "widget_id": widget_id,
            "widget_name": widget_config["title"],
            "timestamp": datetime.now().isoformat(),
            "timeframe": timeframe,
            "data": data
        }
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões do dashboard"""
        if transmission.module_type != ModuleType.OPERATION:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "update_dashboard":
            # Atualizar dashboard
            force_refresh = transmission.payload.get("force_refresh", False)
            dashboard_data = await self.update_dashboard(force_refresh)
            
            return NCNTTransmission(
                transmission_id=f"DASH_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=dashboard_data
            )
        
        elif action == "get_widget_data":
            # Obter dados de widget
            widget_id = transmission.payload.get("widget_id")
            timeframe = transmission.payload.get("timeframe", "realtime")
            widget_data = await self.get_widget_data(widget_id, timeframe)
            
            return NCNTTransmission(
                transmission_id=f"DASH_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=widget_data
            )
        
        elif action == "get_dashboard_config":
            # Obter configuração do dashboard
            config = await self.get_dashboard_config()
            
            return NCNTTransmission(
                transmission_id=f"DASH_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=config
            )
        
        return None
    
    # ========== MÉTODOS DE COLETA DE DADOS ==========
    
    async def _collect_widget_data(self, widget_id: str, widget_config: Dict) -> Dict:
        """Coletar dados para widget específico"""
        widget_type = widget_config["type"]
        data_source = widget_config["data_source"]
        
        # Coletar dados baseado no tipo de fonte
        if data_source == "system_metrics":
            data = await self._collect_system_metrics()
        elif data_source == "performance_data":
            data = await self._collect_performance_data(widget_config.get("metrics", []))
        elif data_source == "risk_metrics":
            data = await self._collect_risk_metrics()
        elif data_source == "trading_data":
            data = await self._collect_trading_data(widget_config.get("metrics", []))
        elif data_source == "compliance_checks":
            data = await self._collect_compliance_data()
        else:
            data = {"error": f"Unknown data source: {data_source}"}
        
        # Formatar baseado no tipo de widget
        formatted_data = self._format_widget_data(widget_type, data, widget_config)
        
        return {
            "widget_id": widget_id,
            "widget_type": widget_type,
            "title": widget_config["title"],
            "timestamp": datetime.now().isoformat(),
            "data": formatted_data,
            "raw_data": data
        }
    
    async def _collect_system_metrics(self) -> Dict:
        """Coletar métricas do sistema"""
        import random
        import psutil
        
        # Coletar métricas reais se possível
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage('/').percent
        except:
            # Valores simulados se psutil não disponível
            cpu_percent = random.uniform(10, 60)
            memory_percent = random.uniform(30, 80)
            disk_percent = random.uniform(20, 70)
        
        # Calcular saúde geral do sistema
        system_health = 100 - ((cpu_percent + memory_percent + disk_percent) / 3)
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_percent": disk_percent,
            "system_health": system_health,
            "active_processes": random.randint(50, 200),
            "network_io": {
                "bytes_sent": random.randint(1000000, 10000000),
                "bytes_recv": random.randint(1000000, 10000000)
            },
            "uptime_seconds": random.randint(3600, 86400),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _collect_performance_data(self, metrics: List[str]) -> Dict:
        """Coletar dados de performance"""
        import random
        
        data = {}
        
        if "latency" in metrics or not metrics:
            data["latency"] = random.uniform(10, 150)
        
        if "throughput" in metrics or not metrics:
            data["throughput"] = random.uniform(500, 2000)
        
        if "error_rate" in metrics or not metrics:
            data["error_rate"] = random.uniform(0, 0.02)
        
        if "response_time" in metrics:
            data["response_time"] = random.uniform(20, 200)
        
        if "success_rate" in metrics:
            data["success_rate"] = random.uniform(0.95, 1.0)
        
        data["timestamp"] = datetime.now().isoformat()
        
        # Adicionar tendência
        for key in data.keys():
            if key != "timestamp":
                # Simular variação suave
                if key not in self.kpi_history:
                    self.kpi_history[key] = []
                
                if self.kpi_history[key]:
                    last_value = self.kpi_history[key][-1]["value"]
                    # Variação de +/- 10%
                    variation = random.uniform(-0.1, 0.1)
                    data[key] = last_value * (1 + variation)
        
        return data
    
    async def _collect_risk_metrics(self) -> Dict:
        """Coletar métricas de risco"""
        import random
        
        return {
            "var_95": random.uniform(1000, 5000),
            "var_99": random.uniform(2000, 8000),
            "max_drawdown": random.uniform(0.05, 0.20),
            "exposure": random.uniform(0.3, 0.8),
            "concentration": random.uniform(0.1, 0.5),
            "liquidity_score": random.uniform(0.5, 0.95),
            "breaches_today": random.randint(0, 3),
            "circuit_breakers_active": random.choice([0, 0, 0, 1]),  # 25% chance
            "timestamp": datetime.now().isoformat()
        }
    
    async def _collect_trading_data(self, metrics: List[str]) -> Dict:
        """Coletar dados de trading"""
        import random
        
        data = {}
        
        if "trades" in metrics or not metrics:
            data["trades"] = random.randint(50, 500)
        
        if "volume" in metrics or not metrics:
            data["volume"] = random.uniform(100000, 1000000)
        
        if "pnl" in metrics or not metrics:
            data["pnl"] = random.uniform(-5000, 20000)
        
        if "win_rate" in metrics:
            data["win_rate"] = random.uniform(0.5, 0.7)
        
        if "open_positions" in metrics:
            data["open_positions"] = random.randint(5, 50)
        
        data["timestamp"] = datetime.now().isoformat()
        
        return data
    
    async def _collect_compliance_data(self) -> Dict:
        """Coletar dados de compliance"""
        import random
        
        checks = {
            "kyc": random.choice(["PASS", "PASS", "PASS", "WARNING"]),
            "aml": random.choice(["PASS", "PASS", "PASS", "FAIL"]),
            "reporting": random.choice(["PASS", "PASS", "LATE"]),
            "limits": random.choice(["PASS", "PASS", "NEAR_LIMIT"]),
            "best_execution": random.choice(["PASS", "PASS", "REVIEW"]),
            "record_keeping": random.choice(["PASS", "PASS", "AUDIT"])
        }
        
        passed_checks = sum(1 for status in checks.values() if status == "PASS")
        total_checks = len(checks)
        compliance_score = (passed_checks / total_checks) * 100
        
        return {
            "checks": checks,
            "compliance_score": compliance_score,
            "failed_checks": [k for k, v in checks.items() if v == "FAIL"],
            "warning_checks": [k for k, v in checks.items() if v in ["WARNING", "REVIEW", "NEAR_LIMIT", "LATE"]],
            "timestamp": datetime.now().isoformat()
        }
    
    # ========== MÉTODOS DE FORMATAÇÃO ==========
    
    def _format_widget_data(self, widget_type: str, data: Dict, config: Dict) -> Dict:
        """Formatar dados para tipo de widget específico"""
        if widget_type == "gauge":
            return self._format_gauge_data(data, config)
        elif widget_type == "line_chart":
            return self._format_line_chart_data(data, config)
        elif widget_type == "table":
            return self._format_table_data(data, config)
        elif widget_type == "bar_chart":
            return self._format_bar_chart_data(data, config)
        elif widget_type == "status_grid":
            return self._format_status_grid_data(data, config)
        else:
            return {"error": f"Unknown widget type: {widget_type}", "raw_data": data}
    
    def _format_gauge_data(self, data: Dict, config: Dict) -> Dict:
        """Formatar dados para gauge"""
        value = data.get("system_health", 50)
        thresholds = config.get("thresholds", {"green": 90, "yellow": 70, "red": 50})
        
        if value >= thresholds["green"]:
            status = "green"
        elif value >= thresholds["yellow"]:
            status = "yellow"
        else:
            status = "red"
        
        return {
            "value": value,
            "min": 0,
            "max": 100,
            "status": status,
            "thresholds": thresholds,
            "display_value": f"{value:.1f}%",
            "trend": self._calculate_trend("system_health", value)
        }
    
    def _format_line_chart_data(self, data: Dict, config: Dict) -> Dict:
        """Formatar dados para gráfico de linha"""
        metrics = config.get("metrics", [])
        chart_data = {}
        
        for metric in metrics:
            if metric in data:
                chart_data[metric] = {
                    "value": data[metric],
                    "trend": self._calculate_trend(metric, data[metric]),
                    "history": self._get_metric_history(metric, 10)
                }
        
        return {
            "series": chart_data,
            "timestamp": data.get("timestamp"),
            "time_range": "last 10 updates"
        }
    
    def _format_table_data(self, data: Dict, config: Dict) -> Dict:
        """Formatar dados para tabela"""
        columns = config.get("columns", [])
        rows = []
        
        # Converter dict em linhas de tabela
        for key, value in data.items():
            if key == "timestamp":
                continue
                
            row = {"metric": key.replace("_", " ").title()}
            
            if isinstance(value, (int, float)):
                row["value"] = f"{value:,.2f}"
                
                # Adicionar status baseado em limites conhecidos
                if "var" in key:
                    limit = 10000 if "95" in key else 20000
                    row["limit"] = f"{limit:,.0f}"
                    row["status"] = "OK" if value < limit else "WARNING"
                elif "drawdown" in key:
                    row["limit"] = "15%"
                    row["status"] = "OK" if value < 0.15 else "WARNING"
                elif "exposure" in key:
                    row["limit"] = "80%"
                    row["status"] = "OK" if value < 0.8 else "WARNING"
            
            rows.append(row)
        
        return {
            "columns": columns,
            "rows": rows,
            "total_rows": len(rows),
            "sort_by": "metric",
            "sort_order": "asc"
        }
    
    def _format_bar_chart_data(self, data: Dict, config: Dict) -> Dict:
        """Formatar dados para gráfico de barras"""
        metrics = config.get("metrics", [])
        bars = []
        
        for metric in metrics:
            if metric in data:
                bars.append({
                    "label": metric.replace("_", " ").title(),
                    "value": data[metric],
                    "color": self._get_bar_color(metric, data[metric])
                })
        
        return {
            "bars": bars,
            "timestamp": data.get("timestamp"),
            "y_axis_label": "Value",
            "x_axis_label": "Metric"
        }
    
    def _format_status_grid_data(self, data: Dict, config: Dict) -> Dict:
        """Formatar dados para grid de status"""
        checks = config.get("checks", [])
        status_data = data.get("checks", {})
        
        status_items = []
        for check in checks:
            status = status_data.get(check, "UNKNOWN")
            
            status_items.append({
                "check": check.upper(),
                "status": status,
                "icon": self._get_status_icon(status),
                "color": self._get_status_color(status),
                "last_checked": data.get("timestamp")
            })
        
        return {
            "items": status_items,
            "overall_score": data.get("compliance_score", 0),
            "timestamp": data.get("timestamp")
        }
    
    # ========== MÉTODOS DE ALERTAS ==========
    
    async def _check_widget_alerts(self, widget_id: str, widget_data: Dict) -> List[Dict]:
        """Verificar alertas para widget"""
        alerts = []
        
        for alert_id, alert_config in self.alert_rules.items():
            if alert_config["metric"] in widget_data.get("raw_data", {}):
                metric_value = widget_data["raw_data"][alert_config["metric"]]
                
                # Verificar condição
                condition_met = False
                condition = alert_config["condition"]
                threshold = alert_config["threshold"]
                
                if condition == ">":
                    condition_met = metric_value > threshold
                elif condition == "<":
                    condition_met = metric_value < threshold
                elif condition == ">=":
                    condition_met = metric_value >= threshold
                elif condition == "<=":
                    condition_met = metric_value <= threshold
                elif condition == "==":
                    condition_met = metric_value == threshold
                
                if condition_met:
                    alert = {
                        "alert_id": alert_id,
                        "widget_id": widget_id,
                        "metric": alert_config["metric"],
                        "value": metric_value,
                        "threshold": threshold,
                        "condition": condition,
                        "severity": alert_config["severity"],
                        "timestamp": datetime.now().isoformat(),
                        "message": f"{alert_config['metric']} {condition} {threshold}: {metric_value}"
                    }
                    
                    alerts.append(alert)
        
        return alerts
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _initialize_kpi_history(self):
        """Inicializar histórico de KPIs"""
        # Inicializar com dados vazios
        self.kpi_history = {
            "system_health": [],
            "latency": [],
            "throughput": [],
            "error_rate": [],
            "var_95": [],
            "max_drawdown": [],
            "trades": [],
            "volume": [],
            "pnl": [],
            "compliance_score": []
        }
    
    async def _update_kpi_history(self, dashboard_data: Dict):
        """Atualizar histórico de KPIs"""
        timestamp = dashboard_data["timestamp"]
        
        for widget_id, widget_data in dashboard_data["widgets"].items():
            raw_data = widget_data.get("raw_data", {})
            
            for metric, value in raw_data.items():
                if isinstance(value, (int, float)) and metric in self.kpi_history:
                    # Adicionar ao histórico
                    self.kpi_history[metric].append({
                        "timestamp": timestamp,
                        "value": value
                    })
                    
                    # Manter tamanho limitado
                    if len(self.kpi_history[metric]) > self.dashboard_config["max_data_points"]:
                        self.kpi_history[metric] = self.kpi_history[metric][-self.dashboard_config["max_data_points"]:]
    
    async def _get_historical_widget_data(self, widget_id: str, timeframe: str) -> Dict:
        """Obter dados históricos de widget"""
        # Implementação simplificada
        return {
            "widget_id": widget_id,
            "timeframe": timeframe,
            "data_points": 100,
            "status": "HISTORICAL",
            "message": "Historical data retrieval not fully implemented"
        }
    
    async def _calculate_dashboard_summary(self, dashboard_data: Dict) -> Dict:
        """Calcular resumo do dashboard"""
        widgets = dashboard_data["widgets"]
        alerts = dashboard_data["alerts"]
        
        # Calcular métricas agregadas
        system_health = widgets.get("system_health", {}).get("data", {}).get("value", 0)
        latency = widgets.get("performance_metrics", {}).get("raw_data", {}).get("latency", 0)
        compliance_score = widgets.get("compliance_status", {}).get("raw_data", {}).get("compliance_score", 0)
        
        critical_alerts = len([a for a in alerts if a.get("severity") == "critical"])
        warning_alerts = len([a for a in alerts if a.get("severity") == "warning"])
        
        return {
            "system_health": system_health,
            "avg_latency_ms": latency,
            "compliance_score": compliance_score,
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "total_widgets": len(widgets),
            "last_updated": dashboard_data["timestamp"],
            "overall_status": "HEALTHY" if critical_alerts == 0 else "DEGRADED"
        }
    
    def _calculate_trend(self, metric: str, current_value: float) -> str:
        """Calcular tendência da métrica"""
        if metric not in self.kpi_history or len(self.kpi_history[metric]) < 2:
            return "stable"
        
        history = self.kpi_history[metric]
        previous_value = history[-2]["value"] if len(history) >= 2 else history[-1]["value"]
        
        if current_value > previous_value * 1.1:
            return "up"
        elif current_value < previous_value * 0.9:
            return "down"
        else:
            return "stable"
    
    def _get_metric_history(self, metric: str, points: int) -> List[Dict]:
        """Obter histórico da métrica"""
        if metric not in self.kpi_history:
            return []
        
        history = self.kpi_history[metric][-points:]
        return [
            {"timestamp": h["timestamp"], "value": h["value"]}
            for h in history
        ]
    
    def _get_bar_color(self, metric: str, value: float) -> str:
        """Obter cor para barra baseada na métrica e valor"""
        if "pnl" in metric:
            return "green" if value >= 0 else "red"
        elif "error" in metric or "drawdown" in metric:
            return "red" if value > 0.1 else "yellow" if value > 0.05 else "green"
        else:
            return "blue"
    
    def _get_status_icon(self, status: str) -> str:
        """Obter ícone para status"""
        icons = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "REVIEW": "🔍",
            "NEAR_LIMIT": "📊",
            "LATE": "⏰",
            "AUDIT": "📋"
        }
        return icons.get(status, "❓")
    
    def _get_status_color(self, status: str) -> str:
        """Obter cor para status"""
        colors = {
            "PASS": "green",
            "FAIL": "red",
            "WARNING": "yellow",
            "REVIEW": "orange",
            "NEAR_LIMIT": "yellow",
            "LATE": "orange",
            "AUDIT": "blue"
        }
        return colors.get(status, "gray")
    
    async def get_dashboard_config(self) -> Dict:
        """Obter configuração completa do dashboard"""
        return {
            "dashboard_config": self.dashboard_config,
            "widgets": self.widgets,
            "alert_rules": self.alert_rules,
            "kpi_metrics": list(self.kpi_history.keys()),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# 📤 03-OPERAÇÕES DIÁRIAS: POST-TRADE RECONCILIATION
# ============================================================================
