
AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "Semantic search across the repository codebase using natural language. Returns relevant code snippets.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query about the code",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": "Read the complete content of a specific source file in the repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path relative to the repository root",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "record_evaluation",
            "description": "Record an evaluation of the candidate's answer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "score": {"type": "number", "description": "Overall score 0-10"},
                    "technical_correctness": {"type": "number", "description": "Score 0-10"},
                    "code_understanding": {"type": "number", "description": "Score 0-10"},
                    "architecture_understanding": {"type": "number", "description": "Score 0-10"},
                    "communication": {"type": "number", "description": "Score 0-10"},
                    "practical_thinking": {"type": "number", "description": "Score 0-10"},
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of strengths shown in the answer",
                    },
                    "weaknesses": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of weak areas in the answer",
                    },
                    "ideal_answer": {
                        "type": "string",
                        "description": "What a strong answer would include",
                    },
                    "suggestions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Improvement suggestions",
                    },
                    "resources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Recommended learning resources",
                    },
                },
                "required": ["score", "technical_correctness", "code_understanding",
                             "architecture_understanding", "communication", "practical_thinking"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "decide_next_question",
            "description": "Decide and generate the next interview question based on context so far.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question_text": {
                        "type": "string",
                        "description": "The interview question to ask",
                    },
                    "question_type": {
                        "type": "string",
                        "enum": ["architecture", "implementation", "debugging",
                                 "optimization", "security", "design", "conceptual"],
                        "description": "Category of the question",
                    },
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                        "description": "Difficulty level",
                    },
                    "related_file": {
                        "type": "string",
                        "description": "File path this question references",
                    },
                },
                "required": ["question_text", "question_type", "difficulty"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_interview",
            "description": "End the interview session. Call when enough information has been gathered.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Reason for ending the interview",
                    },
                    "overall_summary": {
                        "type": "string",
                        "description": "Summary of the candidate's overall performance",
                    },
                    "overall_score": {
                        "type": "number",
                        "description": "Final overall score 0-10",
                    },
                },
                "required": ["reason", "overall_summary", "overall_score"],
            },
        },
    },
]