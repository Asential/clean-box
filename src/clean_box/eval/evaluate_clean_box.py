from dotenv import load_dotenv
load_dotenv("D:\\Projects\\clean-box\\.env")

import pytest
from clean_box.clean_box_agent import agent
from clean_box.util import extract_tool_calls
from clean_box.util import format_messages_string
from clean_box.eval.email_dataset import dataset_examples, expected_tool_calls, email_inputs, response_criteria, decsiion_outputs


from langsmith import testing as t

@pytest.mark.langsmith
@pytest.mark.parametrize(
    "email_input, expected_tool_calls",
    [   # Pick some examples with e-mail reply expected
        (email_inputs[0],expected_tool_calls[0]),
        (email_inputs[2],expected_tool_calls[2]),
    ],
)
def test_email_dataset(email_input, expected_tool_calls):
    result = agent.invoke({"email_input": email_input})
    extracted_tool_calls = extract_tool_calls(result["messages"])
    missing_calls = [call for call in expected_tool_calls if call not in extracted_tool_calls]

    t.log_outputs({
        "missing_calls": missing_calls,
        "extracted_tool_calls": extracted_tool_calls,
        "response": format_messages_string(result["messages"]),
    })

    assert len(missing_calls) == 0
