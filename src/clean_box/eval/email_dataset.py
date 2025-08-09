email_input_1 = {
    "author": "Alice Smith <alice.smith@company.com>",
    "to": "John Doe <john.doe@company.com>",
    "subject": "Quick question about API documentation",
    "email_thread": """Hi John,

Just messaging you regarding the api docs that we were planning to discuss, shall I schedule a call?

Specifically, I'm looking at:
- /auth/refresh
- /auth/validate

Thanks!
Alice""",
}

# Spam
email_input_2 = {
    "author": "Alice Smith <alice.smith@random.com>",
    "to": "John Doe <john.doe@company.com>",
    "subject": "Make you a millionaire overnight!",
    "email_thread": "Hey John, I am a nigerian prince and am stuck in an island, I need 100 dollars to free myself, but I can't access my credit card, could you send me, then I can get the credit card back and send you a million dollars"
  }

# Useless
email_input_3 = {
    "author": "Alice Smith <alice.smith@random.com>",
    "to": "John Doe <john.doe@company.com>",
    "subject": "Exciting loan opportunity!",
    "email_thread": "We are offering a loan with a 0% interest rate for the first year. Contact us to learn more about this amazing offer!"
  }

decision_output_1 = "label"
decision_output_2 = "delete"
decision_output_3 = "delete"

response_criteria_1 = """
• Label email with label_email tool call to classify the email.  
"""

response_criteria_2 = """
• Ensure this is deleted by calling the delete tool.
"""

response_criteria_2 = """
• Ensure this is deleted by calling the delete tool.
"""

email_names = [
    "email_input_1",
    "email_input_2",
    "email_input_3",
]

email_inputs = [
    email_input_1,
    email_input_2,
    email_input_3,
]

response_criteria = [
    response_criteria_1,
    response_criteria_2,
    response_criteria_2,
]

decsiion_outputs = [
    decision_output_1,
    decision_output_2,
    decision_output_3,
]

dataset_examples = [
    {
      "inputs": {"email_input": email_input_1},
      "outputs": {"classification": decision_output_1},
    },
    {
      "inputs": {"email_input": email_input_2},
      "outputs": {"classification": decision_output_2},
    },
    {
      "inputs": {"email_input": email_input_3},
      "outputs": {"classification": decision_output_3},
    },
]

expected_tool_calls = [
    ["label_email", "done"],
    ["delete_email", "done"],
    ["delete_email", "done"],
]