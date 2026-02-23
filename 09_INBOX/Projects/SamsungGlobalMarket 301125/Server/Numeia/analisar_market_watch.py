#!/usr/bin/env python3
"""
Script para Analisar Market Watch CSV e Identificar Símbolos Disponíveis
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict

def ler_csv_market_watch(arquivo: str) -> List[Dict]:
    """Lê o arquivo CSV do Market Watch do MT5"""
    simbolos = []
    
    # Tentar diferentes encodings
    encodings = ['utf-16', 'utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(arquivo, 'r', encoding=encoding) as f:
                # Ler linha por linha para detectar o formato
                lines = f.readlines()
                
                # Procurar cabeçalho
                header_line = None
                for i, line in enumerate(lines):
                    if 'Symbol' in line or 'Símbolo' in line or 'Symbol' in line:
                        header_line = i
                        break
                
                if header_line is None:
                    # Tentar ler diretamente
                    f.seek(0)
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        if 'Symbol' in row or list(row.keys())[0]:
                            key = list(row.keys())[0] if row.keys() else 'Symbol'
                            simbolo = row.get(key, row.get('Symbol', ''))
                            if simbolo and simbolo.strip():
                                simbolos.append({
                                    'symbol': simbolo.strip(),
                                    'bid': row.get('Bid', row.get(list(row.keys())[1] if len(row.keys()) > 1 else '', '')),
                                    'ask': row.get('Ask', row.get(list(row.keys())[2] if len(row.keys()) > 2 else '', '')),
                                })
                else:
                    # Ler com cabeçalho detectado
                    f.seek(0)
                    for i, line in enumerate(f):
                        if i <= header_line:
                            continue
                        parts = line.strip().split(';')
                        if len(parts) >= 2:
                            simbolos.append({
                                'symbol': parts[0].strip(),
                                'bid': parts[1].strip() if len(parts) > 1 else '',
                                'ask': parts[2].strip() if len(parts) > 2 else '',
                            })
            
            if simbolos:
                print(f"[OK] Arquivo lido com encoding: {encoding}")
                break
        except Exception as e:
            continue
    
    return simbolos

def encontrar_simbolos_relevantes(simbolos: List[Dict], procurados: List[str]) -> Dict:
    """Encontra símbolos relevantes e suas alternativas"""
    resultado = {
        'encontrados': {},
        'alternativas': {},
        'nao_encontrados': []
    }
    
    simbolos_lower = {s['symbol'].upper(): s for s in simbolos}
    
    for procurado in procurados:
        procurado_upper = procurado.upper()
        
        # Busca exata
        if procurado_upper in simbolos_lower:
            resultado['encontrados'][procurado] = simbolos_lower[procurado_upper]
        else:
            # Buscar alternativas
            alternativas = []
            
            # Buscar por padrões comuns
            for simbolo, info in simbolos_lower.items():
                # SPX500 -> US500, SPX, SP500, etc.
                if procurado_upper == 'SPX500':
                    if 'US500' in simbolo or 'SP500' in simbolo or 'SPX' in simbolo:
                        alternativas.append((simbolo, info))
                # Outros padrões podem ser adicionados aqui
            
            if alternativas:
                resultado['alternativas'][procurado] = alternativas
            else:
                resultado['nao_encontrados'].append(procurado)
    
    return resultado

def main():
    csv_file = r"c:\Users\Lenovo\Documents\Market Watch 20251121 130734.csv"
    
    print("=" * 70)
    print("ANÁLISE DE MARKET WATCH - MetaTrader 5")
    print("=" * 70)
    print()
    
    if not Path(csv_file).exists():
        print(f"[ERRO] Arquivo não encontrado: {csv_file}")
        return
    
    print(f"[INFO] Lendo arquivo: {csv_file}")
    simbolos = ler_csv_market_watch(csv_file)
    
    if not simbolos:
        print("[ERRO] Não foi possível ler símbolos do arquivo")
        print("[INFO] Tentando método alternativo...")
        
        # Método alternativo: ler como texto simples
        try:
            with open(csv_file, 'rb') as f:
                content = f.read()
                # Tentar detectar encoding
                if content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
                    content = content.decode('utf-16')
                else:
                    content = content.decode('utf-8', errors='ignore')
                
                lines = content.split('\n')
                print(f"[INFO] Total de linhas: {len(lines)}")
                
                for line in lines[1:10]:  # Primeiras linhas para debug
                    parts = line.split(';')
                    if parts and parts[0].strip():
                        print(f"  Linha exemplo: {parts[0].strip()}")
        except Exception as e:
            print(f"[ERRO] {e}")
        
        return
    
    print(f"[OK] {len(simbolos)} símbolos encontrados")
    print()
    
    # Símbolos que estamos procurando
    simbolos_procurados = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'SPX500', 'US500']
    
    print("[INFO] Buscando símbolos relevantes...")
    resultado = encontrar_simbolos_relevantes(simbolos, simbolos_procurados)
    
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    if resultado['encontrados']:
        print("\n[OK] Símbolos encontrados:")
        for simbolo, info in resultado['encontrados'].items():
            print(f"  ✅ {simbolo}")
    
    if resultado['alternativas']:
        print("\n[AVISO] Alternativas encontradas:")
        for simbolo, alternativas in resultado['alternativas'].items():
            print(f"  ⚠️  {simbolo} não encontrado, mas encontradas alternativas:")
            for alt, info in alternativas:
                print(f"     → {alt}")
    
    if resultado['nao_encontrados']:
        print("\n[ERRO] Símbolos não encontrados:")
        for simbolo in resultado['nao_encontrados']:
            print(f"  ❌ {simbolo}")
    
    # Buscar US500 especificamente
    print("\n" + "=" * 70)
    print("BUSCA ESPECÍFICA")
    print("=" * 70)
    
    simbolos_500 = [s for s in simbolos if '500' in s['symbol'].upper() or 'SPX' in s['symbol'].upper() or 'SP500' in s['symbol'].upper()]
    if simbolos_500:
        print("\n[OK] Símbolos relacionados a S&P 500 encontrados:")
        for s in simbolos_500[:10]:  # Primeiros 10
            print(f"  ✅ {s['symbol']}")
    else:
        print("\n[AVISO] Nenhum símbolo S&P 500 encontrado")
    
    # Verificar símbolos principais
    principais = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
    print("\n[INFO] Verificando símbolos principais no config:")
    simbolos_lower = {s['symbol'].upper(): s for s in simbolos}
    for principal in principais:
        if principal.upper() in simbolos_lower:
            print(f"  ✅ {principal}")
        else:
            print(f"  ❌ {principal} NÃO encontrado")

if __name__ == "__main__":
    main()

