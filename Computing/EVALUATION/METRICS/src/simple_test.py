print("Testing Python environment...")
try:
    import torch
    print(f"✅ PyTorch imported: {torch.__version__}")
    print(f"✅ CUDA available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"✅ GPU devices: {torch.cuda.device_count()}")
        print(f"✅ Device name: {torch.cuda.get_device_name(0)}")
    else:
        print("❌ CUDA not available")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("Test completed!")
