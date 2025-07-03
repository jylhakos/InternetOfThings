# Fine-tuning AI models

Hugging Face provides an ecosystem built on PyTorch for fine-tuning Large Language Models (LLMs) through its transformers and trl libraries. 

The primary tool for fine-tuning is the Trainer class from transformers or the SFTTrainer (Supervised Fine-Tuning Trainer) from trl.

## Example: Fine-tuning provided by Hugging Face

Install libraries: 

Install transformers, datasets, trl, and accelerate (for distributed training).

```

    $ pip install transformers datasets trl accelerate bitsandbytes

```
Load model and tokenizer

```

    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    import torch

    model_name = "meta-llama/Llama-2-7b-hf" # Or any other LLM

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=False,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )
    model.config.use_cache = False # Important for fine-tuning

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token # Or set a specific pad token

```
References

Amazon SageMaker

https://aws.amazon.com/sagemaker/

Fine-Tune Your First LLM

https://docs.pytorch.org/torchtune/0.1/tutorials/first_finetune_tutorial.html

Fine-tuning

https://huggingface.co/docs/transformers/en/training


