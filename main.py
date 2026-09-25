import requests

def generate_linkedin_post(topic):
    prompt = f"""
    Write a natural LinkedIn post for a cybersecurity college student.
    Topic: {topic}

    Requirements:
    - Sound like a real student.
    - Use simple and professional English.
    - Avoid exaggerated claims.
    - Mention what was learned.
    - Make it suitable for placement opportunities.
    - Include 3 to 5 relevant hashtags.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()
    return response.json()["response"]


topic = input("Enter your certificate or achievement: ")

post = generate_linkedin_post(topic)

print("\nGenerated LinkedIn Post:\n")
print(post)

with open("generated_posts/post.txt", "w", encoding="utf-8") as file:
    file.write(post)

print("\nPost saved successfully!")