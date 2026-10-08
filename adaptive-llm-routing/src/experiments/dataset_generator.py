"""
Dataset Generator — creates a diverse 50-task benchmark dataset
with GSM8K-style math problems, code tasks, reasoning, and general QA.

Each task has:
  - task_id, prompt, task_type, difficulty, ground_truth (where available)
"""

import json
from pathlib import Path

# we'll also pull a subset from HuggingFace datasets (GSM8K) if available

BENCHMARK_TASKS = [
    # ═══════════════════════════════════════════════════════════════════════
    # SIMPLE TASKS (15 tasks) — should route to Single LLM
    # ═══════════════════════════════════════════════════════════════════════

    # General QA
    {"task_id": "simple_gen_01", "prompt": "What is the capital of France?", "task_type": "general", "difficulty": "simple", "ground_truth": "Paris"},
    {"task_id": "simple_gen_02", "prompt": "Who wrote Romeo and Juliet?", "task_type": "general", "difficulty": "simple", "ground_truth": "William Shakespeare"},
    {"task_id": "simple_gen_03", "prompt": "What does the acronym API stand for?", "task_type": "general", "difficulty": "simple", "ground_truth": "Application Programming Interface"},
    {"task_id": "simple_gen_04", "prompt": "What is the boiling point of water in Celsius?", "task_type": "general", "difficulty": "simple", "ground_truth": "100"},
    {"task_id": "simple_gen_05", "prompt": "Name the largest planet in our solar system.", "task_type": "general", "difficulty": "simple", "ground_truth": "Jupiter"},

    # Simple Math (GSM8K-style)
    {"task_id": "simple_math_01", "prompt": "Calculate 15 * 7 + 3.", "task_type": "math", "difficulty": "simple", "ground_truth": "108"},
    {"task_id": "simple_math_02", "prompt": "What is 256 divided by 8?", "task_type": "math", "difficulty": "simple", "ground_truth": "32"},
    {"task_id": "simple_math_03", "prompt": "If a book costs $12 and you buy 5, how much do you spend?", "task_type": "math", "difficulty": "simple", "ground_truth": "60"},
    {"task_id": "simple_math_04", "prompt": "What is 15% of 200?", "task_type": "math", "difficulty": "simple", "ground_truth": "30"},
    {"task_id": "simple_math_05", "prompt": "A train travels 60 km/h. How far does it go in 3 hours?", "task_type": "math", "difficulty": "simple", "ground_truth": "180 km"},

    # Simple Code
    {"task_id": "simple_code_01", "prompt": "Write a Python function that returns the square of a number.", "task_type": "code", "difficulty": "simple", "ground_truth": None},
    {"task_id": "simple_code_02", "prompt": "What does the `len()` function do in Python?", "task_type": "code", "difficulty": "simple", "ground_truth": "Returns the number of items in an object"},
    {"task_id": "simple_code_03", "prompt": "Write a list comprehension that squares all numbers from 1 to 10.", "task_type": "code", "difficulty": "simple", "ground_truth": None},

    # Simple Reasoning
    {"task_id": "simple_reas_01", "prompt": "Is a tomato a fruit or a vegetable? Explain briefly.", "task_type": "reasoning", "difficulty": "simple", "ground_truth": None},
    {"task_id": "simple_reas_02", "prompt": "What is the difference between RAM and ROM?", "task_type": "reasoning", "difficulty": "simple", "ground_truth": None},

    # ═══════════════════════════════════════════════════════════════════════
    # MEDIUM TASKS (20 tasks) — borderline routing
    # ═══════════════════════════════════════════════════════════════════════

    # Medium Math (GSM8K-style word problems)
    {"task_id": "medium_math_01", "prompt": "A store sells apples for $2 each and oranges for $3 each. If a customer buys a total of 10 fruits and spends $24, how many apples and oranges did they buy? Show your step-by-step reasoning.", "task_type": "math", "difficulty": "medium", "ground_truth": "6 apples and 4 oranges"},
    {"task_id": "medium_math_02", "prompt": "A rectangular garden has a perimeter of 56 meters. If the length is 4 meters more than the width, what are the dimensions of the garden? Show your work.", "task_type": "math", "difficulty": "medium", "ground_truth": "Length: 16m, Width: 12m"},
    {"task_id": "medium_math_03", "prompt": "Janet has 3 times as many marbles as Tom. Together they have 48 marbles. After Janet gives Tom 6 marbles, how many does each have? Show step-by-step reasoning.", "task_type": "math", "difficulty": "medium", "ground_truth": "Janet: 30, Tom: 18"},
    {"task_id": "medium_math_04", "prompt": "A car travels from City A to City B at 60 km/h and returns at 40 km/h. If the total trip takes 5 hours, what is the distance between the cities? Solve step by step.", "task_type": "math", "difficulty": "medium", "ground_truth": "120 km"},
    {"task_id": "medium_math_05", "prompt": "In a class of 40 students, 25 play football, 20 play basketball, and 10 play both. How many play neither sport? Use set theory and show your reasoning.", "task_type": "math", "difficulty": "medium", "ground_truth": "5"},

    # Medium Reasoning
    {"task_id": "medium_reas_01", "prompt": "Explain the difference between TCP and UDP protocols. When would you use each one? Provide real-world examples for both.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_reas_02", "prompt": "Compare and contrast supervised learning and unsupervised learning in machine learning. Give two examples of each and explain when one is preferred over the other.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_reas_03", "prompt": "What are the pros and cons of microservices architecture versus monolithic architecture? Discuss from the perspective of a startup vs large enterprise.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_reas_04", "prompt": "Explain how a hash table works internally. What are collisions and how are they handled? Compare chaining vs open addressing.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_reas_05", "prompt": "Why is Python considered slower than C++? Explain the technical reasons behind runtime performance differences and when Python is still the better choice.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},

    # Medium Code
    {"task_id": "medium_code_01", "prompt": "Write a Python function that implements binary search on a sorted list. Include error handling and explain the time complexity.", "task_type": "code", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_code_02", "prompt": "Implement a stack data structure in Python using a class. Include push, pop, peek, and is_empty methods with proper error handling.", "task_type": "code", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_code_03", "prompt": "Write a Python function to check if a string is a valid palindrome, ignoring spaces and punctuation. Explain your approach.", "task_type": "code", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_code_04", "prompt": "Create a Python decorator that measures the execution time of a function and prints the result. Show an example of its usage.", "task_type": "code", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_code_05", "prompt": "Write a Python function that finds the two numbers in a list that add up to a target sum. Optimize for time complexity and explain why your solution is O(n).", "task_type": "code", "difficulty": "medium", "ground_truth": None},

    # Medium General
    {"task_id": "medium_gen_01", "prompt": "Explain the CAP theorem in distributed systems. Which two properties does each popular database prioritize? Give examples.", "task_type": "general", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_gen_02", "prompt": "What is the difference between REST and GraphQL? When would you choose one over the other? Provide a concrete example scenario.", "task_type": "general", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_gen_03", "prompt": "Explain how HTTPS works. Walk through the TLS handshake process step by step.", "task_type": "general", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_gen_04", "prompt": "What is the difference between concurrency and parallelism? Give examples in Python using threading vs multiprocessing.", "task_type": "general", "difficulty": "medium", "ground_truth": None},
    {"task_id": "medium_gen_05", "prompt": "Explain the concept of database normalization. Describe 1NF through 3NF with examples using a student enrollment database.", "task_type": "general", "difficulty": "medium", "ground_truth": None},

    # ═══════════════════════════════════════════════════════════════════════
    # COMPLEX TASKS (15 tasks) — should route to Multi-Agent
    # ═══════════════════════════════════════════════════════════════════════

    # Complex Math
    {"task_id": "complex_math_01", "prompt": "A company produces widgets in two factories. Factory A produces 60% of widgets with a 3% defect rate. Factory B produces 40% with a 5% defect rate. Step 1: If a randomly selected widget is defective, what is the probability it came from Factory A? Step 2: If you test 100 widgets and find 4 defective ones, is this consistent with the expected defect rate? Step 3: Calculate the 95% confidence interval for the overall defect rate.", "task_type": "math", "difficulty": "complex", "ground_truth": "P(A|defective) ≈ 0.474"},
    {"task_id": "complex_math_02", "prompt": "A farmer has 200 meters of fencing to enclose a rectangular area next to a river (no fencing needed on the river side). Step 1: Express the area as a function of width. Step 2: Find the dimensions that maximize the area using calculus. Step 3: What if the farmer wants to divide the rectangle into 3 equal sections with fencing parallel to the width? Find the new optimal dimensions.", "task_type": "math", "difficulty": "complex", "ground_truth": "Without division: 100m × 50m = 5000 sq m"},
    {"task_id": "complex_math_03", "prompt": "Solve the following system of equations step by step using at least two different methods (substitution and matrix method): 2x + 3y - z = 1, x - y + 2z = 5, 3x + y + z = 8. Verify your solution by substituting back into all three equations.", "task_type": "math", "difficulty": "complex", "ground_truth": "x=2, y=-1, z=3"},

    # Complex Code
    {"task_id": "complex_code_01", "prompt": "Design a Python class hierarchy for a library management system. The system should handle books, magazines, and digital media. Each item should support borrowing, returning, and reservation. Include proper inheritance, abstract methods, and explain your design decisions. Then write a usage example showing polymorphism in action.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_code_02", "prompt": "Analyze the following algorithmic problem step by step: Given an array of n integers, find the longest subsequence such that the difference between adjacent elements is at most k. First, explain the brute force approach and its time complexity. Then, optimize using dynamic programming. Finally, analyze if there is a greedy solution. Compare all three approaches with time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_code_03", "prompt": "Implement a complete LRU (Least Recently Used) cache in Python using a combination of a hash map and a doubly-linked list. Step 1: Design the data structure. Step 2: Implement get() and put() operations in O(1) time. Step 3: Add a method to resize the cache. Step 4: Write comprehensive unit tests. Step 5: Analyze the time and space complexity.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_code_04", "prompt": "Design and implement a rate limiter in Python that supports: 1) Fixed window rate limiting, 2) Sliding window rate limiting, 3) Token bucket algorithm. For each approach, implement the class, explain the tradeoffs, and write test cases. Finally, compare all three approaches in terms of memory usage, accuracy, and burst handling.", "task_type": "code", "difficulty": "complex", "ground_truth": None},

    # Complex Reasoning
    {"task_id": "complex_reas_01", "prompt": "Explain how transformers work in deep learning. Start from the attention mechanism, then explain self-attention, multi-head attention, positional encoding, and the encoder-decoder architecture. Then critically evaluate the pros and cons of transformers versus RNNs and CNNs for NLP tasks. Finally, discuss how modern LLMs like GPT and LLaMA build on the transformer architecture and what innovations they introduced.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_reas_02", "prompt": "You are given a dataset of customer purchase history with 1 million rows and 50 features. Design a complete machine learning pipeline for predicting customer churn. Include: 1) Feature engineering strategy 2) How to handle class imbalance 3) Model selection with justification 4) Evaluation metrics and why 5) How to deploy this model in production with monitoring. For each step, explain the tradeoffs between at least two approaches.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_reas_03", "prompt": "Critically analyze the environmental impact of large language models. First, quantify the carbon footprint of training models like GPT-4 vs LLaMA. Then, evaluate the tradeoff between model size, performance, and environmental cost. Compare at least 3 approaches to reduce the environmental impact (distillation, quantization, sparse models). Finally, propose a framework for 'sustainable AI development' that balances innovation with environmental responsibility.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_reas_04", "prompt": "Design a distributed system architecture for a real-time collaborative document editor (like Google Docs). Address: 1) Conflict resolution using CRDTs vs OT — explain both and justify your choice. 2) How to ensure eventual consistency. 3) Network partition handling. 4) Scalability to 1 million concurrent users. 5) Security considerations. Draw the high-level architecture and explain each component.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_reas_05", "prompt": "Compare and contrast 5 different database paradigms: Relational (PostgreSQL), Document (MongoDB), Graph (Neo4j), Key-Value (Redis), and Time-Series (InfluxDB). For each: explain the data model, ideal use case, scaling strategy, and limitations. Then design a polyglot persistence architecture for an e-commerce platform that uses at least 3 of these databases, explaining why each was chosen for its specific role.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},

    # Complex General
    {"task_id": "complex_gen_01", "prompt": "Write a comprehensive technical analysis of WebAssembly. First, explain how it works at the binary level. Then compare its performance characteristics with JavaScript across CPU-intensive tasks, I/O operations, and startup time. Design a benchmark suite to measure these differences. Finally, evaluate 3 real-world use cases where WebAssembly provides significant advantages and 2 where JavaScript is still preferred.", "task_type": "general", "difficulty": "complex", "ground_truth": None},
    {"task_id": "complex_gen_02", "prompt": "Analyze the evolution of consensus algorithms in distributed systems. Start with Paxos, then Raft, then Byzantine Fault Tolerance (PBFT), and finally blockchain consensus (Proof of Work, Proof of Stake). For each: 1) Explain the core mechanism 2) Analyze failure modes 3) Discuss performance characteristics 4) Give real-world implementations. Compare all algorithms in a table format and recommend which to use for different system requirements.", "task_type": "general", "difficulty": "complex", "ground_truth": None},

    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 2 ADDITIONS (25 tasks) — expanded benchmark
    # ═══════════════════════════════════════════════════════════════════════

    # ── Additional GSM8K-style Simple Math (with numeric ground truths) ──
    {"task_id": "p2_simple_math_01", "prompt": "A bakery sells cupcakes for $3 each. If they sell 45 cupcakes on Monday and 58 on Tuesday, how much total revenue did they make?", "task_type": "math", "difficulty": "simple", "ground_truth": "309"},
    {"task_id": "p2_simple_math_02", "prompt": "A library has 1,245 books. If 387 are fiction and 412 are non-fiction, how many books are in other categories?", "task_type": "math", "difficulty": "simple", "ground_truth": "446"},
    {"task_id": "p2_simple_math_03", "prompt": "If a rectangle has a length of 15 cm and a width of 8 cm, what is its area in square centimeters?", "task_type": "math", "difficulty": "simple", "ground_truth": "120"},
    {"task_id": "p2_simple_math_04", "prompt": "A car's fuel tank holds 50 liters. If it uses 7.5 liters per 100 km, how far can it travel on a full tank?", "task_type": "math", "difficulty": "simple", "ground_truth": "666.67 km"},
    {"task_id": "p2_simple_math_05", "prompt": "There are 24 students in a class. If 3/8 of them are girls, how many boys are there?", "task_type": "math", "difficulty": "simple", "ground_truth": "15"},

    # ── Additional Medium Math (word problems with ground truths) ──
    {"task_id": "p2_medium_math_01", "prompt": "A shop offers a 20% discount on a $150 jacket. After applying the discount, a sales tax of 8% is added. What is the final price? Step 1: Calculate the discount. Step 2: Apply tax. Show your work.", "task_type": "math", "difficulty": "medium", "ground_truth": "129.60"},
    {"task_id": "p2_medium_math_02", "prompt": "Two trains leave the same station at the same time, traveling in opposite directions. Train A travels at 80 km/h and Train B at 120 km/h. After how many hours will they be 500 km apart? Show your reasoning.", "task_type": "math", "difficulty": "medium", "ground_truth": "2.5 hours"},
    {"task_id": "p2_medium_math_03", "prompt": "A company's profit increased by 15% from Year 1 to Year 2, then decreased by 10% from Year 2 to Year 3. If the Year 1 profit was $200,000, what was the Year 3 profit? Show each step.", "task_type": "math", "difficulty": "medium", "ground_truth": "$207,000"},
    {"task_id": "p2_medium_math_04", "prompt": "A cylindrical water tank has radius 3 meters and height 5 meters. Calculate its volume in cubic meters and how many liters of water it can hold. Use π = 3.14159. Show your work step by step.", "task_type": "math", "difficulty": "medium", "ground_truth": "141,372 liters"},
    {"task_id": "p2_medium_math_05", "prompt": "In a survey, 60% of respondents like coffee, 45% like tea, and 25% like both. What percentage likes neither? Use a Venn diagram approach and show your reasoning.", "task_type": "math", "difficulty": "medium", "ground_truth": "20%"},

    # ── Creative / Open-Ended Tasks (new category) ──
    {"task_id": "p2_creative_01", "prompt": "Write a short story (200-300 words) about a programmer who discovers that their code has become sentient.", "task_type": "creative", "difficulty": "medium", "ground_truth": None},
    {"task_id": "p2_creative_02", "prompt": "Create a detailed analogy that explains how the internet works to a 10-year-old child. Use a physical-world metaphor throughout.", "task_type": "creative", "difficulty": "medium", "ground_truth": None},
    {"task_id": "p2_creative_03", "prompt": "Design a board game that teaches basic programming concepts (variables, loops, conditions). Describe the rules, game pieces, win conditions, and give an example turn.", "task_type": "creative", "difficulty": "complex", "ground_truth": None},
    {"task_id": "p2_creative_04", "prompt": "Write a persuasive essay (300 words) arguing whether artificial intelligence will create more jobs than it destroys. Present evidence for both sides before stating your position.", "task_type": "creative", "difficulty": "medium", "ground_truth": None},
    {"task_id": "p2_creative_05", "prompt": "Invent a new sorting algorithm inspired by a natural phenomenon (e.g., how ants organize food). Describe the algorithm, write pseudocode, and analyze its theoretical time complexity.", "task_type": "creative", "difficulty": "complex", "ground_truth": None},

    # ── Additional Complex Code Tasks ──
    {"task_id": "p2_complex_code_01", "prompt": "Implement a thread-safe producer-consumer queue in Python using threading primitives (Lock, Condition). Step 1: Design the data structure. Step 2: Implement put() and get() methods with blocking. Step 3: Add a timeout mechanism. Step 4: Write a test demonstrating 3 producers and 2 consumers. Analyze potential deadlock scenarios.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "p2_complex_code_02", "prompt": "Design and implement a simple regex engine in Python that supports: literal characters, . (any char), * (zero or more), + (one or more), and ? (zero or one). First, explain how you would parse the regex into an NFA. Then implement the matching function. Write test cases for each operator. Finally, discuss the limitations of your approach vs full regex engines.", "task_type": "code", "difficulty": "complex", "ground_truth": None},

    # ── Additional Simple General QA (with ground truths) ──
    {"task_id": "p2_simple_gen_01", "prompt": "What is the chemical formula for water?", "task_type": "general", "difficulty": "simple", "ground_truth": "H2O"},
    {"task_id": "p2_simple_gen_02", "prompt": "In what year did World War II end?", "task_type": "general", "difficulty": "simple", "ground_truth": "1945"},
    {"task_id": "p2_simple_gen_03", "prompt": "What programming language was created by Guido van Rossum?", "task_type": "general", "difficulty": "simple", "ground_truth": "Python"},

    # ── Multi-Domain Reasoning ──
    {"task_id": "p2_complex_reas_01", "prompt": "A hospital wants to implement an AI system for preliminary diagnosis from medical images. Analyze this from three perspectives: 1) Technical: What ML architecture would you choose and why? Compare CNNs vs Vision Transformers for medical imaging. 2) Ethical: What are the risks of AI misdiagnosis? How should liability be handled? 3) Regulatory: What compliance requirements (HIPAA, FDA) must be met? Design a deployment strategy that addresses all three perspectives.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "p2_complex_reas_02", "prompt": "Critically evaluate the claim that 'NoSQL databases are better than relational databases for modern applications.' First, define what 'better' means across 5 dimensions (scalability, consistency, query flexibility, developer experience, cost). Then analyze 3 specific use cases where the claim is TRUE and 3 where it is FALSE. Support each with technical reasoning.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},
    {"task_id": "p2_complex_reas_03", "prompt": "A startup has $500K in funding and needs to build a real-time analytics platform processing 10 million events per day. Compare two architectural approaches: 1) Cloud-native (AWS Lambda + DynamoDB + Kinesis) vs 2) Self-hosted (Kafka + ClickHouse + Kubernetes). For each: estimate monthly costs, analyze scaling limits, evaluate development timeline, and identify 3 biggest risks. Provide a final recommendation with justification.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": None},

    # ═══════════════════════════════════════════════════════════════════════
    # HARD LOGIC TRAPS (10 tasks) — designed to trick single LLMs
    # ═══════════════════════════════════════════════════════════════════════
    {"task_id": "hard_logic_01", "prompt": "A store sells apples for $3, bananas for $2, and cherries for $5. You buy exactly 7 fruits for exactly $26. You must buy at least one of each fruit. How many of EACH fruit did you buy?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "3 apples, 1 banana, 3 cherries"},
    {"task_id": "hard_logic_02", "prompt": "Solve this logic puzzle: Alice, Bob, and Grace are wearing hats: Amber, Blue, and Green. No one wears a hat starting with the same letter as their name. Grace is not wearing the Amber hat. What color hat is Bob wearing? Think step-by-step.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "Amber"},
    {"task_id": "hard_logic_03", "prompt": "A snail is at the bottom of a 30-foot well. Every day it climbs 7 feet, but at night it slides back 4 feet. How many days will it take for the snail to escape the well?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "9"},
    {"task_id": "hard_logic_04", "prompt": "If 3 florps equal 5 blarps, and 2 blarps equal 7 glops, how many glops are in 12 florps?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "70"},
    {"task_id": "hard_logic_05", "prompt": "A train leaves City X for City Y at 60 mph. An hour later, another train leaves City Y for City X at 80 mph. The cities are 340 miles apart. How far from City X are they when they meet?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "180"},
    {"task_id": "hard_logic_06", "prompt": "What is the next number in this sequence: 3, 3, 5, 4, 4, 3, 5, 5, 4, ? (Hint: think about the English words for the numbers 1 through 10).", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "3"},
    {"task_id": "hard_logic_07", "prompt": "There are 5 people in a room. You go in and kill 2 of them. How many people are in the room now?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "6"},
    {"task_id": "hard_logic_08", "prompt": "I have 6 eggs. I broke 2, I cooked 2, and I ate 2. How many eggs are left?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "4"},
    {"task_id": "hard_logic_09", "prompt": "Which is heavier: 100 pounds of rocks or 100 pounds of feathers? Reply with just 'rocks', 'feathers', or 'neither'.", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "neither"},
    {"task_id": "hard_logic_10", "prompt": "A father and son are in a car crash. The father dies instantly. The son is taken to the hospital. The surgeon says, 'I can't operate on him, he's my son.' Who is the surgeon?", "task_type": "reasoning", "difficulty": "complex", "ground_truth": "mother"},

    # ═══════════════════════════════════════════════════════════════════════
    # SCALE-UP BATCH (45 additional tasks)
    # ═══════════════════════════════════════════════════════════════════════
    {"task_id": "scale_math_00", "prompt": "If a train travels at 60 mph for 3 hours, then stops for 1 hour, then travels at 50 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "280"},
    {"task_id": "scale_math_01", "prompt": "If a train travels at 65 mph for 3 hours, then stops for 1 hour, then travels at 52 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "299"},
    {"task_id": "scale_math_02", "prompt": "If a train travels at 70 mph for 3 hours, then stops for 1 hour, then travels at 54 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "318"},
    {"task_id": "scale_math_03", "prompt": "If a train travels at 75 mph for 3 hours, then stops for 1 hour, then travels at 56 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "337"},
    {"task_id": "scale_math_04", "prompt": "If a train travels at 80 mph for 3 hours, then stops for 1 hour, then travels at 58 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "356"},
    {"task_id": "scale_math_05", "prompt": "If a train travels at 85 mph for 3 hours, then stops for 1 hour, then travels at 60 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "375"},
    {"task_id": "scale_math_06", "prompt": "If a train travels at 90 mph for 3 hours, then stops for 1 hour, then travels at 62 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "394"},
    {"task_id": "scale_math_07", "prompt": "If a train travels at 95 mph for 3 hours, then stops for 1 hour, then travels at 64 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "413"},
    {"task_id": "scale_math_08", "prompt": "If a train travels at 100 mph for 3 hours, then stops for 1 hour, then travels at 66 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "432"},
    {"task_id": "scale_math_09", "prompt": "If a train travels at 105 mph for 3 hours, then stops for 1 hour, then travels at 68 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "451"},
    {"task_id": "scale_math_10", "prompt": "If a train travels at 110 mph for 3 hours, then stops for 1 hour, then travels at 70 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "470"},
    {"task_id": "scale_math_11", "prompt": "If a train travels at 115 mph for 3 hours, then stops for 1 hour, then travels at 72 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "489"},
    {"task_id": "scale_math_12", "prompt": "If a train travels at 120 mph for 3 hours, then stops for 1 hour, then travels at 74 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "508"},
    {"task_id": "scale_math_13", "prompt": "If a train travels at 125 mph for 3 hours, then stops for 1 hour, then travels at 76 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "527"},
    {"task_id": "scale_math_14", "prompt": "If a train travels at 130 mph for 3 hours, then stops for 1 hour, then travels at 78 mph for 2 hours, what is the total distance traveled?", "task_type": "math", "difficulty": "medium", "ground_truth": "546"},
    {"task_id": "scale_reas_00", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 2 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_01", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 3 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_02", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 4 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_03", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 5 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_04", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 6 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_05", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 7 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_06", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 8 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_07", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 9 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_08", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 10 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_09", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 11 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_10", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 12 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_11", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 13 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_12", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 14 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_13", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 15 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_reas_14", "prompt": "Analyze the following ethical dilemma: A self-driving car must choose between hitting 16 pedestrians or a barrier. Analyze using utilitarianism vs deontological ethics.", "task_type": "reasoning", "difficulty": "medium", "ground_truth": None},
    {"task_id": "scale_code_00", "prompt": "Write a Python function to solve the `Two Sum` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_01", "prompt": "Write a Python function to solve the `Valid Parentheses` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_02", "prompt": "Write a Python function to solve the `Merge Intervals` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_03", "prompt": "Write a Python function to solve the `Word Break` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_04", "prompt": "Write a Python function to solve the `Climbing Stairs` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_05", "prompt": "Write a Python function to solve the `Coin Change` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_06", "prompt": "Write a Python function to solve the `Longest Substring` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_07", "prompt": "Write a Python function to solve the `3Sum` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_08", "prompt": "Write a Python function to solve the `Container With Most Water` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_09", "prompt": "Write a Python function to solve the `Valid Anagram` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_10", "prompt": "Write a Python function to solve the `Group Anagrams` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_11", "prompt": "Write a Python function to solve the `Maximum Subarray` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_12", "prompt": "Write a Python function to solve the `Jump Game` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_13", "prompt": "Write a Python function to solve the `Unique Paths` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},
    {"task_id": "scale_code_14", "prompt": "Write a Python function to solve the `Reverse Linked List` problem. Include time and space complexity analysis.", "task_type": "code", "difficulty": "complex", "ground_truth": None},

]



def generate_dataset(output_path: Path = None) -> list[dict]:
    """Write the benchmark dataset to JSON."""
    if output_path is None:
        output_path = Path(__file__).parent.parent.parent / "data" / "tasks" / "benchmark_tasks.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(BENCHMARK_TASKS, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(BENCHMARK_TASKS)} tasks → {output_path}")
    return BENCHMARK_TASKS


def get_tasks_by_difficulty(difficulty: str) -> list[dict]:
    return [t for t in BENCHMARK_TASKS if t["difficulty"] == difficulty]


def get_tasks_by_type(task_type: str) -> list[dict]:
    return [t for t in BENCHMARK_TASKS if t["task_type"] == task_type]


def dataset_summary() -> dict:
    """Quick summary of the dataset composition."""
    from collections import Counter
    diff_counts = Counter(t["difficulty"] for t in BENCHMARK_TASKS)
    type_counts = Counter(t["task_type"] for t in BENCHMARK_TASKS)
    gt_count = sum(1 for t in BENCHMARK_TASKS if t.get("ground_truth"))
    return {
        "total": len(BENCHMARK_TASKS),
        "by_difficulty": dict(diff_counts),
        "by_type": dict(type_counts),
        "with_ground_truth": gt_count,
    }


if __name__ == "__main__":
    generate_dataset()
    print(json.dumps(dataset_summary(), indent=2))
