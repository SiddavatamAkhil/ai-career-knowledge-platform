"""
Static reference data so career/interview features work fully offline
(no API key, no internet) and still feel real. Small and hand-curated on
purpose — this is demo data, not a scraped dataset.
"""

ROLE_SKILLS = {
    "Data Scientist": ["python", "sql", "statistics", "machine learning", "pandas",
                        "scikit-learn", "data visualization", "a/b testing", "deep learning"],
    "Backend Engineer": ["python", "java", "sql", "rest api", "docker", "kubernetes",
                          "microservices", "system design", "git", "ci/cd"],
    "Frontend Engineer": ["javascript", "typescript", "react", "html", "css",
                           "webpack", "accessibility", "testing", "git"],
    "ML Engineer": ["python", "pytorch", "tensorflow", "mlops", "docker",
                     "kubernetes", "model deployment", "sql", "distributed systems"],
    "Product Manager": ["roadmapping", "user research", "sql", "a/b testing",
                         "stakeholder management", "agile", "analytics", "communication"],
    "DevOps Engineer": ["linux", "docker", "kubernetes", "terraform", "aws",
                         "ci/cd", "monitoring", "networking", "bash"],
}

MOCK_JOBS = [
    {"title": "Data Scientist", "company": "Northwind Analytics", "location": "Remote",
     "skills": ["python", "sql", "machine learning", "pandas", "statistics"]},
    {"title": "Senior Backend Engineer", "company": "Fabrikam Cloud", "location": "Hyderabad, IN",
     "skills": ["python", "microservices", "docker", "kubernetes", "system design"]},
    {"title": "Frontend Engineer", "company": "Contoso Retail", "location": "Bengaluru, IN",
     "skills": ["react", "typescript", "css", "accessibility"]},
    {"title": "Machine Learning Engineer", "company": "Adatum AI", "location": "Remote",
     "skills": ["pytorch", "mlops", "docker", "model deployment", "python"]},
    {"title": "Associate Product Manager", "company": "Tailwind Apps", "location": "Pune, IN",
     "skills": ["roadmapping", "sql", "user research", "analytics", "agile"]},
    {"title": "DevOps Engineer", "company": "Litware Systems", "location": "Remote",
     "skills": ["kubernetes", "terraform", "aws", "ci/cd", "monitoring"]},
    {"title": "Junior Data Analyst", "company": "Northwind Analytics", "location": "Chennai, IN",
     "skills": ["sql", "python", "data visualization", "statistics"]},
    {"title": "Full-Stack Engineer", "company": "Contoso Retail", "location": "Remote",
     "skills": ["react", "python", "rest api", "sql", "git"]},
]

TECHNICAL_QUESTIONS = {
    "Data Scientist": [
        "How would you handle a dataset with severe class imbalance?",
        "Explain the bias-variance tradeoff with an example.",
        "How do you decide between precision and recall for a given problem?",
        "Walk me through how you'd validate a new ML model before deploying it.",
        "What's the difference between bagging and boosting?",
    ],
    "Backend Engineer": [
        "How would you design a rate limiter for a public API?",
        "Explain the difference between SQL and NoSQL and when you'd choose each.",
        "How do you approach debugging a memory leak in a long-running service?",
        "Design a URL shortener — what are the key components?",
        "What's the difference between horizontal and vertical scaling?",
    ],
    "Frontend Engineer": [
        "How would you optimize the initial load time of a React app?",
        "Explain the virtual DOM and why it helps performance.",
        "How do you approach accessibility in a component library?",
        "What's the difference between controlled and uncontrolled components?",
        "How would you debug a memory leak in a single-page app?",
    ],
    "ML Engineer": [
        "How would you monitor a model for drift in production?",
        "Explain the tradeoffs between batch and real-time inference.",
        "How do you version datasets and models together?",
        "Walk through your approach to a canary deployment for a new model.",
        "What's the difference between quantization and distillation?",
    ],
    "Product Manager": [
        "How would you prioritize a backlog with limited engineering capacity?",
        "Walk me through how you'd measure the success of a new feature.",
        "How do you handle disagreement between engineering and design?",
        "Describe how you'd run an A/B test for a pricing change.",
    ],
    "DevOps Engineer": [
        "How would you design a zero-downtime deployment pipeline?",
        "Explain the difference between containers and virtual machines.",
        "How do you approach secrets management in Kubernetes?",
        "Walk through how you'd debug a service that's intermittently 500-ing.",
    ],
}

HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want to work here?",
    "Describe a time you disagreed with a teammate — how did you handle it?",
    "Tell me about a project you're proud of and your specific contribution.",
    "How do you handle tight deadlines and competing priorities?",
    "Describe a time you failed and what you learned from it.",
    "Where do you see yourself in five years?",
    "Tell me about a time you had to learn something new quickly.",
    "How do you handle feedback you disagree with?",
    "Why are you leaving your current role?",
]

ROADMAP_STAGES = [
    "Foundations", "Core skill-building", "Applied projects",
    "Specialization", "Interview & job-search readiness",
]
