#!/usr/bin/env python3
import os
import json
import sys

# --- ANSI Terminal Color Escape Codes ---
CLR_RESET = "\033[0m"
CLR_RED   = "\033[31m"
CLR_GRN   = "\033[32m"
CLR_YLW   = "\033[33m"
CLR_CYN   = "\033[36m"
B_WHITE   = "\033[1;37m"

def parse_automation_report(report_path):
    """
    Parses an Unreal Engine UAT index.json report and prints a colorized summary.
    """
    if not os.path.exists(report_path):
        print(f"{CLR_RED}❌ ERROR: Test report file not found at: {report_path}{CLR_RESET}")
        sys.exit(1)

    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"{CLR_RED}❌ ERROR: Failed to parse index.json. File is corrupted or invalid.{CLR_RESET}")
        sys.exit(1)

    # Extract global testing metadata
    total_tests = data.get("totalNumTests", 0)
    passed_tests = data.get("numPass", 0)
    failed_tests = data.get("numFail", 0)
    skipped_tests = data.get("numSkip", 0)
    duration_sec = data.get("totalDurationSec", 0.0)
    tests_list = data.get("tests", [])

    print(f"\n{B_WHITE}====================================================={CLR_RESET}")
    print(f"{B_WHITE}🧪 AUTOMATION PIPELINE TEST RESULTS SUMMARY{CLR_RESET}")
    print(f"{B_WHITE}====================================================={CLR_RESET}")
    print(f"Total Evaluated : {total_tests}")
    print(f"Passed          : {CLR_GRN}{passed_tests}{CLR_RESET}")
    print(f"Failed          : {CLR_RED if failed_tests > 0 else CLR_RESET}{failed_tests}{CLR_RESET}")
    print(f"Skipped         : {CLR_YLW if skipped_tests > 0 else CLR_RESET}{skipped_tests}{CLR_RESET}")
    print(f"Total Duration  : {duration_sec:.2f} seconds")
    print(f"{B_WHITE}----------------------------------------------------={CLR_RESET}\n")

    print(f"{B_WHITE}📋 DETAILED TEST CASE BREAKDOWN:{CLR_RESET}")
    
    # Track if our critical physics/chemical suites hit a wall
    critical_failure_detected = False

    for test in tests_list:
        test_name = test.get("testDisplayName", "Unnamed Test")
        full_name = test.get("fullTestPath", "")
        state = test.get("state", "Unknown").upper()
        errors_count = test.get("numErrors", 0)
        
        # Colorize line entries based on test state outcomes
        if state == "SUCCESS" or state == "PASS":
            status_tag = f"{CLR_GRN}[PASS]{CLR_RESET}"
        elif state == "FAIL":
            status_tag = f"{CLR_RED}[FAIL]{CLR_RESET}"
            # If our specific subsystems fail, flag it for rigorous pipeline tracking
            if "Pycnogonid" in full_name or "Substep" in full_name:
                critical_failure_detected = True
        else:
            status_tag = f"{CLR_YLW}[{state}]{CLR_RESET}"

        print(f" {status_tag} {test_name}")
        
        # Output associated error logs to stdout if the test failed
        if errors_count > 0:
            entries = test.get("entries", [])
            for entry in entries:
                if entry.get("event", "").upper() == "ERROR":
                    print(f"      {CLR_RED}└── ⚠️ {entry.get('message')}{CLR_RESET}")

    print(f"\n{B_WHITE}====================================================={CLR_RESET}")

    # Enforce strict exit codes for automated Bash/CI systems
    if failed_tests > 0:
        if critical_failure_detected:
            print(f"{CLR_RED}❌ PIPELINE CRITICAL FAIL: Pycnogonid physics or chemical subsystems failed constraints!{CLR_RESET}\n")
        else:
            print(f"{CLR_RED}❌ PIPELINE FAILURE: Test cases returned errors.{CLR_RESET}\n")
        sys.exit(1)
    else:
        print(f"{CLR_GRN}🚀 PIPELINE SUCCESS: All custom math and step matrices verified clean!{CLR_RESET}\n")
        sys.exit(0)

if __name__ == "__main__":
    # Path matches the REPORT_DIR variable configured inside the Bash script runner
    DEFAULT_REPORT_PATH = "Saved/AutomationReports/index.json"
    
    # Allow overriding the path via command line argument if needed
    target_report = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPORT_PATH
    parse_automation_report(target_report)
