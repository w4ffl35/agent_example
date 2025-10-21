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
    args = vars(parser.parse_args())
    app = App()
    app.run()


if __name__ == "__main__":
    main()
