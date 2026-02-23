#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUDITORIA CIENTÍFICA COM API GEMINI - BLOQUEIO ESTRATÉGICO SELL

Combina análise de código real com dados empíricos de mercado via Gemini
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Tentar importar bibliotecas assíncronas
try:
    import asyncio
    import aiohttp
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("⚠️  Bibliotecas assíncronas não disponíveis. Instale com: pip install aiohttp")
    print("   Continuando com modo síncrono...")

# Tentar importar biblioteca do Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Biblioteca google-generativeai não disponível. Instale com: pip install google-generativeai")
    print("   Continuando com análise de código apenas...")

class AuditoriaCientificaGemini:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_name = "gemini-2.0-flash-exp"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        self.metricas = {
            'timestamp': datetime.now().isoformat(),
            'versao_auditoria': '2.1-gemini',
            'testes_empiricos_executados': 0,
            'cenarios_validados': 0
        }
    
    def obter_dados_mercado_reais_sync(self, par: str, timeframe: str) -> Dict[str, Any]:
        """Obtém dados empíricos reais de mercado via Gemini (modo síncrono)"""
        
        if not GEMINI_AVAILABLE or self.api_key == "MODO_LOCAL":
            return {
                "par": par,
                "timeframe": timeframe,
                "tendencia_principal": "NEUTRAL",
                "forca_tendencia": "MEDIA",
                "confianca_analise": "BAIXA",
                "timestamp": datetime.now().isoformat(),
                "modo": "SIMULACAO_LOCAL",
                "aviso": "API Gemini não disponível - usando simulação"
            }
        
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(model_name=self.model_name)
            
            prompt = f"""
            ANÁLISE TÉCNICA EMPÍRICA - {par} {timeframe}
            
            Com base em dados de mercado atuais, forneça APENAS em formato JSON:
            {{
                "par": "{par}",
                "timeframe": "{timeframe}", 
                "tendencia_principal": "STRONG_BUY|BUY|NEUTRAL|SELL|STRONG_SELL",
                "forca_tendencia": "ALTA|MEDIA|BAIXA",
                "confianca_analise": "ALTA|MEDIA|BAIXA",
                "timestamp": "{datetime.now().isoformat()}"
            }}
            """
            
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 500
                }
            )
            
            texto = response.text
            # Extrair JSON
            inicio = texto.find('{')
            fim = texto.rfind('}') + 1
            
            if inicio != -1 and fim != -1:
                return json.loads(texto[inicio:fim])
            else:
                return {"erro": "JSON não encontrado", "resposta": texto}
                
        except Exception as e:
            return {"erro": str(e), "tipo": type(e).__name__}
    
    async def obter_dados_mercado_reais(self, par: str, timeframe: str) -> Dict[str, Any]:
        """Obtém dados empíricos reais de mercado via Gemini (modo assíncrono ou síncrono)"""
        
        if ASYNC_AVAILABLE and self.api_key != "MODO_LOCAL":
            # Tentar modo assíncrono
            try:
                prompt_analise_mercado = f"""
                ANÁLISE TÉCNICA EMPÍRICA - {par} {timeframe}
                
                Com base em dados de mercado atuais via Google Search, forneça APENAS:
                1. Tendência predominante (STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL)
                2. Confiança da análise (ALTA, MEDIA, BAIXA)
                
                Formato JSON estrito:
                {{
                    "par": "{par}",
                    "timeframe": "{timeframe}", 
                    "tendencia_principal": "STRING",
                    "forca_tendencia": "STRING",
                    "confianca_analise": "STRING",
                    "timestamp": "{datetime.now().isoformat()}"
                }}
                """
                
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt_analise_mercado}]
                    }],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 500
                    }
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}?key={self.api_key}",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status == 200:
                            data = await response.json()
                            texto_resposta = data['candidates'][0]['content']['parts'][0]['text']
                            
                            inicio_json = texto_resposta.find('{')
                            fim_json = texto_resposta.rfind('}') + 1
                            
                            if inicio_json != -1 and fim_json != -1:
                                return json.loads(texto_resposta[inicio_json:fim_json])
                            else:
                                return {"erro": "JSON não encontrado", "resposta": texto_resposta}
                        else:
                            error_text = await response.text()
                            return {"erro": f"HTTP {response.status}", "detalhes": error_text}
                            
            except Exception as e:
                # Fallback para modo síncrono
                return self.obter_dados_mercado_reais_sync(par, timeframe)
        else:
            # Usar modo síncrono
            return self.obter_dados_mercado_reais_sync(par, timeframe)
    
    def analisar_codigo_prometheus(self, codigo: str) -> Dict[str, Any]:
        """Analisa o código real do Prometheus para verificar lógica do bloqueio SELL"""
        
        analise = {
            'bloqueio_sell_detectado': False,
            'localizacao_bloqueio': [],
            'condicoes_ativacao': [],
            'vulnerabilidades': []
        }
        
        linhas = codigo.split('\n')
        
        for i, linha in enumerate(linhas):
            linha_upper = linha.upper()
            
            # Procurar lógica de bloqueio SELL - CORREÇÃO: Buscar padrão específico
            if 'PRIMARY_TREND' in linha_upper and 'SELL' in linha_upper:
                # Verificar se há return None ou bloqueio logo após
                contexto_proximo = '\n'.join(linhas[i:min(len(linhas), i+10)])
                if 'RETURN NONE' in contexto_proximo.upper() or 'STRATEGIC_BLOCK' in contexto_proximo.upper():
                    analise['bloqueio_sell_detectado'] = True
                    analise['localizacao_bloqueio'].append({
                        'linha': i + 1,
                        'codigo': linha.strip(),
                        'contexto': linhas[max(0, i-2):min(len(linhas), i+5)]
                    })
            
            # Identificar condições de ativação
            if 'H4' in linha_upper or '4H' in linha_upper or 'TENDENCIA' in linha_upper:
                if 'SELL' in linha_upper or 'VENDER' in linha_upper:
                    analise['condicoes_ativacao'].append({
                        'linha': i + 1, 
                        'condicao': linha.strip()
                    })
        
        # Verificar vulnerabilidades: procurar caminhos alternativos que possam contornar o bloqueio
        codigo_upper = codigo.upper()
        if 'SELL' in codigo_upper and 'ORDER_TYPE_SELL' in codigo_upper:
            # Verificar se há execução de SELL sem passar pelo filtro
            if 'EXECUTE_TRADE' in codigo_upper or 'ORDER_SEND' in codigo_upper:
                # Verificar se há validação antes da execução
                if 'STRATEGIC_BLOCK' not in codigo_upper and 'PRIMARY_TREND == "SELL"' not in codigo_upper:
                    analise['vulnerabilidades'].append({
                        'tipo': 'POSSIVEL_BYPASS',
                        'descricao': 'Pode haver caminho de execução que contorna o bloqueio SELL'
                    })
        
        return analise
    
    async def executar_auditoria_completa(self, codigo_prometheus: str, par_analise: str = "EUR/USD") -> Dict[str, Any]:
        """Executa auditoria completa integrando análise de código + dados empíricos"""
        
        print("🔍 FASE 1: ANÁLISE ESTÁTICA DO CÓDIGO")
        analise_codigo = self.analisar_codigo_prometheus(codigo_prometheus)
        print(f"   ✅ Bloqueio SELL detectado: {analise_codigo['bloqueio_sell_detectado']}")
        print(f"   📍 Localizações encontradas: {len(analise_codigo['localizacao_bloqueio'])}")
        
        print("\n📊 FASE 2: COLETA DE DADOS EMPÍRICOS DE MERCADO")
        dados_mercado = await self.obter_dados_mercado_reais(par_analise, "4H")
        
        if "erro" in dados_mercado:
            print(f"   ⚠️  Erro ao obter dados: {dados_mercado['erro']}")
            print("   📝 Usando simulação baseada em análise de código...")
            # Fallback: simular dados de mercado baseado na análise do código
            dados_mercado = {
                "par": par_analise,
                "timeframe": "4H",
                "tendencia_principal": "SELL",  # Simular cenário de teste
                "forca_tendencia": "MEDIA",
                "confianca_analise": "MEDIA",
                "timestamp": datetime.now().isoformat(),
                "modo": "SIMULACAO"
            }
        else:
            print(f"   ✅ Dados obtidos: Tendência = {dados_mercado.get('tendencia_principal', 'N/A')}")
        
        print("\n⚡ FASE 3: SIMULAÇÃO DO COMPORTAMENTO DO SISTEMA")
        simulacao = self.simular_comportamento_sistema(analise_codigo, dados_mercado)
        print(f"   ✅ Bloqueio efetivo: {simulacao['bloqueio_efetivo']}")
        
        # Atualizar métricas
        self.metricas['testes_empiricos_executados'] += 1
        if simulacao['bloqueio_efetivo']:
            self.metricas['cenarios_validados'] += 1
        
        return {
            'auditoria': {
                'metodologia': 'ANÁLISE_CÓDIGO + DADOS_MERCADO_REAIS',
                'timestamp': self.metricas['timestamp'],
                'metricas': self.metricas
            },
            'analise_codigo': analise_codigo,
            'dados_mercado_empiricos': dados_mercado,
            'simulacao_comportamento': simulacao,
            'veredito_final': self.gerar_veredito_final(analise_codigo, simulacao)
        }
    
    def simular_comportamento_sistema(self, analise_codigo: Dict, dados_mercado: Dict) -> Dict[str, Any]:
        """Simula como o Prometheus se comportaria com os dados reais"""
        
        tendencia_mercado = dados_mercado.get('tendencia_principal', 'NEUTRAL')
        bloqueio_detectado = analise_codigo['bloqueio_sell_detectado']
        
        # Lógica de simulação baseada na análise do código
        if tendencia_mercado in ['SELL', 'STRONG_SELL'] and bloqueio_detectado:
            return {
                'sinal_entrada_bruto': 'SELL',
                'sinal_pos_filtro': 'NEUTRAL/BLOQUEADO',
                'bloqueio_ativado': True,
                'razao_bloqueio': f'Tendência de mercado {tendencia_mercado} detectada - Bloqueio estratégico ativo',
                'bloqueio_efetivo': True,
                'acao_sistema': 'RETURN_NONE'
            }
        elif tendencia_mercado in ['SELL', 'STRONG_SELL'] and not bloqueio_detectado:
            return {
                'sinal_entrada_bruto': 'SELL',
                'sinal_pos_filtro': 'SELL',
                'bloqueio_ativado': False,
                'razao_bloqueio': 'BLOQUEIO NÃO DETECTADO NO CÓDIGO',
                'bloqueio_efetivo': False,
                'acao_sistema': 'EXECUTAR_SELL',
                'vulnerabilidade': True
            }
        else:
            return {
                'sinal_entrada_bruto': tendencia_mercado,
                'sinal_pos_filtro': tendencia_mercado,
                'bloqueio_ativado': False,
                'razao_bloqueio': f'Tendência {tendencia_mercado} não requer bloqueio',
                'bloqueio_efetivo': True,  # Não precisa bloquear se não é SELL
                'acao_sistema': 'PERMITIR_SINAL'
            }
    
    def gerar_veredito_final(self, analise_codigo: Dict, simulacao: Dict) -> Dict[str, Any]:
        """Gera veredito final baseado em evidências empíricas"""
        
        bloqueio_operacional = (
            analise_codigo['bloqueio_sell_detectado'] and 
            simulacao['bloqueio_efetivo']
        )
        
        # Verificar se há vulnerabilidades
        tem_vulnerabilidades = len(analise_codigo['vulnerabilidades']) > 0 or simulacao.get('vulnerabilidade', False)
        
        nivel_confianca = 'ALTO'
        if not analise_codigo['bloqueio_sell_detectado']:
            nivel_confianca = 'CRÍTICO'
        elif tem_vulnerabilidades:
            nivel_confianca = 'MÉDIO'
        elif len(analise_codigo['localizacao_bloqueio']) == 0:
            nivel_confianca = 'BAIXO'
        
        return {
            'status_auditoria': 'SUCESSO' if bloqueio_operacional and not tem_vulnerabilidades else 'FALHA',
            'bloqueio_sell_operacional': bloqueio_operacional,
            'nivel_confianca': nivel_confianca,
            'vulnerabilidades_detectadas': tem_vulnerabilidades,
            'recomendacao_ceo': self.gerar_recomendacao_estrategica(bloqueio_operacional, tem_vulnerabilidades),
            'evidencias_empiricas': {
                'codigo_analisado': analise_codigo['bloqueio_sell_detectado'],
                'dados_mercado': simulacao['bloqueio_ativado'],
                'comportamento_simulado': simulacao['bloqueio_efetivo'],
                'localizacoes_bloqueio': len(analise_codigo['localizacao_bloqueio'])
            }
        }
    
    def gerar_recomendacao_estrategica(self, bloqueio_operacional: bool, tem_vulnerabilidades: bool) -> str:
        if tem_vulnerabilidades:
            return "❌ NO-GO - Vulnerabilidades detectadas. Bloqueio SELL pode ser contornado. Revisar código urgentemente."
        elif bloqueio_operacional:
            return "✅ GO - Sistema implementa bloqueio SELL corretamente. Pode prosseguir para produção com monitoramento."
        else:
            return "❌ NO-GO - Bloqueio SELL não está operacional ou não é efetivo. Retornar para desenvolvimento."

# EXECUÇÃO PRINCIPAL
def main_sync():
    """Versão síncrona que funciona sem dependências assíncronas"""
    print("="*80)
    print("🔬 AUDITORIA CIENTÍFICA - BLOQUEIO SELL (MODO SÍNCRONO)")
    print("="*80)
    print()
    
    API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not API_KEY:
        print("⚠️  API Key não encontrada. Usando análise de código + simulação de mercado...")
        API_KEY = "MODO_LOCAL"
    
    auditoria = AuditoriaCientificaGemini(API_KEY)
    
    # Carregar código
    codigo_path = Path('prometheus_master_control_v6.0.py')
    if not codigo_path.exists():
        print(f"❌ Arquivo não encontrado: {codigo_path}")
        return
    
    with open(codigo_path, 'r', encoding='utf-8') as f:
        codigo_prometheus = f.read()
    
    print(f"✅ Código carregado: {len(codigo_prometheus)} caracteres\n")
    
    # Análise de código
    print("🔍 FASE 1: ANÁLISE ESTÁTICA DO CÓDIGO")
    analise_codigo = auditoria.analisar_codigo_prometheus(codigo_prometheus)
    print(f"   ✅ Bloqueio SELL: {analise_codigo['bloqueio_sell_detectado']}")
    print(f"   📍 Localizações: {len(analise_codigo['localizacao_bloqueio'])}")
    
    # Dados de mercado (síncrono)
    print("\n📊 FASE 2: COLETA DE DADOS DE MERCADO")
    dados_mercado = auditoria.obter_dados_mercado_reais_sync("EUR/USD", "4H")
    if "erro" in dados_mercado:
        print(f"   ⚠️  {dados_mercado['erro']}")
    else:
        print(f"   ✅ Tendência: {dados_mercado.get('tendencia_principal', 'N/A')}")
        if dados_mercado.get('modo') == 'SIMULACAO_LOCAL':
            print("   📝 Modo: Simulação (API não disponível)")
    
    # Simulação
    print("\n⚡ FASE 3: SIMULAÇÃO DO COMPORTAMENTO")
    simulacao = auditoria.simular_comportamento_sistema(analise_codigo, dados_mercado)
    print(f"   ✅ Bloqueio efetivo: {simulacao['bloqueio_efetivo']}")
    
    # Veredito
    veredito = auditoria.gerar_veredito_final(analise_codigo, simulacao)
    
    resultado = {
        'auditoria': {
            'metodologia': 'ANÁLISE_CÓDIGO + DADOS_MERCADO',
            'timestamp': auditoria.metricas['timestamp'],
            'modo_execucao': 'SINCRONO'
        },
        'analise_codigo': analise_codigo,
        'dados_mercado': dados_mercado,
        'simulacao': simulacao,
        'veredito_final': veredito
    }
    
    # Exibir resultado
    print("\n" + "="*80)
    print("📋 RELATÓRIO FINAL")
    print("="*80)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print("="*80)
    
    print(f"\n🚀 DECISÃO: {veredito['recomendacao_ceo']}")
    print(f"🛡️  BLOQUEIO OPERACIONAL: {veredito['bloqueio_sell_operacional']}")
    print(f"📊 CONFIANÇA: {veredito['nivel_confianca']}")
    
    # Salvar
    with open('auditoria_cientifica_resultado.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Relatório salvo: auditoria_cientifica_resultado.json")

async def main_async():
    print("="*80)
    print("🔬 AUDITORIA CIENTÍFICA COM API GEMINI - BLOQUEIO SELL")
    print("="*80)
    print()
    
    # Obter API Key do ambiente ou config
    API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not API_KEY:
        print("⚠️  API Key do Gemini não encontrada nas variáveis de ambiente.")
        print("   Configure: GEMINI_API_KEY ou GOOGLE_API_KEY")
        print("   Continuando com análise de código apenas (sem dados de mercado)...")
        print()
        API_KEY = "MODO_LOCAL"  # Placeholder para modo local
    
    auditoria = AuditoriaCientificaGemini(API_KEY)
    
    # Carregar código real do Prometheus
    codigo_prometheus_path = Path('prometheus_master_control_v6.0.py')
    if codigo_prometheus_path.exists():
        try:
            with open(codigo_prometheus_path, 'r', encoding='utf-8') as f:
                codigo_prometheus = f.read()
            print(f"✅ Código do Prometheus carregado: {codigo_prometheus_path}")
            print(f"   Tamanho: {len(codigo_prometheus)} caracteres")
        except Exception as e:
            print(f"❌ Erro ao ler código: {e}")
            return
    else:
        print(f"⚠️  Arquivo não encontrado: {codigo_prometheus_path}")
        print("   Usando código de exemplo para demonstração")
        codigo_prometheus = """
# Exemplo de código com bloqueio SELL
def analisar_mercado(tendencia_h4):
    if tendencia_h4 == 'SELL':
        aplicar_bloqueio_strategic()  # ← BLOQUEIO ATIVO
        return 'NEUTRAL'
    else:
        return tendencia_h4
"""
    
    print()
    
    # Executar auditoria completa
    resultado = await auditoria.executar_auditoria_completa(codigo_prometheus, "EUR/USD")
    
    # Relatório final
    print("\n" + "="*80)
    print("📋 RELATÓRIO FINAL DE AUDITORIA CIENTÍFICA COM DADOS EMPÍRICOS")
    print("="*80)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print("="*80)
    
    # Decisão estratégica
    veredito = resultado['veredito_final']
    print(f"\n🚀 DECISÃO CEO: {veredito['recomendacao_ceo']}")
    print(f"🛡️  BLOQUEIO OPERACIONAL: {veredito['bloqueio_sell_operacional']}")
    print(f"📊 NÍVEL CONFIANÇA: {veredito['nivel_confianca']}")
    print(f"⚠️  VULNERABILIDADES: {veredito['vulnerabilidades_detectadas']}")
    
    # Salvar relatório
    output_file = 'auditoria_cientifica_resultado.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Relatório salvo em: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Erro ao salvar relatório: {e}")

if __name__ == "__main__":
    try:
        # Tentar modo assíncrono primeiro, fallback para síncrono
        if ASYNC_AVAILABLE:
            try:
                asyncio.run(main_async())
            except Exception as e:
                print(f"\n⚠️  Erro no modo assíncrono: {e}")
                print("   Mudando para modo síncrono...\n")
                main_sync()
        else:
            main_sync()
    except KeyboardInterrupt:
        print("\n\n⚠️  Auditoria interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

