import unittest

from finclaw.core.llm import MockLLM, _extract_name


class MockLLMTests(unittest.TestCase):
    def test_extract_name_from_prompt(self) -> None:
        prompt = "Satoshi Nakamoto | Role: Quant\nContext:\n- x"
        self.assertEqual(_extract_name(prompt), "Satoshi Nakamoto")

    def test_deterministic_response_for_same_prompt(self) -> None:
        llm = MockLLM()
        prompt = "Jim Simons | Role: Quant\nRespond as yourself."
        first = llm(prompt)
        second = llm(prompt)
        self.assertEqual(first, second)

    def test_fallback_for_unknown_name(self) -> None:
        llm = MockLLM()
        response = llm("Unknown Name | Role: X")
        self.assertIn(response, llm.fallback)


if __name__ == "__main__":
    unittest.main()
