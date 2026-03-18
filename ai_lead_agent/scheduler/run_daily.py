from apscheduler.schedulers.blocking import BlockingScheduler
import os
import sys

# ---------------------------
# Fix import path
# ---------------------------

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from main import graph
    print("✅ Successfully imported graph from main")
except ImportError as e:
    print(f"❌ ImportError: {e}")
    sys.exit(1)


def run_agent():
    print("\n🚀 Running AI Lead Agent...")
    graph.invoke({})
    print("✅ Run finished\n")


# RUN ONCE IMMEDIATELY
run_agent()

scheduler = BlockingScheduler()

# Run everyday at 9 AM
scheduler.add_job(run_agent, "cron", hour=9)

print("⏳ Scheduler started... waiting for next run")

scheduler.start()