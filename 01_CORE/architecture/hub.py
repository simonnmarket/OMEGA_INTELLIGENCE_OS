"""
OMEGA Intelligence Hub Orchestrator
This module acts as the maestro of the Bank-Like Ecosystem. It interconnects the 4 layers:
Brain (L4) -> Treasury (L3) -> Compliance (L2) -> Traders (L1).
"""
import time
import logging
from typing import Dict, Any, List

# Import all agents
from .layer1_traders import QuantumScoutProAgent, Apollo11QuantumAgent
from .layer2_compliance import InstitutionalRadarAgent, HFTManagerAgent
from .layer3_treasury import NumeiaTreasuryAgent
from .layer4_brain import DallEloEngineAgent, ElliottWaveAgent, MPIIndexAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OmegaEcosystemHub:
    def __init__(self):
        logging.info("Initializing OMEGA Ecosystem Hub...")
        
        # Layer 4 - Brain
        self.brain_agents = [
            DallEloEngineAgent(),
            ElliottWaveAgent(),
            MPIIndexAgent()
        ]
        
        # Layer 3 - Treasury
        self.treasury_agents = [
            NumeiaTreasuryAgent()
        ]
        
        # Layer 2 - Compliance / Radar
        self.compliance_agents = [
            InstitutionalRadarAgent(),
            HFTManagerAgent()
        ]
        
        # Layer 1 - Traders
        self.trader_agents = [
            QuantumScoutProAgent(),
            Apollo11QuantumAgent()
        ]
        
        logging.info("All layers initialized successfully.")
        
    def get_system_status(self) -> Dict[str, Any]:
        """Returns the status of all active agents."""
        status_report = {}
        for agents, layer_name in zip(
            [self.brain_agents, self.treasury_agents, self.compliance_agents, self.trader_agents],
            ["Layer 4 (Brain)", "Layer 3 (Treasury)", "Layer 2 (Compliance)", "Layer 1 (Traders)"]
        ):
            status_report[layer_name] = [agent.info() for agent in agents]
            
        return status_report

    def run_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a full tick cycle of the ecosystem, now strictly disciplined by the Orchestral Harmonization.
        """
        asset = market_data.get("symbol", "UNKNOWN")
        logging.info(f"--- Starting OMEGA Cycle for {asset} ---")
        
        # 1. Tuning Fork (Identify the Musical Scale)
        from .harmonization import AssetSignatureMatrix, MarketRegimeDetector
        asset_scale = AssetSignatureMatrix.get_signature(asset)
        market_regime = MarketRegimeDetector.detect_regime(market_data)
        
        logging.info(f"[MAESTRO] Tuning Instruments for {asset} | Scale: {asset_scale['tempo']} | Regime: {market_regime}")
        
        # Phase 1: Brain Analysis (Macro & Fractal)
        logging.info("1. Executing Brain Agents...")
        brain_state = {}
        for agent in self.brain_agents:
            brain_state[agent.name] = agent.process(market_data)
            
        current_context = {"market_data": market_data, "brain_insights": brain_state, "asset_scale": asset_scale, "regime": market_regime}
        
        # Phase 2: Treasury Allocation
        logging.info("2. Executing Treasury Strategy...")
        treasury_state = {}
        for agent in self.treasury_agents:
            treasury_state[agent.name] = agent.process(current_context)
            
        current_context["treasury_directives"] = treasury_state
        
        # Phase 3: Compliance & Radar Scanning
        logging.info("3. Scanning Flow Toxicity & Risk Limits...")
        compliance_state = {}
        radar_clear = True
        for agent in self.compliance_agents:
            # Inject dynamic limits based on the asset scale into the agent's context 
            res = agent.process(current_context)
            compliance_state[agent.name] = res
            
            # Simple veto logic based on Radar
            if "anomaly_detected" in res and res["anomaly_detected"]:
                radar_clear = False
                logging.warning(f"Compliance VETO triggered by {agent.name}. Halting Execution.")
                break
                
        current_context["compliance_status"] = compliance_state
        
        # Phase 4: Quantum Execution (Only if the instrument is allowed to play on this scale)
        trader_actions = {}
        if radar_clear:
            logging.info("4. Executing Trades (Radar Clear & Tempo Checked)...")
            allowed_instruments = asset_scale.get("allowed_agents", [])
            for agent in self.trader_agents:
                if agent.name in allowed_instruments:
                    trader_actions[agent.name] = agent.process(current_context)
                else:
                    logging.info(f"[MAESTRO] Silencing {agent.name} -> Not tuned for {asset_scale['name']} ({asset}).")
        else:
            logging.info("4. Execution Halted due to Compliance VETO.")
            
        logging.info(f"--- OMEGA Cycle Completed ---")

        
        return {
            "cycle_status": "SUCCESS",
            "brain": brain_state,
            "treasury": treasury_state,
            "compliance": compliance_state,
            "execution": trader_actions
        }

if __name__ == "__main__":
    hub = OmegaEcosystemHub()
    # Dummy tick
    tick_data = {"symbol": "EURUSD", "timestamp": time.time(), "price": 1.0500}
    hub.run_cycle(tick_data)
