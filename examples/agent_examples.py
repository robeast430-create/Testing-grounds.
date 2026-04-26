#!/usr/bin/env python3
"""
Neural Agent - Comprehensive Example Scripts
"""

from neural_agent import NeuralAgent
from neural_agent.ml import VectorStore, TextProcessor, MLModels
from neural_agent.coding import GitManager, BuildManager

def example_basic_usage():
    """Basic agent usage example"""
    agent = NeuralAgent()
    
    agent.memory.add("Python is a versatile programming language")
    agent.memory.add("Machine learning is a subset of AI")
    
    results = agent.memory.recall("programming")
    print("Memories about programming:", results)
    
    return agent

def example_web_scrape():
    """Web scraping example"""
    agent = NeuralAgent()
    
    result = agent.web.summarize_page("https://python.org")
    print("Page summary:", result)
    
    search_results = agent.web.search("Python programming tutorials")
    for r in search_results:
        print(f"- {r['title']}: {r['url']}")

def example_file_operations():
    """File operations example"""
    agent = NeuralAgent()
    
    print(agent.files.list())
    
    content = agent.files.read("README.md")
    print(f"File content (first 100 chars): {content[:100]}")
    
    agent.files.write("test.txt", "Hello, Neural Agent!")
    print(agent.files.read("test.txt"))

def example_code_analysis():
    """Code analysis example"""
    agent = NeuralAgent()
    
    result = agent.code_analyzer.analyze_file("neural_agent/core/neural_core.py")
    print(f"Analysis: {result}")

def example_project_management():
    """Project management example"""
    agent = NeuralAgent()
    
    project = agent.projects.create_project("My Project", "A test project")
    print(f"Created project: {project.id}")
    
    task = agent.projects.create_task(
        project.id,
        "Implement feature X",
        priority="high"
    )
    print(f"Created task: {task.id}")
    
    stats = agent.projects.get_stats(project.id)
    print(f"Project stats: {stats}")

def example_ml_models():
    """ML models example"""
    ml = MLModels()
    
    X = [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6]]
    y = [2, 3, 4, 5, 6]
    
    model = ml.linear_regression(X, y)
    predictions = ml.predict_linear(model, [[6, 7]])
    print(f"Predictions: {predictions}")

def example_text_processing():
    """Text processing example"""
    processor = TextProcessor()
    
    text = "Python is a great programming language for data science"
    
    tokens = processor.tokenize(text)
    print(f"Tokens: {tokens}")
    
    keywords = processor.extract_keywords(text)
    print(f"Keywords: {keywords}")
    
    summary = processor.summarize(text, num_sentences=2)
    print(f"Summary: {summary}")

def example_vector_store():
    """Vector store example"""
    store = VectorStore(dimension=128)
    
    doc1 = [0.1] * 128
    doc2 = [0.9] * 128
    doc3 = [0.5] * 128
    
    store.add([doc1, doc2, doc3], metadata=[
        {"text": "Document 1"},
        {"text": "Document 2"},
        {"text": "Document 3"}
    ])
    
    results = store.search(doc1, k=2)
    print(f"Similar documents: {results}")

def example_git_operations():
    """Git operations example"""
    git = GitManager(None)
    
    if git.is_git_repo():
        print(git.status())
        print(git.log())
    else:
        print("Not a git repository")

def example_build_project():
    """Build project example"""
    build = BuildManager(None)
    
    project_type = build.detect_project_type()
    print(f"Project type: {project_type}")
    
    if project_type != "unknown":
        result = build.build()
        print(f"Build result: {result}")

def example_api_client():
    """API client example"""
    from neural_agent.network import HTTPClient
    
    client = HTTPClient("https://api.example.com")
    
    response = client.get("/endpoint")
    print(f"Status: {response['status_code']}")

def example_database():
    """Database example"""
    from neural_agent.database import SQLManager
    
    db = SQLManager()
    
    db.connect("test")
    db.create_table("test", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "value": "REAL"
    })
    
    db.insert("test", {"id": 1, "name": "test", "value": 1.5})
    results = db.select("test")
    print(f"Results: {results}")

def example_regex_tools():
    """Regex tools example"""
    from neural_agent.tools import RegexTools
    
    regex = RegexTools()
    
    text = "Contact us at info@example.com or support@company.org"
    
    emails = regex.extract("email", text)
    print(f"Found emails: {emails}")
    
    urls = regex.extract("url", "Visit https://example.com or http://test.org")
    print(f"Found URLs: {urls}")
    
    result = regex.test_pattern(r'\w+@\w+\.\w+', text)
    print(f"Pattern test: {result}")

def example_security_tools():
    """Security tools example"""
    from neural_agent.security import SecurityTools
    
    security = SecurityTools()
    
    sha256_hash = security.hash_string("password123", "sha256")
    print(f"SHA256: {sha256_hash}")
    
    encoded = security.encode_base64("Hello")
    print(f"Base64: {encoded}")
    
    password = security.generate_password(16)
    print(f"Generated password: {password}")

def example_monitoring():
    """Monitoring example"""
    agent = NeuralAgent()
    
    agent.alerts.add_alert("high_cpu", "gt", 80, "CPU usage is too high!")
    agent.alerts.add_alert("low_memory", "lt", 20, "Memory is running low!")
    
    print("Active alerts:", agent.alerts.list_alerts())
    
    stats = agent.uptime.get_stats()
    print("Uptime stats:", stats)

def example_log_analysis():
    """Log analysis example"""
    from neural_agent.tools import LogAnalyzer
    
    analyzer = LogAnalyzer(None)
    
    result = analyzer.analyze("agent.log")
    print(f"Log analysis: {result}")
    
    matches = analyzer.grep("agent.log", "ERROR")
    print(f"Error matches: {len(matches)}")

def example_file_converter():
    """File converter example"""
    from neural_agent.tools import FileConverter
    
    converter = FileConverter()
    
    result = converter.csv_to_json("data.csv")
    print(f"Converted: {result[:100]}")

def example_kanban_board():
    """Kanban board example"""
    agent = NeuralAgent()
    
    projects = agent.projects.list_projects()
    if projects:
        project_id = projects[0]["id"]
        
        agent.kanban.move_task(project_id, "task_1", "in_progress")
        agent.kanban.add_comment(project_id, "task_1", "Working on this")
        
        board = agent.kanban.board(project_id)
        print(f"Kanban board: {board}")

def example_crypto_tools():
    """Crypto tools example"""
    from neural_agent.security import SecurityTools
    
    security = SecurityTools()
    
    xor_encrypted = security.xor_encrypt("Hello World", "key")
    print(f"XOR encrypted: {xor_encrypted}")
    
    caesar = security.caesar_cipher("Hello", shift=3)
    print(f"Caesar cipher: {caesar}")

if __name__ == "__main__":
    print("Neural Agent Examples")
    print("=" * 50)
    
    print("\n1. Basic Usage")
    print("-" * 20)
    example_basic_usage()
    
    print("\n2. Text Processing")
    print("-" * 20)
    example_text_processing()
    
    print("\n3. Regex Tools")
    print("-" * 20)
    example_regex_tools()
    
    print("\n4. Security Tools")
    print("-" * 20)
    example_security_tools()
    
    print("\nAll examples completed!")