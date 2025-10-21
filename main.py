import argparse
from app import App


def main():
    parser = argparse.ArgumentParser(description="Run the Agent Example App")
    parser.add_argument(
        "--agent_folder",
        type=str,
        default="dev_onboarding",
        help="Name of the agent folder (contains system_prompt.md and knowledge/)",
    )
    parser.add_argument(
        "--agent_name",
        type=str,
        default="Bot",
        help="Name of the agent",
    )
    parser.add_argument(
        "--base_path",
        type=str,
        default="docs/rag",
        help="Base path containing agent folders",
    )
    parser.add_argument(
        "--provider_name",
        type=str,
        default="ollama",
        help="Name of the embedding provider",
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="llama3.2",
        help="Name of the language model to use",
    )
    parser.add_argument(
        "--extra_files",
        type=str,
        default="",
        help="Comma-separated list of extra files to include in the knowledge base",
    )
    args = vars(parser.parse_args())
    app = App(
        agent_folder=args["agent_folder"],
        agent_name=args["agent_name"],
        provider_name=args["provider_name"],
        model_name=args["model_name"],
        base_path=args["base_path"],
        extra_files=args["extra_files"].split(",") if args["extra_files"] else [],
    )
    app.run()
    app.join()


if __name__ == "__main__":
    main()
