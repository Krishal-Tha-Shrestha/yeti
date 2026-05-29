import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai import chat

def main():
    print("=" * 40)
    print("  YETI - Personal AI Assistant")
    print("  Type 'quit' to exit")
    print("=" * 40)
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("Yeti: Goodbye Krishal!")
                break

            print("Yeti: ", end="", flush=True)
            response = chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\nYeti: Goodbye Krishal!")
            break
        except ConnectionError:
            print("Yeti: Lost connection. Check your internet and try again.")
        except TimeoutError:
            print("Yeti: Request timed out. Try again.")
        except Exception as e:
            print(f"Yeti: Something went wrong — {e}")
            print("Yeti: Try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()