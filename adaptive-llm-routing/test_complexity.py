from src.graph.builder import build_adaptive_graph

prompt = """
First analyze the problem, then design the solution. After that, compare SQL
and NoSQL databases and evaluate their differences. Next, implement a concurrent
transaction system using Python.

Why is one architecture better than another?
How can race conditions and deadlocks be prevented?
Calculate the throughput using 10000 * 5 = 50000 operations per second.
Calculate time and space complexity.

Compare synchronous and asynchronous communication. Analyze scalability,
reliability, consistency, fault tolerance, latency, and performance.

First design the database layer, then design the API layer, after that design
Redis caching, and finally design Kafka messaging.

Write Python code using classes, functions, imports, and a code block.
Explain every step, analyze the design, evaluate the trade-offs, justify the
decisions, and explain why the final architecture is optimal.

```python
import redis

class TransactionManager:
    def process_transaction(self):
        return True

def process_payment():
    return True
"""

graph = build_adaptive_graph()

state = graph.invoke({
"task_id": "phase1-complex-test",
"prompt": prompt,
"task_type": "reasoning",
"ground_truth": ""
})

print("COMPLEXITY:", state.get("complexity_score"))
print("ROUTE:", state.get("route"))
print("CONFIDENCE:", state.get("routing_confidence"))
print("MODEL:", state.get("model_used"))
print("QUALITY:", state.get("quality_score"))
print("LATENCY:", state.get("latency_seconds"))
print("STEPS:", len(state.get("intermediate_steps", [])))
print("ERROR:", state.get("error"))

print("\nRESPONSE:")
print(state.get("response", "")[:1000])