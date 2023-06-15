# arg parsing test:
import argparse

l = 2

def run(args) -> None:
    print(args)
    print("success")

def main() -> None:
    print("executed main")
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="command")
    run_parser = subparsers.add_parser("run")
    run_parser.set_defaults(func=run)

    args = parser.parse_args()
    print("parsed args")
    print(vars(args))
    args.func(args)

if __name__ == "__main__":
    main()