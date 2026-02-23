#!/usr/bin/env python3
"""
PostTradeReconciliationModule - Módulo NCNT
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

class PostTradeReconciliationModule(NCNTBaseModule):
    """📤 RECONCILIAÇÃO PÓS-TRADE - Validação e Matching"""
    
    def __init__(self):
        super().__init__("post_trade_reconciliation", ModuleType.OPERATION)
        self.reconciliation_rules = self._initialize_reconciliation_rules()
        self.reconciliation_results = {}
        self.trade_store = {}
        self.discrepancy_log = {}
        
    def _initialize_reconciliation_rules(self) -> Dict:
        """Inicializar regras de reconciliação"""
        return {
            "matching_tolerance": {
                "price": 0.0001,  # 0.01%
                "quantity": 0.0001,  # 0.01%
                "time": 60,  # seconds
                "value": 0.001  # 0.1%
            },
            "auto_correction": {
                "price_discrepancy": True,
                "quantity_discrepancy": False,
                "time_discrepancy": True,
                "missing_trades": True
            },
            "validation_checks": {
                "validate_timestamps": True,
                "validate_prices": True,
                "validate_quantities": True,
                "validate_counterparties": True,
                "validate_instruments": True
            },
            "reporting": {
                "generate_daily_report": True,
                "generate_discrepancy_report": True,
                "alert_on_discrepancy": True,
                "retention_days": 90
            }
        }
    
    async def initialize(self, config: Dict) -> bool:
        await super().initialize(config)
        
        # Configurar armazenamento
        self.storage_config = config.get("storage_config", {
            "trade_retention_days": 30,
            "result_retention_days": 90,
            "backup_frequency": "daily",
            "encryption_required": True
        })
        
        # Configurar notificações
        self.notification_config = config.get("notification_config", {
            "email_recipients": ["reconciliation@ncnt.com", "ops@ncnt.com"],
            "slack_channel": "#reconciliation",
            "alert_threshold": 0.01,  # 1% discrepancy
            "critical_threshold": 0.05  # 5% discrepancy
        })
        
        self.status = "ACTIVE"
        return True
    
    async def reconcile_trades(self, trades_executed: List[Dict], 
                              trades_expected: List[Dict]) -> Dict:
        """Reconciliar trades executados vs esperados"""
        reconciliation_id = f"RECON_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        reconciliation = {
            "reconciliation_id": reconciliation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "summary": {
                "total_executed": len(trades_executed),
                "total_expected": len(trades_expected),
                "matches": 0,
                "mismatches": 0,
                "missing": 0,
                "extra": 0
            },
            "details": {
                "matches": [],
                "mismatches": [],
                "missing": [],
                "extra": []
            },
            "discrepancies": [],
            "auto_corrections": [],
            "requires_manual_review": False
        }
        
        print(f"🔍 Starting trade reconciliation: {reconciliation_id}")
        
        try:
            # Processar reconciliação
            await self._process_reconciliation(reconciliation, trades_executed, trades_expected)
            
            # Calcular métricas
            await self._calculate_reconciliation_metrics(reconciliation)
            
            # Aplicar correções automáticas
            await self._apply_auto_corrections(reconciliation)
            
            # Gerar relatórios
            reconciliation["reports"] = await self._generate_reconciliation_reports(reconciliation)
            
            reconciliation["status"] = "COMPLETED"
            reconciliation["completed_at"] = datetime.now().isoformat()
            
            print(f"✅ Reconciliation completed: {reconciliation_id}")
            
        except Exception as e:
            reconciliation["status"] = "FAILED"
            reconciliation["error"] = str(e)
            reconciliation["completed_at"] = datetime.now().isoformat()
            print(f"❌ Reconciliation failed: {reconciliation_id} - {e}")
        
        # Armazenar resultados
        self.reconciliation_results[reconciliation_id] = reconciliation
        
        return reconciliation
    
    async def validate_trade(self, trade_data: Dict) -> Dict:
        """Validar trade individual"""
        validation_id = f"VALID_{uuid.uuid4().hex[:8]}"
        
        validation = {
            "validation_id": validation_id,
            "trade_id": trade_data.get("trade_id", "UNKNOWN"),
            "timestamp": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "checks": [],
            "overall_valid": True,
            "issues": []
        }
        
        # Executar validações
        validation_checks = self.reconciliation_rules["validation_checks"]
        
        if validation_checks["validate_timestamps"]:
            timestamp_check = await self._validate_timestamp(trade_data)
            validation["checks"].append(timestamp_check)
            if not timestamp_check["valid"]:
                validation["overall_valid"] = False
                validation["issues"].append("INVALID_TIMESTAMP")
        
        if validation_checks["validate_prices"]:
            price_check = await self._validate_price(trade_data)
            validation["checks"].append(price_check)
            if not price_check["valid"]:
                validation["overall_valid"] = False
                validation["issues"].append("INVALID_PRICE")
        
        if validation_checks["validate_quantities"]:
            quantity_check = await self._validate_quantity(trade_data)
            validation["checks"].append(quantity_check)
            if not quantity_check["valid"]:
                validation["overall_valid"] = False
                validation["issues"].append("INVALID_QUANTITY")
        
        if validation_checks["validate_counterparties"]:
            counterparty_check = await self._validate_counterparty(trade_data)
            validation["checks"].append(counterparty_check)
            if not counterparty_check["valid"]:
                validation["overall_valid"] = False
                validation["issues"].append("INVALID_COUNTERPARTY")
        
        if validation_checks["validate_instruments"]:
            instrument_check = await self._validate_instrument(trade_data)
            validation["checks"].append(instrument_check)
            if not instrument_check["valid"]:
                validation["overall_valid"] = False
                validation["issues"].append("INVALID_INSTRUMENT")
        
        validation["status"] = "COMPLETED"
        
        return validation
    
    async def process_transmission(self, transmission: NCNTTransmission) -> Optional[NCNTTransmission]:
        """Processar transmissões de reconciliação"""
        if transmission.module_type != ModuleType.OPERATION:
            return None
            
        action = transmission.payload.get("action")
        
        if action == "reconcile_trades":
            # Reconciliar trades
            trades_executed = transmission.payload.get("trades_executed", [])
            trades_expected = transmission.payload.get("trades_expected", [])
            
            reconciliation_result = await self.reconcile_trades(trades_executed, trades_expected)
            
            return NCNTTransmission(
                transmission_id=f"RECON_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=reconciliation_result
            )
        
        elif action == "validate_trade":
            # Validar trade
            trade_data = transmission.payload.get("trade_data", {})
            validation_result = await self.validate_trade(trade_data)
            
            return NCNTTransmission(
                transmission_id=f"RECON_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=validation_result
            )
        
        elif action == "get_reconciliation_report":
            # Obter relatório de reconciliação
            reconciliation_id = transmission.payload.get("reconciliation_id")
            report = await self.get_reconciliation_report(reconciliation_id)
            
            return NCNTTransmission(
                transmission_id=f"RECON_RESP_{uuid.uuid4().hex[:8]}",
                source_module=self.module_name,
                target_module=transmission.source_module,
                module_type=self.module_type,
                payload=report
            )
        
        return None
    
    # ========== MÉTODOS DE RECONCILIAÇÃO ==========
    
    async def _process_reconciliation(self, reconciliation: Dict, 
                                     trades_executed: List[Dict], 
                                     trades_expected: List[Dict]):
        """Processar reconciliação de trades"""
        matched_executed = set()
        matched_expected = set()
        
        # Tentar encontrar matches
        for i, expected in enumerate(trades_expected):
            for j, executed in enumerate(trades_executed):
                if j in matched_executed:
                    continue
                    
                # Verificar se trades correspondem
                match_result = await self._check_trade_match(expected, executed)
                
                if match_result["is_match"]:
                    # Trades correspondem
                    reconciliation["summary"]["matches"] += 1
                    reconciliation["details"]["matches"].append({
                        "expected": expected,
                        "executed": executed,
                        "match_quality": match_result["match_quality"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    matched_expected.add(i)
                    matched_executed.add(j)
                    
                    break
                elif match_result["is_partial_match"]:
                    # Match parcial (mismatch)
                    reconciliation["summary"]["mismatches"] += 1
                    reconciliation["details"]["mismatches"].append({
                        "expected": expected,
                        "executed": executed,
                        "discrepancies": match_result["discrepancies"],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    reconciliation["discrepancies"].extend(match_result["discrepancies"])
                    
                    matched_expected.add(i)
                    matched_executed.add(j)
                    
                    break
        
        # Identificar trades faltantes (esperados mas não executados)
        for i, expected in enumerate(trades_expected):
            if i not in matched_expected:
                reconciliation["summary"]["missing"] += 1
                reconciliation["details"]["missing"].append(expected)
        
        # Identificar trades extras (executados mas não esperados)
        for j, executed in enumerate(trades_executed):
            if j not in matched_executed:
                reconciliation["summary"]["extra"] += 1
                reconciliation["details"]["extra"].append(executed)
    
    async def _check_trade_match(self, expected: Dict, executed: Dict) -> Dict:
        """Verificar se trades correspondem"""
        tolerances = self.reconciliation_rules["matching_tolerance"]
        discrepancies = []
        
        # Verificar trade IDs
        expected_id = expected.get("trade_id")
        executed_id = executed.get("trade_id")
        
        if expected_id and executed_id and expected_id != executed_id:
            discrepancies.append({
                "field": "trade_id",
                "expected": expected_id,
                "executed": executed_id,
                "difference": "different",
                "severity": "high"
            })
        
        # Verificar símbolo
        expected_symbol = expected.get("symbol")
        executed_symbol = executed.get("symbol")
        
        if expected_symbol != executed_symbol:
            discrepancies.append({
                "field": "symbol",
                "expected": expected_symbol,
                "executed": executed_symbol,
                "difference": "different",
                "severity": "high"
            })
        
        # Verificar quantidade
        expected_quantity = expected.get("quantity", 0)
        executed_quantity = executed.get("quantity", 0)
        
        if abs(expected_quantity - executed_quantity) > tolerances["quantity"]:
            discrepancies.append({
                "field": "quantity",
                "expected": expected_quantity,
                "executed": executed_quantity,
                "difference": abs(expected_quantity - executed_quantity),
                "severity": "medium"
            })
        
        # Verificar preço
        expected_price = expected.get("price", 0)
        executed_price = executed.get("price", 0)
        
        if expected_price > 0:
            price_diff_pct = abs(expected_price - executed_price) / expected_price
            
            if price_diff_pct > tolerances["price"]:
                discrepancies.append({
                    "field": "price",
                    "expected": expected_price,
                    "executed": executed_price,
                    "difference": price_diff_pct,
                    "severity": "high"
                })
        
        # Verificar timestamp
        expected_time = expected.get("timestamp")
        executed_time = executed.get("timestamp")
        
        if expected_time and executed_time:
            try:
                expected_dt = datetime.fromisoformat(expected_time.replace('Z', '+00:00'))
                executed_dt = datetime.fromisoformat(executed_time.replace('Z', '+00:00'))
                time_diff = abs((executed_dt - expected_dt).total_seconds())
                
                if time_diff > tolerances["time"]:
                    discrepancies.append({
                        "field": "timestamp",
                        "expected": expected_time,
                        "executed": executed_time,
                        "difference": time_diff,
                        "severity": "low"
                    })
            except:
                pass
        
        # Determinar tipo de match
        if len(discrepancies) == 0:
            return {
                "is_match": True,
                "is_partial_match": False,
                "match_quality": "perfect",
                "discrepancies": []
            }
        elif len([d for d in discrepancies if d["severity"] == "high"]) == 0:
            return {
                "is_match": False,
                "is_partial_match": True,
                "match_quality": "good",
                "discrepancies": discrepancies
            }
        else:
            return {
                "is_match": False,
                "is_partial_match": True,
                "match_quality": "poor",
                "discrepancies": discrepancies
            }
    
    async def _calculate_reconciliation_metrics(self, reconciliation: Dict):
        """Calcular métricas de reconciliação"""
        summary = reconciliation["summary"]
        
        if summary["total_expected"] > 0:
            reconciliation["metrics"] = {
                "match_rate": summary["matches"] / summary["total_expected"],
                "discrepancy_rate": summary["mismatches"] / summary["total_expected"],
                "missing_rate": summary["missing"] / summary["total_expected"],
                "extra_rate": summary["extra"] / summary["total_executed"] if summary["total_executed"] > 0 else 0,
                "overall_accuracy": (summary["matches"] + 0.5 * summary["mismatches"]) / summary["total_expected"]
            }
        else:
            reconciliation["metrics"] = {
                "match_rate": 0,
                "discrepancy_rate": 0,
                "missing_rate": 0,
                "extra_rate": 0,
                "overall_accuracy": 0
            }
        
        # Verificar se requer revisão manual
        threshold = self.notification_config["alert_threshold"]
        critical_threshold = self.notification_config["critical_threshold"]
        
        if reconciliation["metrics"]["missing_rate"] > critical_threshold:
            reconciliation["requires_manual_review"] = True
            reconciliation["review_reason"] = "High missing trades rate"
        elif reconciliation["metrics"]["discrepancy_rate"] > threshold:
            reconciliation["requires_manual_review"] = True
            reconciliation["review_reason"] = "High discrepancy rate"
    
    async def _apply_auto_corrections(self, reconciliation: Dict):
        """Aplicar correções automáticas"""
        auto_correction = self.reconciliation_rules["auto_correction"]
        corrections = []
        
        # Corrigir discrepâncias de preço
        if auto_correction["price_discrepancy"]:
            for mismatch in reconciliation["details"]["mismatches"]:
                price_discrepancies = [
                    d for d in mismatch.get("discrepancies", []) 
                    if d["field"] == "price" and d["severity"] != "high"
                ]
                
                for discrepancy in price_discrepancies:
                    correction = {
                        "type": "price_correction",
                        "trade_id": mismatch["executed"].get("trade_id"),
                        "field": "price",
                        "old_value": discrepancy["executed"],
                        "new_value": discrepancy["expected"],
                        "reason": "Auto-correct price discrepancy",
                        "timestamp": datetime.now().isoformat()
                    }
                    corrections.append(correction)
        
        # Corrigir discrepâncias de tempo
        if auto_correction["time_discrepancy"]:
            for mismatch in reconciliation["details"]["mismatches"]:
                time_discrepancies = [
                    d for d in mismatch.get("discrepancies", []) 
                    if d["field"] == "timestamp"
                ]
                
                for discrepancy in time_discrepancies:
                    correction = {
                        "type": "timestamp_correction",
                        "trade_id": mismatch["executed"].get("trade_id"),
                        "field": "timestamp",
                        "old_value": discrepancy["executed"],
                        "new_value": discrepancy["expected"],
                        "reason": "Auto-correct timestamp discrepancy",
                        "timestamp": datetime.now().isoformat()
                    }
                    corrections.append(correction)
        
        reconciliation["auto_corrections"] = corrections
    
    # ========== MÉTODOS DE VALIDAÇÃO ==========
    
    async def _validate_timestamp(self, trade_data: Dict) -> Dict:
        """Validar timestamp do trade"""
        timestamp = trade_data.get("timestamp")
        
        if not timestamp:
            return {
                "check": "timestamp",
                "valid": False,
                "reason": "Missing timestamp",
                "severity": "high"
            }
        
        try:
            trade_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            current_time = datetime.now()
            
            # Verificar se timestamp não está no futuro
            if trade_time > current_time:
                return {
                    "check": "timestamp",
                    "valid": False,
                    "reason": "Timestamp in the future",
                    "severity": "high"
                }
            
            # Verificar se timestamp não é muito antigo (mais de 7 dias)
            if (current_time - trade_time).days > 7:
                return {
                    "check": "timestamp",
                    "valid": False,
                    "reason": "Timestamp too old",
                    "severity": "medium"
                }
            
            return {
                "check": "timestamp",
                "valid": True,
                "reason": "Timestamp valid",
                "severity": "low"
            }
            
        except ValueError:
            return {
                "check": "timestamp",
                "valid": False,
                "reason": "Invalid timestamp format",
                "severity": "high"
            }
    
    async def _validate_price(self, trade_data: Dict) -> Dict:
        """Validar preço do trade"""
        price = trade_data.get("price", 0)
        symbol = trade_data.get("symbol", "")
        
        if price <= 0:
            return {
                "check": "price",
                "valid": False,
                "reason": "Price must be positive",
                "severity": "high"
            }
        
        # Verificar limites de preço baseados no símbolo
        price_limits = {
            "EURUSD": (0.5, 2.0),
            "XAUUSD": (1000, 3000),
            "BTCUSD": (10000, 100000),
            "default": (0, 1000000)
        }
        
        limit = price_limits.get(symbol, price_limits["default"])
        
        if not (limit[0] <= price <= limit[1]):
            return {
                "check": "price",
                "valid": False,
                "reason": f"Price outside expected range: {limit[0]} - {limit[1]}",
                "severity": "high"
            }
        
        return {
            "check": "price",
            "valid": True,
            "reason": "Price valid",
            "severity": "low"
        }
    
    async def _validate_quantity(self, trade_data: Dict) -> Dict:
        """Validar quantidade do trade"""
        quantity = trade_data.get("quantity", 0)
        
        if quantity <= 0:
            return {
                "check": "quantity",
                "valid": False,
                "reason": "Quantity must be positive",
                "severity": "high"
            }
        
        # Verificar limites de quantidade
        max_quantity = 1000000  # 1 milhão
        
        if quantity > max_quantity:
            return {
                "check": "quantity",
                "valid": False,
                "reason": f"Quantity exceeds maximum: {max_quantity}",
                "severity": "high"
            }
        
        return {
            "check": "quantity",
            "valid": True,
            "reason": "Quantity valid",
            "severity": "low"
        }
    
    async def _validate_counterparty(self, trade_data: Dict) -> Dict:
        """Validar contraparte do trade"""
        counterparty = trade_data.get("counterparty", "")
        
        if not counterparty:
            return {
                "check": "counterparty",
                "valid": False,
                "reason": "Missing counterparty",
                "severity": "high"
            }
        
        # Lista de contrapartes aprovadas
        approved_counterparties = [
            "BROKER_A", "BROKER_B", "BROKER_C", 
            "EXCHANGE_A", "EXCHANGE_B", "INTERNAL"
        ]
        
        if counterparty not in approved_counterparties:
            return {
                "check": "counterparty",
                "valid": False,
                "reason": f"Counterparty not approved: {counterparty}",
                "severity": "high"
            }
        
        return {
            "check": "counterparty",
            "valid": True,
            "reason": "Counterparty valid",
            "severity": "low"
        }
    
    async def _validate_instrument(self, trade_data: Dict) -> Dict:
        """Validar instrumento do trade"""
        symbol = trade_data.get("symbol", "")
        
        if not symbol:
            return {
                "check": "instrument",
                "valid": False,
                "reason": "Missing symbol",
                "severity": "high"
            }
        
        # Lista de instrumentos suportados
        supported_instruments = [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
            "XAUUSD", "XAGUSD", "BTCUSD", "ETHUSD", "US500", "US30", "NAS100"
        ]
        
        if symbol not in supported_instruments:
            return {
                "check": "instrument",
                "valid": False,
                "reason": f"Instrument not supported: {symbol}",
                "severity": "high"
            }
        
        return {
            "check": "instrument",
            "valid": True,
            "reason": "Instrument valid",
            "severity": "low"
        }
    
    # ========== MÉTODOS DE RELATÓRIO ==========
    
    async def _generate_reconciliation_reports(self, reconciliation: Dict) -> Dict:
        """Gerar relatórios de reconciliação"""
        reports = {}
        
        if self.reconciliation_rules["reporting"]["generate_daily_report"]:
            reports["daily_report"] = await self._generate_daily_report(reconciliation)
        
        if self.reconciliation_rules["reporting"]["generate_discrepancy_report"]:
            reports["discrepancy_report"] = await self._generate_discrepancy_report(reconciliation)
        
        return reports
    
    async def _generate_daily_report(self, reconciliation: Dict) -> Dict:
        """Gerar relatório diário"""
        return {
            "report_id": f"DAILY_RECON_{datetime.now().strftime('%Y%m%d')}",
            "type": "daily_reconciliation",
            "timestamp": datetime.now().isoformat(),
            "summary": reconciliation["summary"],
            "metrics": reconciliation.get("metrics", {}),
            "status": reconciliation["status"],
            "requires_manual_review": reconciliation.get("requires_manual_review", False),
            "auto_corrections_applied": len(reconciliation.get("auto_corrections", [])),
            "recommendations": await self._generate_recommendations(reconciliation)
        }
    
    async def _generate_discrepancy_report(self, reconciliation: Dict) -> Dict:
        """Gerar relatório de discrepâncias"""
        discrepancies = reconciliation.get("discrepancies", [])
        
        high_severity = [d for d in discrepancies if d.get("severity") == "high"]
        medium_severity = [d for d in discrepancies if d.get("severity") == "medium"]
        low_severity = [d for d in discrepancies if d.get("severity") == "low"]
        
        return {
            "report_id": f"DISCREPANCY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "discrepancy",
            "timestamp": datetime.now().isoformat(),
            "total_discrepancies": len(discrepancies),
            "by_severity": {
                "high": len(high_severity),
                "medium": len(medium_severity),
                "low": len(low_severity)
            },
            "by_field": self._group_discrepancies_by_field(discrepancies),
            "top_discrepancies": high_severity[:10],
            "trend_analysis": await self._analyze_discrepancy_trend()
        }
    
    def _group_discrepancies_by_field(self, discrepancies: List[Dict]) -> Dict:
        """Agrupar discrepâncias por campo"""
        grouped = {}
        
        for discrepancy in discrepancies:
            field = discrepancy.get("field", "unknown")
            if field not in grouped:
                grouped[field] = []
            grouped[field].append(discrepancy)
        
        return {
            field: {
                "count": len(items),
                "examples": items[:3]
            }
            for field, items in grouped.items()
        }
    
    async def _analyze_discrepancy_trend(self) -> Dict:
        """Analisar tendência de discrepâncias"""
        # Implementação simplificada
        return {
            "trend": "stable",
            "average_daily_discrepancies": 12.5,
            "most_common_field": "price",
            "improvement_suggestion": "Review price validation logic"
        }
    
    async def _generate_recommendations(self, reconciliation: Dict) -> List[str]:
        """Gerar recomendações baseadas na reconciliação"""
        recommendations = []
        
        metrics = reconciliation.get("metrics", {})
        
        if metrics.get("missing_rate", 0) > 0.05:  # 5%
            recommendations.append("Investigate missing trades - possible execution issues")
        
        if metrics.get("discrepancy_rate", 0) > 0.02:  # 2%
            recommendations.append("Review price validation and matching logic")
        
        if metrics.get("extra_rate", 0) > 0.01:  # 1%
            recommendations.append("Check for duplicate trade entries")
        
        if len(reconciliation.get("auto_corrections", [])) > 10:
            recommendations.append("Consider improving trade data quality at source")
        
        return recommendations
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def get_reconciliation_report(self, reconciliation_id: str) -> Dict:
        """Obter relatório de reconciliação específico"""
        if reconciliation_id not in self.reconciliation_results:
            return {"error": f"Reconciliation {reconciliation_id} not found", "status": "UNKNOWN"}
        
        reconciliation = self.reconciliation_results[reconciliation_id]
        
        return {
            "reconciliation_id": reconciliation_id,
            "status": reconciliation["status"],
            "timestamp": reconciliation["timestamp"],
            "summary": reconciliation["summary"],
            "metrics": reconciliation.get("metrics", {}),
            "requires_manual_review": reconciliation.get("requires_manual_review", False),
            "auto_corrections": len(reconciliation.get("auto_corrections", [])),
            "discrepancies": len(reconciliation.get("discrepancies", [])),
            "reports": reconciliation.get("reports", {})
        }

# ============================================================================
# 🛠️ 04-INFRAESTRUTURA TÉCNICA: MODULES
# ============================================================================
