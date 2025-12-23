USE_REAL_LLM = False

import os

def main():
    print("Pet AI project is running")


if __name__ == "__main__":
    main()


def get_user_idea():
    idea = input("Please, enter your idea: ")
    return idea


def ask_clarifying_questions():
    print("\nAnswer a few quick questions (short answers are fine).")

    def ask_non_empty(question):
        while True:
            answer = input(question).strip()
            if answer:
                return answer
            print("Please enter a valid answer.")

    location = ask_non_empty("1) Where will it be (city/online/mall etc.)? ")
    audience = ask_non_empty("2) Who is the target audience? ")
    budget = ask_non_empty("3) What is the approximate budget (in $)? ")
    timeline = ask_non_empty("4) When do you want to launch (e.g., 1 month, 3 months)? ")
    advantage = ask_non_empty("5) What is your main advantage vs competitors? ")

    return {
        "location": location,
        "audience": audience,
        "budget": budget,
        "timeline": timeline,
        "advantage": advantage
    }


def build_llm_prompt(idea, idea_type, extras):
    prompt = f"""
You are a business analyst.
Analyze the business idea below and return a structured result.

Idea: {idea}
Idea type: {idea_type}

Extra context:
- Location: {extras.get("location", "")}
- Target audience: {extras.get("audience", "")}
- Budget: {extras.get("budget", "")}
- Timeline: {extras.get("timeline", "")}
- Main advantage: {extras.get("advantage", "")}

Return only the following fields, each on a new line:

PROBLEM:
TARGET_AUDIENCE:
VALUE_PROPOSITION:
MVP:
NEXT_STEPS:
"""
    return prompt


def fake_llm_response(prompt):
    return """PROBLEM:
People want better coffee experience or convenience.

TARGET AUDIENCE:
Coffee lovers, office workers, students, local residents.

VALUE PROPOSITION:
High-quality coffee, cozy atmosphere, fast service.

MVP:
Small coffee kiosk or minimal coffee corner with 3-5 drinks.

NEXT STEPS:
Choose location, test pricing, interview 20 potential customers.
"""


def llm_response(prompt):
    if not USE_REAL_LLM:
        print("\n[INFO] Using fake LLM (real API disabled by flag)\n")
        return fake_llm_response(prompt)

    try:
        from openai import OpenAI
        client = OpenAI()

        response = client.responses.create(
            model="gpt-5-mini",
            input=prompt
        )
        return response.output_text

    except Exception as e:
        print("\n[WARNING] Real LLM failed. Using fake LLM.")
        print(f"[DETAILS] {e}\n")
        return fake_llm_response(prompt)






def parse_llm_output(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    result = {
        "problem": "",
        "target_audience": "",
        "value_proposition": "",
        "mvp": "",
        "next_steps": ""
    }

    def normalize_header(s: str) -> str:
        # "Target audience:" -> "TARGETAUDIENCE"
        s = s.strip().upper()
        s = s.replace(" ", "").replace("_", "")
        if s.endswith(":"):
            s = s[:-1]
        return s

    mapping = {
        "PROBLEM": "problem",
        "TARGETAUDIENCE": "target_audience",
        "VALUEPROPOSITION": "value_proposition",
        "MVP": "mvp",
        "NEXTSTEPS": "next_steps",
    }

    current_key = None

    for line in lines:
        header = normalize_header(line)
        if header in mapping:
            current_key = mapping[header]
            continue

        if current_key:
            if result[current_key]:
                result[current_key] += " " + line
            else:
                result[current_key] = line

    return result



def analyze_idea(idea, extras):
    idea_lower = idea.lower()

    if "app" in idea_lower or "platform" in idea_lower:
        idea_type = "Digital product"
    elif "store" in idea_lower or "shop" in idea_lower:
        idea_type = "Offline business"
    else:
        idea_type = "General business idea"

    prompt = build_llm_prompt(idea, idea_type, extras)
    llm_text = llm_response(prompt)
    parsed = parse_llm_output(llm_text)


    analysis = { 
        "idea_type": idea_type,
        "problem": parsed["problem"],
        "target_audience": parsed["target_audience"],
        "value_proposition": parsed["value_proposition"],
        "mvp": parsed["mvp"],
        "next_steps": parsed["next_steps"]
    }

    return analysis


def show_analysis(analysis):

    print("IDEA TYPE:")
    print(analysis["idea_type"])

    print("\n--- ANALYSIS RESULT ---\n")

    print("PROBLEM:")
    print(analysis["problem"])

    print("\nTARGET AUDIENCE:")
    print(analysis["target_audience"])

    print("\nVALUE PROPOSITION:")
    print(analysis["value_proposition"])

    print("\nMVP:")
    print(analysis["mvp"])

    print("\nNEXT STEPS:")
    print(analysis["next_steps"])



print("Welcome to Business AI MVP Generator!")

user_idea = get_user_idea()
extras = ask_clarifying_questions()

analysis = analyze_idea(user_idea, extras)
show_analysis(analysis)
