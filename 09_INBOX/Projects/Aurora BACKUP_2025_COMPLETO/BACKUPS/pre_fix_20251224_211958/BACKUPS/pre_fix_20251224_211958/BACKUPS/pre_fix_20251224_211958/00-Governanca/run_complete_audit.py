#!/usr/bin/env python3
"""
AURORA PROJECT - COMPLETE AUDIT RUNNER
Execute this script to generate complete audit reports automatically

Usage:
    python run_complete_audit.py

This will:
1. Run complete audit of all modules
2. Generate comprehensive reports (Markdown, JSON, HTML, Executive Summary)
3. Save reports to 05-Documentacao/Audit-Reports/
4. Create latest copies in 05-Documentacao/Latest-Reports/
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Aurora.AuditRunner")

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_complete_report import ReportGenerator, AutoUpdateSystem

def main():
    """Main execution"""
    print("="*80)
    print("AURORA PROJECT - COMPLETE AUDIT SYSTEM")
    print("="*80)
    print(f"\nStarted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}\n")
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Project Root: {project_root}")
    print(f"Output Directory: {project_root / '05-Documentacao' / 'Audit-Reports'}\n")
    
    try:
        # Initialize generator
        print("Initializing report generator...")
        generator = ReportGenerator(str(project_root))
        
        # Generate all reports
        print("\n" + "-"*80)
        print("RUNNING COMPLETE AUDIT")
        print("-"*80)
        print("\nThis process includes:")
        print("  1. Code analysis of all modules")
        print("  2. Security audit")
        print("  3. Compliance assessment")
        print("  4. Integration analysis")
        print("  5. Conflict of interest analysis")
        print("  6. Risk assessment")
        print("  7. Report generation")
        print("\nPlease wait...\n")
        
        reports = generator.generate_all_reports()
        
        # Auto-update system
        print("\n" + "-"*80)
        print("UPDATING LATEST REPORTS")
        print("-"*80)
        auto_update = AutoUpdateSystem(str(project_root))
        auto_update.update_reports()
        
        # Summary
        print("\n" + "="*80)
        print("AUDIT COMPLETE - REPORTS GENERATED")
        print("="*80)
        print("\nGenerated Reports:")
        for report_type, report_path in reports.items():
            if report_path:
                file_size = Path(report_path).stat().st_size / 1024  # KB
                print(f"  [OK] {report_type.upper():12s}: {Path(report_path).name}")
                print(f"     Size: {file_size:.1f} KB")
                print(f"     Path: {report_path}\n")
        
        # Latest reports location
        latest_dir = project_root / "05-Documentacao" / "Latest-Reports"
        print(f"\nLatest Reports Location: {latest_dir}")
        print("\n" + "="*80)
        print("SUCCESS - All reports generated and updated!")
        print("="*80)
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S CET')}\n")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during audit: {e}", exc_info=True)
        print(f"\n[ERROR] {e}")
        return 1

if __name__ == "__main__":
    exit(main())

