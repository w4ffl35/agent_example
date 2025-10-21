import argparse
from app import App


def main():
    parser = argparse.ArgumentParser(description="Run the Agent Example App")
    parser.add_argument(
        "--system_prompt_path",
        type=str,
        default="docs/system_prompt.md",
        help="Path to the system prompt file",
    )
    parser.add_argument(
        "--agent_name",
        type=str,
        default="Bot",
        help="Name of the agent",
    )
    args = vars(parser.parse_args())
    app = App(
        system_prompt_path=args["system_prompt_path"], agent_name=args["agent_name"]
    )
    app.run()
    # Wait for the app thread to finish before exiting
    app.join()


if __name__ == "__main__":
    main()
