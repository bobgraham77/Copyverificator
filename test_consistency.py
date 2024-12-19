import streamlit as st
from app import analyze_text
import time

def test_consistency():
    # Test text
    test_text = """
    Welcome to our revolutionary product that will transform your life!
    
    Our cutting-edge solution addresses all your needs with state-of-the-art technology.
    Don't miss out on this amazing opportunity to enhance your daily routine.
    
    Act now and receive an exclusive bonus package worth $500!
    Contact us today to learn more about how we can help you achieve your goals.
    """
    
    print("Running consistency test with the same text 3 times...")
    print("\nTest text:", test_text)
    
    # Run analysis 3 times
    for i in range(3):
        print(f"\nTest #{i+1}")
        print("-" * 50)
        start_time = time.time()
        result = analyze_text(test_text)
        end_time = time.time()
        print(f"Analysis completed in {end_time - start_time:.2f} seconds")
        print("\nResults:")
        print(result)
        print("-" * 50)
        time.sleep(2)  # Wait a bit between tests

if __name__ == "__main__":
    test_consistency()
