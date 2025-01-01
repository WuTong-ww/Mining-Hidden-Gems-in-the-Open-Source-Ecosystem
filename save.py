from transformers import GPT2LMHeadModel, GPT2Tokenizer

# 下载 GPT-2 模型和分词器
model_name = "gpt2"  # 可以选择 'gpt2-medium', 'gpt2-large', 'gpt2-xl'
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# 保存模型和分词器到本地
model.save_pretrained("./gpt2_model")
tokenizer.save_pretrained("./gpt2_model")

print("GPT-2 模型和分词器已成功保存！")
