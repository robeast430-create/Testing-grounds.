from neural_agent import NeuralAgent
from neural_agent.api.api_server import APIServer
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Neural Agent")
    parser.add_argument("--port", type=int, default=8080, help="API server port (default: 8080)")
    parser.add_argument("--no-api", action="store_true", help="Disable API server")
    parser.add_argument("--config", type=str, default="config.json", help="Config file path")
    args = parser.parse_args()
    
    agent = NeuralAgent(config_file=args.config)
    
    if not args.no_api:
        api = APIServer(agent, port=args.port)
        api.start()
        agent.api = api
    
    try:
        agent.start()
    except KeyboardInterrupt:
        pass
    finally:
        if hasattr(agent, 'api'):
            agent.api.stop()

if __name__ == "__main__":
    main()