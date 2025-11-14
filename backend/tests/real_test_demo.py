"""
Simple demo of real network request testing with Ollama.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.llm.llm_providers.ollama_provider import OllamaProvider


async def demo_real_test():
    """Demonstrate real network request testing."""
    print("=== Real Ollama Network Request Demo ===")
    print()

    # Create provider
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="qwen2.5:1.5b",
        temperature=0.1,
        max_tokens=100,
        timeout=30
    )

    try:
        print("Testing connection...")
        connection_ok = await provider.test_connection()
        if connection_ok:
            print("[SUCCESS] Connected to Ollama!")
        else:
            print("[FAILED] Cannot connect to Ollama")
            return

        print("\nTesting simple English generation...")
        response1 = await provider.generate_response(
            prompt="What is AI?",
            system_prompt="You are a helpful assistant. Give a brief answer."
        )

        if response1.is_successful:
            print(f"[SUCCESS] English response:")
            print(f"  Content: {response1.data.content}")
            print(f"  Tokens: {response1.metadata.total_tokens}")
            print(f"  Time: {response1.metadata.response_time_ms}ms")
        else:
            print(f"[FAILED] {response1.error.error_message}")

        print("\nTesting Chinese generation...")
        response2 = await provider.generate_response(
            prompt="请简单介绍一下机器学习",
            system_prompt="你是一个友好的AI助手。请用中文简短回答。"
        )

        if response2.is_successful:
            print(f"[SUCCESS] Chinese response:")
            print(f"  Content: {response2.data.content}")
            print(f"  Tokens: {response2.metadata.total_tokens}")
            print(f"  Time: {response2.metadata.response_time_ms}ms")
        else:
            print(f"[FAILED] {response2.error.error_message}")

        print("\nTesting statistics...")
        stats = provider.get_statistics()
        print(f"[INFO] Statistics:")
        print(f"  Requests: {stats['request_count']}")
        print(f"  Total tokens: {stats['total_tokens']}")
        print(f"  Total cost: ${stats['total_cost']:.6f}")

        # Cleanup
        await provider.close()
        print("\n[SUCCESS] Demo completed successfully!")

    except Exception as e:
        print(f"[ERROR] Demo failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(demo_real_test())