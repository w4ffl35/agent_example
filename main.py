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
    parser.add_argument(
        "--rag_directory",
        type=str,
        default="docs/rag",
        help="Path to the RAG documents directory",
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
    args = vars(parser.parse_args())
    app = App(
        system_prompt_path=args["system_prompt_path"],
        agent_name=args["agent_name"],
        provider_name=args["provider_name"],
        model_name=args["model_name"],
        rag_directory=args["rag_directory"],
    )
    app.run()
    app.join()


if __name__ == "__main__":
    main()
