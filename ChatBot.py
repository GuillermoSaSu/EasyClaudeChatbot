import os
import sys
from anthropic import Anthropic

#The model that we are going to use.
MODEL = "claude-sonnet-5"

#The instructions that you give to the model to know how to act.
SYSTEM_PROMPT = (
    "You are a  concise and helpful assistant. Respond in english unless asked otherwise. "
    " If you do not know something state so cleary."
)

#MAx length of every answer
MAX_TOKENS = 1024

INPUT_PRICE_PER_MILLION = 2.0
OUTPUT_PRICE_PER_MILLION = 10.0

def main():
    #The client automatically reads the ANTHROPIC_API_KEY environment variable, so there is no need to pass it manually.
    client = Anthropic()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Please set environment variable 'ANTHROPIC_API_KEY'")
        sys.exit(1)

    #An array to save the history of the conversation.
    history = []

    total_input_tokens = 0
    total_output_tokens = 0

    print("🤖 Chatbot ready!. Write 'exit' to finish")

    while True:
        try:
            user_message = input("You: ").strip()
        except(EOFError, KeyboardInterrupt):
            print("See youuu!")
            break

        if user_message.lower() in ("exit", "quit"):
            #Let's see the cost of the comunication.
            total_cost = (
                total_input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
                + total_output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
            )
            print(
                f"\n 📊 Session summary: {total_input_tokens} input tokens "
                f" + {total_output_tokens} output tokens = "
                f"${total_cost:.5f}"
            )
            print("See youuu!")
            break

        if not user_message:
            continue

        history.append({"role": "user", "content": user_message})

        # CAll to the API, sending:
        # -The model used.
        # - System prompt
        # - ALL the history
        # We use streaming to the answer show in live.
        print("Claude: ", end="", flush=True)
        complete_answer = ""

        with client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=history,
        ) as stream:
            for texto in stream.text_stream:
                print(texto, end="", flush=True)
                complete_answer += texto

            final_message = stream.get_final_message()

        print("\n")

        history.append({"role": "assistant", "content": complete_answer})

        #cost counter
        tokens_in = final_message.usage.input_tokens
        tokens_out = final_message.usage.output_tokens
        total_input_tokens += tokens_in
        total_output_tokens += tokens_out


if __name__ == "__main__":
    main()
